"""
board_api_harvest.py — 2026-10-17 heavy-fiber job discovery for Ashby/Lever/Greenhouse.
Reads blocklist of already-known job URLs (raw list file), extracts org slugs,
fetches each org's public board JSON API, filters to fresher/entry AI/ML/Backend/Full-stack/Data
roles in India or India-eligible remote, dedupes by (org,id) key, writes pool JSON.
Run: uv run python src/scripts/board_api_harvest.py
"""

import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
WORK = Path(r"C:\Users\binit\AppData\Local\Temp\opencode")
BLFILE = WORK / "job_blocklist_raw.txt"
OUT = ROOT / "src" / "job_search_results" / "2026-10-17-harvest-pool.json"

START = time.time()
CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}

# ---------------- org slug extraction from blocklist ----------------
LEVER_RE = re.compile(r"(?:jobs\.)?lever\.co/([A-Za-z0-9_.-]+)", re.I)
ASHBY_RE = re.compile(r"ashbyhq\.com/([A-Za-z0-9_.-]+)", re.I)
GH_RE = re.compile(r"greenhouse\.io/([A-Za-z0-9_-]+)/", re.I)

MANUAL_ORGS = {
    "lever": ["portcast", "drivetrain", "hevodata", "jobtwine", "enablecomp", "brillio-2",
              "offchainlabs", "jobgether", "boardintelligence", "farfetch", "equativ", "ewor",
              "policyme", "shyftlabs", "trackmind", "galepartners", "weekdayworks",
              "merklescience", "epifi", "lingarogroup", "zimperium", "outcomesai", "sprinto",
              "veeva", "binance", "gotoGroup".lower()],
    "ashby": ["hirehangar", "jerry.ai", "riveron", "ande", "duna", "brainco", "janea-systems",
              "espa", "yotta", "simular", "realmalliance", "cohere", "quora", "hex",
              "gecko-robotics", "tessera-labs", "sift", "fal-ai", "cartesia", "mistral.ai",
              "abridge", "gptzero", "emergence", "playpowerlabs", "careway", "aiprise",
              "tolken", "meraki-labs", "openai", "bio", "korza", "aiprojects"],
    "greenhouse": ["turing", "enterpret", "rzr", "anteriad", "doordashindia", "dscout",
                   "lynxanalytics", "interviewkickstart", "rubrik", "databricks"],
}

# ---------------- text filters ----------------
INDIA = ["india", "bengaluru", "bangalore", "hyderabad", "pune", "mumbai", "gurgaon",
         "gurugram", "noida", "chennai", "delhi", "kolkata", "ahmedabad", "jaipur",
         "indore", "nagpur", "kochi", "vadodara", "surat", "chandigarh", "mysore"]
BLOCK_GEO = ["united states", "u.s.", "(us)", "us only", "north america", "canada",
             "europe", "emea", "london", "berlin", "france", "singapore", "australia",
             "new york", "san francisco", "toronto", "ontario", "sweden", "netherlands",
             "(uk)", "britain", "spain", "italy", "poland", "mexico", "brazil", "dubai",
             "uae", "indonesia", "philippines", "nigeria", "kenya", "ukraine"]


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


EXCL_WORDS = re.compile(
    r"\b(senior|principal|staff|lead|manager|director|head|architect|president|vp|"
    r"frontend|front-end|front end|qa|quality|recruiting|sales|marketing|growth|"
    r"customer|business|financial|legal|design|supply|clinical|revenue|operations)\b", re.I)
LEVEL_TAIL = re.compile(r"(engineer|developer|scientist|sde|analyst)\s*[-(]?\s*(ii|iii|2|3)\b", re.I)
REQ_WORDS = re.compile(
    r"\b(software|developer|engineer|sde|machine learning|\bml\b|\bai\b|llm|genai|generative|"
    r"data|nlp|intern|trainee|graduate|applied|research|devops|sre)\b", re.I)


def title_verdict(title: str):
    if not title:
        return None
    t = title
    if EXCL_WORDS.search(t) or LEVEL_TAIL.search(t):
        return None
    if not REQ_WORDS.search(t):
        return None
    return True


# ---------------- fetching ----------------
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
            data = fetch(f"https://api.lever.co/v0/postings/{org}?mode=json")
            for j in data or []:
                if not isinstance(j, dict):
                    continue
                ident = j.get("id")
                cat = j.get("categories") or {}
                out[norm_key(platform, org, ident)] = {
                    "platform": platform, "org": org,
                    "title": j.get("text"),
                    "location": cat.get("location"),
                    "commitment": cat.get("commitment"),
                    "url": j.get("hostedUrl") or f"https://jobs.lever.co/{org}/{ident}",
                }
        elif platform == "ashby":
            data = fetch(f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true")
            for j in data.get("jobs", []) or []:
                ident = j.get("id")
                out[norm_key(platform, org, ident)] = {
                    "platform": platform, "org": org,
                    "title": j.get("title"),
                    "location": j.get("location"),
                    "commitment": None,
                    "url": f"https://jobs.ashbyhq.com/{org}/{ident}",
                    "id": ident,
                }
        elif platform == "greenhouse":
            data = fetch(f"https://boards-api.greenhouse.io/v1/boards/{org}/jobs")
            for j in data.get("jobs", []) or []:
                ident = j.get("id")
                loc = (j.get("location") or {}).get("name") if isinstance(j.get("location"), dict) else j.get("location")
                out[norm_key(platform, org, ident)] = {
                    "platform": platform, "org": org,
                    "title": j.get("title"),
                    "location": loc,
                    "commitment": None,
                    "url": j.get("absolute_url") or f"https://job-boards.greenhouse.io/{org}/jobs/{ident}",
                    "id": ident,
                    "updated": j.get("updated_at"),
                }
    except urllib.error.HTTPError as e:
        print(f"  [{platform}:{org}] HTTP {e.code}", flush=True)
    except Exception as e:
        print(f"  [{platform}:{org}] ERR {type(e).__name__}: {e}", flush=True)
    return out


def main():
    # ---- collect org slugs from blocklist + manual
    padr, mastr, ghr = set(MANUAL_ORGS["lever"]), set(MANUAL_ORGS["ashby"]), set(MANUAL_ORGS["greenhouse"])
    if BLFILE.exists():
        for line in BLFILE.read_text(encoding="utf-8", errors="replace").splitlines():
            if m := LEVER_RE.search(line): padr.add(m.group(1))
            if m := ASHBY_RE.search(line): mastr.add(m.group(1))
            if m := GH_RE.search(line): ghr.add(m.group(1))
    # ashby slug cleanup: shared-page slugs like /openai/bf036... fine

    orgs = {"lever": sorted(padr), "ashby": sorted(mastr), "greenhouse": sorted(ghr)}
    print("ORG COUNTS:", {k: len(v) for k, v in orgs.items()}, flush=True)

    # ---- harvest all
    all_jobs = {}
    tasks = [(p, o) for p, ol in orgs.items() for o in ol if o not in (".mcp.json",)]
    print(f"HARVEST TASKS: {len(tasks)}", flush=True)
    with ThreadPoolExecutor(max_workers=14) as ex:
        futs = {ex.submit(harvest_org, p, o): (p, o) for p, o in tasks}
        for f in as_completed(futs):
            for k, v in f.result().items():
                all_jobs[k] = v
    print(f"TOTAL JOB NUGGETS: {len(all_jobs)}", flush=True)

    # ---- blocklist keys for dedup
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
    print(f"POOL (filtered+fresh): {len(pool)}  -> {OUT}", flush=True)
    from collections import Counter
    print("BY PLATFORM:", dict(Counter(p['platform'] for p in pool)), flush=True)


if __name__ == "__main__":
    main()
