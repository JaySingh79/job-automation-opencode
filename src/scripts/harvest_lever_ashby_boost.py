"""
harvest_lever_ashby_boost.py — Boost Lever and Ashby to 100+ fresh postings (>= 2026-10-01).
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
from expand_fresh_harvest import firecrawl_search_one

def main():
    applied_set = load_applied_set()
    existing_ashby = json.loads((OUT_DIR / "temp_fresh_ashby.json").read_text(encoding="utf-8"))
    existing_lever = json.loads((OUT_DIR / "temp_fresh_lever.json").read_text(encoding="utf-8"))

    seen_ashby_urls = {j["url"].strip().lower().rstrip("/") for j in existing_ashby}
    seen_lever_urls = {j["url"].strip().lower().rstrip("/") for j in existing_lever}

    print(f"Current Counts: Ashby={len(existing_ashby)}, Lever={len(existing_lever)}")

    lever_queries = [
        'site:jobs.lever.co "Bengaluru" after:2026-10-01',
        'site:jobs.lever.co "Bangalore" after:2026-10-01',
        'site:jobs.lever.co "Hyderabad" after:2026-10-01',
        'site:jobs.lever.co "Pune" after:2026-10-01',
        'site:jobs.lever.co "Gurgaon" OR "Gurugram" OR "Noida" after:2026-10-01',
        'site:jobs.lever.co "Mumbai" OR "Delhi" after:2026-10-01',
        'site:jobs.lever.co "Remote - India" after:2026-10-01',
        'site:jobs.lever.co ("India" OR "Remote") ("Software" OR "Engineer") after:2026-10-01',
        'site:jobs.lever.co ("India" OR "Remote") ("Developer" OR "Data") after:2026-10-01',
        'site:jobs.lever.co ("India" OR "Remote") ("Backend" OR "Full Stack" OR "Fullstack") after:2026-10-01',
        'site:jobs.lever.co ("India" OR "Remote") ("Python" OR "AI" OR "ML") after:2026-10-01',
        'site:jobs.lever.co ("India" OR "Remote") ("Associate" OR "Junior" OR "Intern") after:2026-10-01',
    ]

    ashby_queries = [
        'site:jobs.ashbyhq.com "Bengaluru" after:2026-10-01',
        'site:jobs.ashbyhq.com "Bangalore" after:2026-10-01',
        'site:jobs.ashbyhq.com "Hyderabad" after:2026-10-01',
        'site:jobs.ashbyhq.com "Pune" after:2026-10-01',
        'site:jobs.ashbyhq.com "Gurgaon" OR "Gurugram" OR "Noida" after:2026-10-01',
        'site:jobs.ashbyhq.com "Remote - India" after:2026-10-01',
        'site:jobs.ashbyhq.com ("India" OR "Remote") ("Software" OR "Engineer") after:2026-10-01',
        'site:jobs.ashbyhq.com ("India" OR "Remote") ("Developer" OR "Data") after:2026-10-01',
        'site:jobs.ashbyhq.com ("India" OR "Remote") ("Backend" OR "Fullstack") after:2026-10-01',
        'site:jobs.ashbyhq.com ("India" OR "Remote") ("Python" OR "AI" OR "ML") after:2026-10-01',
    ]

    new_lever_orgs = set()
    new_ashby_orgs = set()

    print("\n--- Running Lever Boost Queries ---", flush=True)
    for q in lever_queries:
        print(f"Searching: {q[:55]}...", flush=True)
        items = firecrawl_search_one(q, limit=25)
        for it in items:
            u = it.get("url") or ""
            if m := re.search(r"https?://(?:jobs\.)?lever\.co/([A-Za-z0-9_.-]+)", u, re.I):
                org = m.group(1).lower().strip("/")
                if org not in ("v0", "search", "apply", "postings", "jobtwine"):
                    new_lever_orgs.add(org)
        time.sleep(1.2)

    print(f"Discovered {len(new_lever_orgs)} new Lever orgs.", flush=True)

    print("\n--- Running Ashby Boost Queries ---", flush=True)
    for q in ashby_queries:
        print(f"Searching: {q[:55]}...", flush=True)
        items = firecrawl_search_one(q, limit=25)
        for it in items:
            u = it.get("url") or ""
            if m := re.search(r"https?://jobs\.ashbyhq\.com/([A-Za-z0-9_.-]+)", u, re.I):
                org = m.group(1).lower().strip("/")
                if org not in ("api", "posting-api", "job-board"):
                    new_ashby_orgs.add(org)
        time.sleep(1.2)

    print(f"Discovered {len(new_ashby_orgs)} new Ashby orgs.", flush=True)

    # Fast probe with 30 workers and 5s timeout to prevent any hangs
    print(f"\nProbing {len(new_lever_orgs)} Lever orgs and {len(new_ashby_orgs)} Ashby orgs...", flush=True)

    def safe_fetch_lever(org):
        try:
            return fetch_lever_fresh(org, applied_set)
        except Exception:
            return []

    def safe_fetch_ashby(org):
        try:
            return fetch_ashby_fresh(org, applied_set)
        except Exception:
            return []

    with ThreadPoolExecutor(max_workers=30) as ex:
        futs_l = {ex.submit(safe_fetch_lever, o): o for o in new_lever_orgs}
        futs_a = {ex.submit(safe_fetch_ashby, o): o for o in new_ashby_orgs}

        for f in as_completed(futs_l):
            for j in f.result():
                u_norm = j["url"].strip().lower().rstrip("/")
                if u_norm not in seen_lever_urls and u_norm not in applied_set:
                    seen_lever_urls.add(u_norm)
                    existing_lever.append(j)

        for f in as_completed(futs_a):
            for j in f.result():
                u_norm = j["url"].strip().lower().rstrip("/")
                if u_norm not in seen_ashby_urls and u_norm not in applied_set:
                    seen_ashby_urls.add(u_norm)
                    existing_ashby.append(j)

    print(f"\nBOOST COMPLETE:", flush=True)
    print(f"  Ashby: {len(existing_ashby)}", flush=True)
    print(f"  Lever: {len(existing_lever)}", flush=True)

    with open(OUT_DIR / "temp_fresh_ashby.json", "w", encoding="utf-8") as f:
        json.dump(existing_ashby, f, indent=2)
    with open(OUT_DIR / "temp_fresh_lever.json", "w", encoding="utf-8") as f:
        json.dump(existing_lever, f, indent=2)

if __name__ == "__main__":
    main()
