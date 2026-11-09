#!/usr/bin/env python3
"""
Weekday Underneath ATS Career URL Extractor
Resolves exact careersPageLink for all external (fastApply=False) fresher jobs
and categorizes them into their respective subagent search result folders.
"""

import os
import re
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

BUILD_ID = "-0uncBQ8SMEce1yNKfyov"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"

HARVEST_FILE = os.path.join("src", "job_search_results", "weekday", "weekday_fresher_harvest_2026-10-29.json")

# Destination folders per workspace rules
WORKDAY_DIR = os.path.join("src", "job_search_results", "workday")
ATS_DIR = os.path.join("src", "job_search_results", "ashby_lever_greenhouse")
EIGHTFOLD_DIR = os.path.join("src", "job_search_results", "eightfold")
DIRECT_CO_DIR = os.path.join("src", "job_search_results", "weekday")

def fetch_job_details(slug):
    url = f"https://jobs.weekday.works/_next/data/{BUILD_ID}/{slug}.json"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=8) as res:
            data = json.loads(res.read().decode("utf-8"))
            return slug, data.get("pageProps", {}).get("jobDetails")
    except Exception as e:
        return slug, None

def categorize_ats(url):
    u = (url or "").lower()
    if "myworkdayjobs.com" in u:
        return "workday"
    elif "ashby.com" in u or "lever.co" in u or "greenhouse.io" in u:
        return "ashby_lever_greenhouse"
    elif "eightfold.ai" in u:
        return "eightfold"
    elif "smartrecruiters.com" in u:
        return "smartrecruiters"
    elif "successfactors.com" in u:
        return "successfactors"
    elif "avature.net" in u or "jobs." in u:
        return "company_direct"
    return "company_direct"

def main():
    if not os.path.exists(HARVEST_FILE):
        print(f"[!] Harvest file not found: {HARVEST_FILE}")
        return

    with open(HARVEST_FILE, "r", encoding="utf-8") as f:
        all_jobs = json.load(f)

    external_jobs = [j for j in all_jobs if not j.get("fastApply")]
    print(f"[*] Found {len(external_jobs)} external (fastApply=False) qualified fresher jobs.")

    slugs = []
    slug_map = {}
    for j in external_jobs:
        url = j.get("url") or ""
        slug = url.split("?")[0].rstrip("/").split("/")[-1]
        if slug:
            slugs.append(slug)
            slug_map[slug] = j

    print(f"[*] Concurrently resolving exact underneath career links for {len(slugs)} jobs...")
    start_time = time.time()

    resolved_count = 0
    workday_jobs = []
    ats_jobs = []
    eightfold_jobs = []
    direct_jobs = []

    with ThreadPoolExecutor(max_workers=16) as executor:
        future_to_slug = {executor.submit(fetch_job_details, s): s for s in slugs}
        for future in as_completed(future_to_slug):
            slug, details = future.result()
            if not details:
                continue

            orig_job = slug_map.get(slug, {})
            careers_url = details.get("careersPageLink") or details.get("directJobLink")
            if not careers_url:
                continue

            resolved_count += 1
            ats_type = categorize_ats(careers_url)

            record = {
                "id": slug,
                "title": details.get("jobTitle") or orig_job.get("title"),
                "company": details.get("companyName") or orig_job.get("company"),
                "location": details.get("locationList") or orig_job.get("location"),
                "experience": details.get("minimumExperience") or orig_job.get("experience"),
                "salary": details.get("minimumSalary") or orig_job.get("salary"),
                "weekday_url": orig_job.get("url"),
                "careers_url": careers_url,
                "ats_category": ats_type,
                "skills": details.get("skills") or orig_job.get("skills")
            }

            if ats_type == "workday":
                workday_jobs.append(record)
            elif ats_type == "ashby_lever_greenhouse":
                ats_jobs.append(record)
            elif ats_type == "eightfold":
                eightfold_jobs.append(record)
            else:
                direct_jobs.append(record)

    elapsed = time.time() - start_time
    print(f"[+] Successfully resolved {resolved_count}/{len(slugs)} underneath URLs in {elapsed:.2f}s!")
    print(f"    - Workday Jobs: {len(workday_jobs)}")
    print(f"    - Ashby / Lever / Greenhouse Jobs: {len(ats_jobs)}")
    print(f"    - Eightfold Jobs: {len(eightfold_jobs)}")
    print(f"    - Direct Company Career Jobs: {len(direct_jobs)}")

    # Save to designated subfolders per GEMINI.md rules
    os.makedirs(WORKDAY_DIR, exist_ok=True)
    os.makedirs(ATS_DIR, exist_ok=True)
    os.makedirs(EIGHTFOLD_DIR, exist_ok=True)
    os.makedirs(DIRECT_CO_DIR, exist_ok=True)

    with open(os.path.join(WORKDAY_DIR, "weekday_harvested_workday_jobs.json"), "w", encoding="utf-8") as f:
        json.dump(workday_jobs, f, indent=2)

    with open(os.path.join(ATS_DIR, "weekday_harvested_ats_jobs.json"), "w", encoding="utf-8") as f:
        json.dump(ats_jobs, f, indent=2)

    with open(os.path.join(EIGHTFOLD_DIR, "weekday_harvested_eightfold_jobs.json"), "w", encoding="utf-8") as f:
        json.dump(eightfold_jobs, f, indent=2)

    with open(os.path.join(DIRECT_CO_DIR, "weekday_external_direct_company_urls.json"), "w", encoding="utf-8") as f:
        json.dump(direct_jobs, f, indent=2)

    print(f"[+] All resolved underneath URLs saved strictly into designated board subfolders!")

if __name__ == "__main__":
    main()
