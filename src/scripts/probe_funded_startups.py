"""
probe_funded_startups.py — Test company slugs on Ashby and Lever.
"""
import json
import re
import ssl
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

OCT_1_2026 = datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp()
CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0"}

# Helper imports
import sys
sys.path.append(r"D:\Projects\PRACTICE\firecrawl_test\src\scripts")
from harvest_fresh_300_ats import classify_location, classify_title, load_applied_set, fetch_json
from harvest_fresh_monthly_ats import fetch_lever_fresh, fetch_ashby_fresh

def test_slugs():
    applied_set = load_applied_set()
    existing_ashby = json.loads(Path("src/job_search_results/ashby_lever_greenhouse/temp_fresh_ashby.json").read_text(encoding="utf-8"))
    existing_lever = json.loads(Path("src/job_search_results/ashby_lever_greenhouse/temp_fresh_lever.json").read_text(encoding="utf-8"))

    seen_ashby = {j["url"].strip().lower().rstrip("/") for j in existing_ashby}
    seen_lever = {j["url"].strip().lower().rstrip("/") for j in existing_lever}

    print(f"Current verified fresh: Ashby={len(existing_ashby)}, Lever={len(existing_lever)}")

    # Extract all company names and slugs from all leads files
    candidate_slugs = set()
    for f in Path("src/job_search_results/leads_and_startups").glob("*.json"):
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            # URLs
            for m in re.finditer(r"jobs\.ashbyhq\.com/([A-Za-z0-9_.-]+)", content, re.I):
                s = m.group(1).lower().strip("/")
                if s not in ("api", "posting-api", "job-board"): candidate_slugs.add(s)
            for m in re.finditer(r"(?:jobs\.)?lever\.co/([A-Za-z0-9_.-]+)", content, re.I):
                s = m.group(1).lower().strip("/")
                if s not in ("v0", "search", "apply", "postings", "jobtwine"): candidate_slugs.add(s)
            # Company names
            try:
                data = json.loads(content)
                items = []
                if isinstance(data, list): items = data
                elif isinstance(data, dict):
                    for v in data.values():
                        if isinstance(v, list): items.extend(v)
                for it in items:
                    if isinstance(it, dict) and "name" in it:
                        # clean name into slug
                        name = re.sub(r"[^A-Za-z0-9]+", "-", it["name"].lower()).strip("-")
                        candidate_slugs.add(name)
                        # also raw name
                        raw = re.sub(r"[^A-Za-z0-9]+", "", it["name"].lower())
                        candidate_slugs.add(raw)
            except Exception:
                pass
        except Exception:
            pass

    print(f"Total candidate slugs from leads & startups: {len(candidate_slugs)}")

    # Test all candidate slugs against Ashby and Lever
    def probe_ashby(slug):
        try:
            return fetch_ashby_fresh(slug, applied_set)
        except Exception:
            return []

    def probe_lever(slug):
        try:
            return fetch_lever_fresh(slug, applied_set)
        except Exception:
            return []

    with ThreadPoolExecutor(max_workers=30) as ex:
        futs_a = {ex.submit(probe_ashby, s): s for s in candidate_slugs}
        futs_l = {ex.submit(probe_lever, s): s for s in candidate_slugs}

        for f in as_completed(futs_a):
            for j in f.result():
                u_norm = j["url"].strip().lower().rstrip("/")
                if u_norm not in seen_ashby and u_norm not in applied_set:
                    seen_ashby.add(u_norm)
                    existing_ashby.append(j)

        for f in as_completed(futs_l):
            for j in f.result():
                u_norm = j["url"].strip().lower().rstrip("/")
                if u_norm not in seen_lever and u_norm not in applied_set:
                    seen_lever.add(u_norm)
                    existing_lever.append(j)

    print(f"\nUPDATED COUNTS:")
    print(f"  Ashby: {len(existing_ashby)}")
    print(f"  Lever: {len(existing_lever)}")

    Path("src/job_search_results/ashby_lever_greenhouse/temp_fresh_ashby.json").write_text(json.dumps(existing_ashby, indent=2), encoding="utf-8")
    Path("src/job_search_results/ashby_lever_greenhouse/temp_fresh_lever.json").write_text(json.dumps(existing_lever, indent=2), encoding="utf-8")

if __name__ == "__main__":
    test_slugs()
