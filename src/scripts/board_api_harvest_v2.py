"""Harvest v2 — 2026-10-17: NEW org slugs discovered via dork round 2.
Writes 2026-10-17-harvest-pool-2.json (merged, deduped vs blocklist keys).
Run: uv run python src/scripts/board_api_harvest_v2.py
"""
import json
import re
import ssl
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from collections import Counter

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
WORK = Path(r"C:\Users\binit\AppData\Local\Temp\opencode")
BLFILE = WORK / "job_blocklist_raw.txt"
OUT = ROOT / "src" / "job_search_results" / "2026-10-17-harvest-pool-2.json"

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
CTX = ssl.create_default_context()

EXTRA_ORGS = {
    "lever": ["everbridge", "gohighlevel", "paytm", "oscilar", "savvymoney", "teamsnap",
              "shopback-2", "saviynt", "smart-working-solutions", "ion", "thinkahead", "greedygame"],
    "ashby": ["skylo", "notion", "opslevel", "qualified", "wonderly", "breadwinner", "immersivelabs", "tilthq", "oscilar",
              "cynlr", "lgads"],
    "greenhouse": ["singlestore", "bitgo", "platformscience", "nirmata", "commerceiq", "anaplan", "gupshup", "zetwerk",
                   "cloudsek", "coherehealth", "redwoodsoftware", "jumio", "greedygame", "okta",
                   "easyship", "tegnaindia", "thetradedesk"],
}

INDIA = ["india", "bengaluru", "bangalore", "hyderabad", "pune", "mumbai", "gurgaon",
         "gurugram", "noida", "chennai", "delhi", "kolkata", "ahmedabad", "jaipur",
         "indore", "nagpur", "kochi", "vadodara", "surat", "chandigarh", "mysore"]
BLOCK_GEO = ["united states", "u.s.", "(us)", "us only", "north america", "canada",
             "europe", "emea", "london", "berlin", "france", "singapore", "australia",
             "new york", "san francisco", "toronto", "ontario", "sweden", "netherlands",
             "(uk)", "britain", "spain", "italy", "poland", "mexico", "brazil", "dubai",
             "uae", "indonesia", "philippines", "nigeria", "kenya", "ukraine"]

EXCL_WORDS = re.compile(
    r"\b(senior|principal|staff|lead|manager|director|head|architect|president|vp|"
    r"frontend|front-end|front end|qa|quality|recruiting|sales|marketing|growth|"
    r"customer|business|financial|legal|design|supply|clinical|revenue|operations)\b", re.I)
LEVEL_TAIL = re.compile(r"(engineer|developer|scientist|sde|analyst)\s*[-(]?\s*(ii|iii|2|3)\b", re.I)
REQ_WORDS = re.compile(
    r"\b(software|developer|engineer|sde|machine learning|\bml\b|\bai\b|llm|genai|generative|"
    r"data|nlp|intern|trainee|graduate|applied|research|devops|sre)\b", re.I)


def loc_verdict(location: str):
    if not location:
        return None
    l = location.lower()
    if any(t in l for t in INDIA):
        return "india"
    if any(b in l for b in BLOCK_GEO):
        return None
    if "remote" in l or "apac" in l or "worldwide" in l or "global" in l or "anywhere" in l:
        return "remote"
    return None


def title_verdict(title: str):
    if not title:
        return None
    if EXCL_WORDS.search(title) or LEVEL_TAIL.search(title):
        return None
    if not REQ_WORDS.search(title):
        return None
    return True


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=15, context=CTX) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def norm_key(platform, org, ident):
    return f"{platform}:{org.lower()}:{str(ident).lower()}"


def harvest_org(platform, org):
    out = {}
    try:
        if platform == "lever":
            for j in fetch(f"https://api.lever.co/v0/postings/{org}?mode=json") or []:
                if not isinstance(j, dict):
                    continue
                cat = j.get("categories") or {}
                out[norm_key(platform, org, j.get("id"))] = {
                    "platform": platform, "org": org,
                    "title": j.get("text"),
                    "location": cat.get("location"),
                    "commitment": cat.get("commitment"),
                    "url": j.get("hostedUrl") or f"https://jobs.lever.co/{org}/{j.get('id')}",
                    "updated": (j.get("createdAt") and time.strftime("%Y-%m-%d", time.gmtime(j["createdAt"] / 1000))) or "",
                }
        elif platform == "ashby":
            data = fetch(f"https://api.ashbyhq.com/posting-api/job-board/{org}")
            for j in data.get("jobs", []) or []:
                out[norm_key(platform, org, j.get("id"))] = {
                    "platform": platform, "org": org,
                    "title": j.get("title"), "location": j.get("location"),
                    "commitment": None,
                    "url": f"https://jobs.ashbyhq.com/{org}/{j.get('id')}",
                    "id": j.get("id"),
                    "updated": (j.get("updatedAt") or "")[:10],
                }
        elif platform == "greenhouse":
            data = fetch(f"https://boards-api.greenhouse.io/v1/boards/{org}/jobs")
            for j in data.get("jobs", []) or []:
                loc = (j.get("location") or {}).get("name") if isinstance(j.get("location"), dict) else j.get("location")
                out[norm_key(platform, org, j.get("id"))] = {
                    "platform": platform, "org": org,
                    "title": j.get("title"), "location": loc,
                    "commitment": None,
                    "url": j.get("absolute_url") or f"https://job-boards.greenhouse.io/{org}/jobs/{j.get('id')}",
                    "id": j.get("id"),
                    "updated": j.get("updated_at"),
                }
    except urllib.error.HTTPError as e:
        print(f"  [{platform}:{org}] HTTP {e.code}", flush=True)
    except Exception as e:
        print(f"  [{platform}:{org}] ERR {type(e).__name__}: {e}", flush=True)
    return out


def main():
    all_jobs = {}
    tasks = [(p, o) for p, ol in EXTRA_ORGS.items() for o in ol]
    print(f"HARVEST TASKS: {len(tasks)}", flush=True)
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(harvest_org, p, o): (p, o) for p, o in tasks}
        for f in as_completed(futs):
            for k, v in f.result().items():
                all_jobs[k] = v
    print(f"TOTAL JOB NUGGETS: {len(all_jobs)}", flush=True)

    known_keys = set()
    if BLFILE.exists():
        for line in BLFILE.read_text(encoding="utf-8", errors="replace").splitlines():
            l = line.rstrip().strip('/')
            if m := re.search(r"(?:jobs\.)?lever\.co/([A-Za-z0-9_.-]+)/([a-f0-9-]{8,})", l, re.I):
                known_keys.add(norm_key("lever", m.group(1), m.group(2)))
            if m := re.search(r"ashbyhq\.com/([A-Za-z0-9_.-]+)/([a-f0-9-]{8,})", l, re.I):
                known_keys.add(norm_key("ashby", m.group(1), m.group(2)))
            if m := re.search(r"greenhouse\.io/([A-Za-z0-9_-]+)/jobs/(\d+)", l, re.I):
                known_keys.add(norm_key("greenhouse", m.group(1), m.group(2)))

    pool = []
    for k, j in all_jobs.items():
        tk = title_verdict(j.get("title") or "")
        lv = loc_verdict(j.get("location") or "")
        if tk and lv and k not in known_keys:
            j["geo_tag"] = lv
            j["key"] = k
            pool.append(j)

    pool.sort(key=lambda x: (x["platform"], x["org"], (x["title"] or "").lower()))
    OUT.write_text(json.dumps({"date": "2026-10-17", "count": len(pool), "jobs": pool},
                              indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"POOL-2 (filtered+fresh): {len(pool)}  -> {OUT}", flush=True)
    print("BY PLATFORM:", dict(Counter(p["platform"] for p in pool)), flush=True)


if __name__ == "__main__":
    main()
