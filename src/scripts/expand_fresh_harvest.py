"""
expand_fresh_harvest.py — Expand Ashby and Lever fresh harvest (>= 2026-10-01) to 100 each.
Paced Firecrawl search + board API timestamp verification.
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
from collections import Counter
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
OUT_DIR = ROOT / "src" / "job_search_results" / "ashby_lever_greenhouse"

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
FIRECRAWL_KEY = os.getenv("FIRECRAWL_API_KEY")
OCT_1_2026 = datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp()

import sys
sys.path.append(r"D:\Projects\PRACTICE\firecrawl_test\src\scripts")
from harvest_fresh_300_ats import (
    classify_location, classify_title, load_applied_set, fetch_json
)
from harvest_fresh_monthly_ats import fetch_lever_fresh, fetch_ashby_fresh

# Paced Firecrawl search
def firecrawl_search_one(query, limit=25):
    url = "https://api.firecrawl.dev/v1/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIRECRAWL_KEY}"
    }
    payload = {
        "query": query,
        "limit": limit,
        "scrapeOptions": {"formats": ["markdown"]}
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("data", [])
    except urllib.error.HTTPError as e:
        print(f"  [HTTP {e.code}] for query: {query[:45]}...", flush=True)
        if e.code == 429:
            time.sleep(5)
    except Exception as e:
        print(f"  [Err] {e} for query: {query[:45]}...", flush=True)
    return []

def main():
    applied_set = load_applied_set()
    print(f"Loaded {len(applied_set)} applied/attempted URLs for exclusion.")

    # Load existing temp files
    existing_ashby = json.loads((OUT_DIR / "temp_fresh_ashby.json").read_text(encoding="utf-8"))
    existing_lever = json.loads((OUT_DIR / "temp_fresh_lever.json").read_text(encoding="utf-8"))
    existing_gh = json.loads((OUT_DIR / "temp_fresh_gh.json").read_text(encoding="utf-8"))

    print(f"Starting with:")
    print(f"  Ashby:      {len(existing_ashby)} / 100")
    print(f"  Lever:      {len(existing_lever)} / 100")
    print(f"  Greenhouse: {len(existing_gh)} / 100")

    seen_ashby_urls = {j["url"].strip().lower().rstrip("/") for j in existing_ashby}
    seen_lever_urls = {j["url"].strip().lower().rstrip("/") for j in existing_lever}

    ashby_queries = [
        'site:jobs.ashbyhq.com "India" (engineer OR developer OR python OR data) after:2026-10-01',
        'site:jobs.ashbyhq.com ("Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Pune") after:2026-10-01',
        'site:jobs.ashbyhq.com "Remote" ("Machine Learning" OR "AI Engineer" OR "Python") after:2026-10-01',
        'site:jobs.ashbyhq.com "Remote" ("Software Engineer" OR "Backend" OR "Fullstack") after:2026-10-01',
        'site:jobs.ashbyhq.com ("Data Scientist" OR "Data Engineer" OR "AI") ("India" OR "Remote") after:2026-10-01',
        'site:jobs.ashbyhq.com ("LLM" OR "GenAI" OR "Agentic" OR "NLP") after:2026-10-01',
        'site:jobs.ashbyhq.com ("Intern" OR "Associate" OR "Graduate" OR "Junior") after:2026-10-01',
        'site:jobs.ashbyhq.com ("Computer Vision" OR "Robotics" OR "Applied Scientist") after:2026-10-01',
        'site:jobs.ashbyhq.com/ "India" after:2026-10-01',
        'site:jobs.ashbyhq.com/ "Remote" ("developer" OR "engineer") after:2026-10-01'
    ]

    lever_queries = [
        'site:jobs.lever.co "India" (engineer OR developer OR python OR data) after:2026-10-01',
        'site:jobs.lever.co ("Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Pune") after:2026-10-01',
        'site:jobs.lever.co "Remote" ("Machine Learning" OR "AI Engineer" OR "Python") after:2026-10-01',
        'site:jobs.lever.co "Remote" ("Software Engineer" OR "Backend" OR "Fullstack") after:2026-10-01',
        'site:jobs.lever.co ("Data Scientist" OR "Data Engineer" OR "AI") ("India" OR "Remote") after:2026-10-01',
        'site:jobs.lever.co ("LLM" OR "GenAI" OR "Agentic" OR "NLP") after:2026-10-01',
        'site:jobs.lever.co ("Intern" OR "Associate" OR "Graduate" OR "Junior") after:2026-10-01',
        'site:jobs.lever.co ("Computer Vision" OR "Robotics" OR "Applied Scientist") after:2026-10-01',
        'site:jobs.lever.co/ "India" after:2026-10-01',
        'site:jobs.lever.co/ "Remote" ("developer" OR "engineer") after:2026-10-01'
    ]

    new_ashby_orgs = set()
    new_lever_orgs = set()
    direct_candidates = []

    print("\n--- Running Paced Firecrawl Searches for Ashby ---")
    for q in ashby_queries:
        print(f"Searching: {q[:55]}...", flush=True)
        items = firecrawl_search_one(q, limit=25)
        for it in items:
            u = it.get("url") or ""
            if m := re.search(r"https?://jobs\.ashbyhq\.com/([A-Za-z0-9_.-]+)", u, re.I):
                org = m.group(1).lower().strip("/")
                if org not in ("api", "posting-api", "job-board"):
                    new_ashby_orgs.add(org)
                # If direct job link
                if m_id := re.search(r"https?://jobs\.ashbyhq\.com/[A-Za-z0-9_.-]+/([a-f0-9-]{8,})", u, re.I):
                    direct_candidates.append(("ashby", org, u, it.get("title") or ""))
        time.sleep(1.2) # Avoid rate limit

    print(f"\nDiscovered {len(new_ashby_orgs)} Ashby orgs from search.")

    print("\n--- Running Paced Firecrawl Searches for Lever ---")
    for q in lever_queries:
        print(f"Searching: {q[:55]}...", flush=True)
        items = firecrawl_search_one(q, limit=25)
        for it in items:
            u = it.get("url") or ""
            if m := re.search(r"https?://(?:jobs\.)?lever\.co/([A-Za-z0-9_.-]+)", u, re.I):
                org = m.group(1).lower().strip("/")
                if org not in ("v0", "search", "apply", "postings", "jobtwine"):
                    new_lever_orgs.add(org)
                if m_id := re.search(r"https?://(?:jobs\.)?lever\.co/[A-Za-z0-9_.-]+/([a-f0-9-]{8,})", u, re.I):
                    direct_candidates.append(("lever", org, u, it.get("title") or ""))
        time.sleep(1.2)

    print(f"\nDiscovered {len(new_lever_orgs)} Lever orgs from search.")

    # Query newly discovered orgs with board APIs for postings >= 2026-10-01
    print(f"\nQuerying Board APIs for {len(new_ashby_orgs)} new Ashby orgs and {len(new_lever_orgs)} new Lever orgs...", flush=True)
    with ThreadPoolExecutor(max_workers=25) as ex:
        futs_a = {ex.submit(fetch_ashby_fresh, o, applied_set): o for o in new_ashby_orgs}
        futs_l = {ex.submit(fetch_lever_fresh, o, applied_set): o for o in new_lever_orgs}

        for f in as_completed(futs_a):
            for j in f.result():
                u_norm = j["url"].strip().lower().rstrip("/")
                if u_norm not in seen_ashby_urls and u_norm not in applied_set:
                    seen_ashby_urls.add(u_norm)
                    existing_ashby.append(j)

        for f in as_completed(futs_l):
            for j in f.result():
                u_norm = j["url"].strip().lower().rstrip("/")
                if u_norm not in seen_lever_urls and u_norm not in applied_set:
                    seen_lever_urls.add(u_norm)
                    existing_lever.append(j)

    print(f"\nUpdated Counts after new org API harvest:")
    print(f"  Ashby: {len(existing_ashby)}")
    print(f"  Lever: {len(existing_lever)}")

    # Save progress
    with open(OUT_DIR / "temp_fresh_ashby.json", "w", encoding="utf-8") as f:
        json.dump(existing_ashby, f, indent=2)
    with open(OUT_DIR / "temp_fresh_lever.json", "w", encoding="utf-8") as f:
        json.dump(existing_lever, f, indent=2)

if __name__ == "__main__":
    main()
