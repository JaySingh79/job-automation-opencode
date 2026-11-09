"""
harvest_fresh_monthly_ats.py — Search & harvest 100 Ashby, 100 Lever, 100 Greenhouse jobs
strictly posted/updated within the past month (>= 2026-10-01, <= 37 days old).
Combines Firecrawl search sweeps with live board API timestamp verification.
"""
import os
import json
import re
import ssl
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from collections import Counter, defaultdict
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
OUT_DIR = ROOT / "src" / "job_search_results" / "ashby_lever_greenhouse"
OUT_COMBINED = OUT_DIR / "2026-11-07-fresh-300-ashby-lever-greenhouse.json"
OUT_ASHBY = OUT_DIR / "2026-11-07-ashby-100.json"
OUT_LEVER = OUT_DIR / "2026-11-07-lever-100.json"
OUT_GH = OUT_DIR / "2026-11-07-greenhouse-100.json"

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
FIRECRAWL_KEY = os.getenv("FIRECRAWL_API_KEY")

OCT_1_2026 = datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp()

# Helper imports from previous robust module
import sys
sys.path.append(r"D:\Projects\PRACTICE\firecrawl_test\src\scripts")
from harvest_fresh_300_ats import (
    classify_location, classify_title, load_applied_set, fetch_json
)

# ------------------- 1. FIRECRAWL SEARCH SWEEPS -------------------
def firecrawl_search_batch(queries, limit_per_query=20):
    discovered_urls = defaultdict(set) # platform -> set of urls
    discovered_orgs = defaultdict(set) # platform -> set of orgs

    def search_one(q):
        url = "https://api.firecrawl.dev/v1/search"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {FIRECRAWL_KEY}"
        }
        payload = {
            "query": q,
            "limit": limit_per_query,
            "scrapeOptions": {"formats": ["markdown"]}
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("data", [])
        except Exception as e:
            print(f"  [Firecrawl Err] '{q[:40]}...': {e}", flush=True)
            return []

    print(f"Launching {len(queries)} Firecrawl search queries in parallel...", flush=True)
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(search_one, q): q for q in queries}
        for f in as_completed(futs):
            items = f.result()
            for it in items:
                u = it.get("url") or ""
                # Lever match
                if m := re.search(r"https?://(?:jobs\.)?lever\.co/([A-Za-z0-9_.-]+)(?:/([a-f0-9-]{8,}))?", u, re.I):
                    org = m.group(1).lower().strip("/")
                    if org not in ("v0", "search", "apply", "postings", "jobtwine"):
                        discovered_orgs["lever"].add(org)
                    if m.group(2):
                        discovered_urls["lever"].add((org, u, it.get("title") or ""))
                # Ashby match
                elif m := re.search(r"https?://jobs\.ashbyhq\.com/([A-Za-z0-9_.-]+)(?:/([a-f0-9-]{8,}))?", u, re.I):
                    org = m.group(1).lower().strip("/")
                    if org not in ("api", "posting-api", "job-board"):
                        discovered_orgs["ashby"].add(org)
                    if m.group(2):
                        discovered_urls["ashby"].add((org, u, it.get("title") or ""))
                # Greenhouse match
                elif m := re.search(r"https?://(?:job-boards\.|boards\.)?greenhouse\.io/([A-Za-z0-9_-]+)(?:/jobs/(\d+))?", u, re.I):
                    org = m.group(1).lower().strip("/")
                    if org not in ("v1", "boards", "embed", "api", "jobs"):
                        discovered_orgs["greenhouse"].add(org)
                    if m.group(2):
                        discovered_urls["greenhouse"].add((org, u, it.get("title") or ""))

    print(f"Firecrawl sweep summary:", flush=True)
    for p in ["ashby", "lever", "greenhouse"]:
        print(f"  {p.upper()}: {len(discovered_orgs[p])} orgs discovered, {len(discovered_urls[p])} direct URLs", flush=True)
    return discovered_orgs, discovered_urls

# ------------------- 2. BOARD API FETCH WITH TIMESTAMP GATE -------------------
def fetch_lever_fresh(org, applied_set):
    jobs = []
    try:
        data = fetch_json(f"https://api.lever.co/v0/postings/{org}?mode=json")
        for j in (data or []):
            if not isinstance(j, dict): continue
            ca = j.get("createdAt")
            if not ca or (ca / 1000.0) < OCT_1_2026:
                continue
            title = j.get("text") or ""
            t_clean, cat_role = classify_title(title)
            if not t_clean: continue
            cat = j.get("categories") or {}
            loc = cat.get("location") or ""
            geo = classify_location(loc)
            if not geo: continue
            u = j.get("hostedUrl") or f"https://jobs.lever.co/{org}/{j.get('id')}"
            if u.strip().lower().rstrip("/") in applied_set: continue
            post_date = datetime.fromtimestamp(ca / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")
            jobs.append({
                "platform": "lever", "org": org, "title": t_clean, "category": cat_role,
                "location": loc, "geo": geo, "url": u, "posted_date": post_date, "created_at": ca,
                "work_type": cat.get("commitment") or "Full-time"
            })
    except Exception:
        pass
    return jobs

def fetch_ashby_fresh(org, applied_set):
    jobs = []
    try:
        data = fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true")
        for j in (data.get("jobs") or []):
            pub = j.get("publishedAt")
            if not pub: continue
            try:
                dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                if dt.timestamp() < OCT_1_2026: continue
                post_date = dt.strftime("%Y-%m-%d")
            except Exception:
                continue
            title = j.get("title") or ""
            t_clean, cat_role = classify_title(title)
            if not t_clean: continue
            loc = j.get("location") or ""
            all_locs = [loc] + [sec.get("location") or "" for sec in (j.get("secondaryLocations") or [])]
            geo = None
            for l_cand in all_locs:
                geo = classify_location(l_cand)
                if geo:
                    loc = l_cand
                    break
            if not geo: continue
            ident = j.get("id")
            u = f"https://jobs.ashbyhq.com/{org}/{ident}"
            if u.strip().lower().rstrip("/") in applied_set: continue
            jobs.append({
                "platform": "ashby", "org": org, "title": t_clean, "category": cat_role,
                "location": loc, "geo": geo, "url": u, "posted_date": post_date, "published_at": pub,
                "work_type": j.get("employmentType") or "Full-time"
            })
    except Exception:
        pass
    return jobs

def fetch_gh_fresh(org, applied_set):
    jobs = []
    try:
        data = fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{org}/jobs")
        for j in (data.get("jobs") or []):
            up = j.get("updated_at")
            if not up: continue
            try:
                dt = datetime.fromisoformat(up.replace("Z", "+00:00"))
                if dt.timestamp() < OCT_1_2026: continue
                post_date = dt.strftime("%Y-%m-%d")
            except Exception:
                continue
            title = j.get("title") or ""
            t_clean, cat_role = classify_title(title)
            if not t_clean: continue
            loc_obj = j.get("location")
            loc = loc_obj.get("name") if isinstance(loc_obj, dict) else (loc_obj or "")
            geo = classify_location(loc)
            if not geo: continue
            ident = str(j.get("id"))
            u = j.get("absolute_url") or f"https://job-boards.greenhouse.io/{org}/jobs/{ident}"
            if u.strip().lower().rstrip("/") in applied_set: continue
            jobs.append({
                "platform": "greenhouse", "org": org, "title": t_clean, "category": cat_role,
                "location": loc, "geo": geo, "url": u, "posted_date": post_date, "updated_at": up,
                "work_type": "Full-time"
            })
    except Exception:
        pass
    return jobs

# ------------------- 3. URL LIVENESS VERIFICATION -------------------
def verify_url_live(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=8, context=CTX) as r:
            return r.status in (200, 301, 302)
    except urllib.error.HTTPError as e:
        if e.code in (404, 410, 403):
            return False
        return True # Some boards block bot head requests with 401/429
    except Exception:
        return True # Network transient error, don't discard blindly

# ------------------- MAIN HARVESTER -------------------
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    applied_set = load_applied_set()
    print(f"Loaded {len(applied_set)} previously applied/attempted URLs for exclusion.", flush=True)

    # 1. Broad freshness search queries for Firecrawl
    queries = [
        # Ashby
        'site:jobs.ashbyhq.com ("India" OR "Remote") ("Machine Learning" OR "AI Engineer" OR "Python") -senior after:2026-10-01',
        'site:jobs.ashbyhq.com ("India" OR "Remote") ("Software Engineer" OR "Backend Developer" OR "Fullstack") -senior after:2026-10-01',
        'site:jobs.ashbyhq.com ("India" OR "Bengaluru" OR "Bangalore") ("Developer" OR "Engineer" OR "Data") -senior after:2026-10-01',
        'site:jobs.ashbyhq.com ("Remote" OR "Worldwide") ("Machine Learning" OR "LLM" OR "AI" OR "Python") -senior after:2026-10-01',
        'site:jobs.ashbyhq.com ("Intern" OR "Associate" OR "Junior" OR "Graduate" OR "Fresher") ("AI" OR "ML" OR "Software") after:2026-10-01',
        # Lever
        'site:jobs.lever.co ("India" OR "Remote") ("Machine Learning" OR "AI Engineer" OR "Python") -senior after:2026-10-01',
        'site:jobs.lever.co ("India" OR "Remote") ("Software Engineer" OR "Backend Developer" OR "Fullstack") -senior after:2026-10-01',
        'site:jobs.lever.co ("India" OR "Bengaluru" OR "Bangalore" OR "Hyderabad") ("Developer" OR "Engineer" OR "Data") -senior after:2026-10-01',
        'site:jobs.lever.co ("Remote" OR "Worldwide") ("Machine Learning" OR "LLM" OR "AI" OR "Python") -senior after:2026-10-01',
        'site:jobs.lever.co ("Intern" OR "Associate" OR "Junior" OR "Graduate" OR "Fresher") ("AI" OR "ML" OR "Software") after:2026-10-01',
        # Greenhouse
        'site:job-boards.greenhouse.io OR site:boards.greenhouse.io ("India" OR "Remote") ("Machine Learning" OR "AI Engineer" OR "Python") -senior after:2026-10-01',
        'site:job-boards.greenhouse.io OR site:boards.greenhouse.io ("India" OR "Remote") ("Software Engineer" OR "Backend Developer" OR "Fullstack") -senior after:2026-10-01',
        'site:job-boards.greenhouse.io OR site:boards.greenhouse.io ("India" OR "Bengaluru" OR "Bangalore" OR "Hyderabad") ("Developer" OR "Data") -senior after:2026-10-01',
        'site:job-boards.greenhouse.io OR site:boards.greenhouse.io ("Remote" OR "Worldwide") ("Machine Learning" OR "AI" OR "Python") -senior after:2026-10-01',
        'site:job-boards.greenhouse.io OR site:boards.greenhouse.io ("Intern" OR "Associate" OR "Junior" OR "Graduate" OR "Fresher") ("AI" OR "ML" OR "Software") after:2026-10-01'
    ]

    discovered_orgs, direct_results = firecrawl_search_batch(queries, limit_per_query=25)

    # 2. Build full org pools
    lever_orgs = set(discovered_orgs["lever"])
    ashby_orgs = set(discovered_orgs["ashby"])
    gh_orgs = set(discovered_orgs["greenhouse"])

    # Include known active orgs
    known_lever = [
        "binance", "brillio-2", "coupa", "drivetrain", "enablecomp", "equativ",
        "everbridge", "ewor", "farfetch", "galepartners", "gohighlevel", "hevodata",
        "lingarogroup", "merklescience", "offchainlabs", "outcomesai", "paytm",
        "policyme", "portcast", "porter", "saviynt", "shopback-2", "shyftlabs",
        "smart-working-solutions", "supermove", "teamsnap", "trackmind", "veeva",
        "weekdayworks", "zimperium", "cars24", "spinny", "apna", "sharechat",
        "glance", "coindcx", "mpl", "dream11", "clevertap", "weloglobal", "tsmg", "jobgether",
        "policyme", "vida", "theathletic", "muttdata", "supermove", "vimeo", "spotify"
    ]
    for o in known_lever: lever_orgs.add(o)

    known_ashby = [
        "abridge", "aiprise", "baseten", "brainco", "cartesia", "clerk", "cognition",
        "cohere", "cursor", "cynlr", "elevenlabs", "emergence", "fal-ai", "gecko-robotics",
        "hex", "jerry.ai", "lgads", "linear", "magic", "mistral.ai", "modal", "notion",
        "opslevel", "perplexity", "pika", "pinecone", "poolside", "posthog", "quora",
        "reka", "resend", "runway", "sarvam", "sierra", "sift", "skylo", "suno",
        "tessera-labs", "tolken", "warp", "weaviate", "hirehangar", "playpowerlabs",
        "careway", "korza", "ande", "duna", "espa", "yotta", "simular", "realmalliance",
        "gptzero", "meraki-labs", "bio", "aiprojects", "bjakcareer", "spector-ai",
        "gradera", "interview-kickstart", "ahl-saafai", "buildai", "ema", "mastra",
        "sandboxaq", "mimolabs", "handshake", "mapbox", "sycamore", "clickhouse",
        "retool", "posthog", "cal.com", "raycast", "dub", "superhuman", "glean"
    ]
    for o in known_ashby: ashby_orgs.add(o)

    known_gh = [
        "affirm", "anthropic", "brex", "carta", "checkr", "chime", "cloudflare",
        "coinbase", "databricks", "datadog", "elastic", "figma", "fireblocks", "fivetran",
        "gemini", "gitlab", "groww", "gusto", "hackerrank", "honeycomb", "inmobi",
        "lattice", "launchdarkly", "mercury", "mongodb", "monzo", "n26", "neo4j",
        "newrelic", "pagerduty", "ramp", "remote", "robinhood", "rubrik", "scaleai",
        "stripe", "togetherai", "vercel", "turing", "enterpret", "rzr", "anteriad",
        "doordashindia", "dscout", "lynxanalytics", "interviewkickstart", "singlestore",
        "bitgo", "platformscience", "nirmata", "commerceiq", "anaplan", "gupshup",
        "zetwerk", "cloudsek", "coherehealth", "redwoodsoftware", "jumio", "greedygame",
        "easyship", "tegnaindia", "thetradedesk", "browserstack", "hasura", "urbancompany",
        "skildai-careers", "postman", "okta", "deliveroo", "zetaglobal", "instacart",
        "thoughtworks", "yugabyte", "gravitonresearchcapital", "gleanwork", "samsara", "asg"
    ]
    for o in known_gh: gh_orgs.add(o)

    print(f"\nTotal org pools to query: Lever={len(lever_orgs)}, Ashby={len(ashby_orgs)}, Greenhouse={len(gh_orgs)}", flush=True)

    # 3. Query all board APIs in parallel for postings with timestamp >= 2026-10-01
    lever_jobs = []
    ashby_jobs = []
    gh_jobs = []

    with ThreadPoolExecutor(max_workers=30) as ex:
        futs_l = {ex.submit(fetch_lever_fresh, o, applied_set): o for o in lever_orgs}
        futs_a = {ex.submit(fetch_ashby_fresh, o, applied_set): o for o in ashby_orgs}
        futs_g = {ex.submit(fetch_gh_fresh, o, applied_set): o for o in gh_orgs}

        for f in as_completed(futs_l):
            lever_jobs.extend(f.result())
        for f in as_completed(futs_a):
            ashby_jobs.extend(f.result())
        for f in as_completed(futs_g):
            gh_jobs.extend(f.result())

    # 4. Integrate direct results from search that pass filters
    print(f"Board API fresh jobs harvested: Lever={len(lever_jobs)}, Ashby={len(ashby_jobs)}, Greenhouse={len(gh_jobs)}", flush=True)

    # Dedup helper
    def dedup_jobs(jobs):
        seen = set()
        deduped = []
        for j in jobs:
            u_norm = j["url"].strip().lower().rstrip("/")
            if u_norm not in seen and u_norm not in applied_set:
                seen.add(u_norm)
                deduped.append(j)
        return deduped

    lever_clean = dedup_jobs(lever_jobs)
    ashby_clean = dedup_jobs(ashby_jobs)
    gh_clean = dedup_jobs(gh_jobs)

    print(f"Deduplicated fresh jobs (posted >= 2026-10-01):", flush=True)
    print(f"  Lever: {len(lever_clean)}", flush=True)
    print(f"  Ashby: {len(ashby_clean)}", flush=True)
    print(f"  Greenhouse: {len(gh_clean)}", flush=True)

    # If any board is under 100, sort all unapplied jobs by date descending so the most recent ones come first
    # and strictly pick the top 100 most recent for each
    def sort_by_recency_and_fit(j):
        score = 0
        # Post date score (e.g. 2026-11-05 = very high)
        pd = j.get("posted_date", "2026-10-01")
        try:
            # Days since 2026-10-01
            dt = datetime.strptime(pd, "%Y-%m-%d")
            score += (dt.timestamp() - OCT_1_2026) / 86400.0 * 2.0
        except Exception:
            pass

        cat = j.get("category", "")
        if cat in ("GenAI_LLM", "ML_Vision", "Machine_Learning"):
            score += 30
        elif cat == "Data_Science":
            score += 20
        elif cat == "SDE_Backend":
            score += 10

        if j.get("geo") == "India":
            score += 15
        elif j.get("geo") == "Remote":
            score += 10

        t_lower = j.get("title", "").lower()
        if any(w in t_lower for w in ["intern", "trainee", "fresher", "junior", "associate", "entry", "sde 1", "sde-1", "sde i"]):
            score += 10

        return score

    lever_clean.sort(key=sort_by_recency_and_fit, reverse=True)
    ashby_clean.sort(key=sort_by_recency_and_fit, reverse=True)
    gh_clean.sort(key=sort_by_recency_and_fit, reverse=True)

    # Let's check counts
    print(f"Current filtered counts: Lever={len(lever_clean)}, Ashby={len(ashby_clean)}, Greenhouse={len(gh_clean)}", flush=True)

    # Save checkpoint datasets
    with open(OUT_DIR / "temp_fresh_lever.json", "w", encoding="utf-8") as f:
        json.dump(lever_clean, f, indent=2)
    with open(OUT_DIR / "temp_fresh_ashby.json", "w", encoding="utf-8") as f:
        json.dump(ashby_clean, f, indent=2)
    with open(OUT_DIR / "temp_fresh_gh.json", "w", encoding="utf-8") as f:
        json.dump(gh_clean, f, indent=2)

if __name__ == "__main__":
    main()
