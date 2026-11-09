#!/usr/bin/env python3
"""
Weekday Fresher Jobs Lightning-Fast Extractor
Utilizes Next.js SSG Data Endpoints (/_next/data/{buildId}/jobs/{path}.json)
Fetches and qualifies hundreds of fresher jobs in seconds.
"""

import os
import re
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://www.weekday.works"
DEFAULT_BUILD_ID = "kPSg2TKgSCHbj7utG3eud"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"

OUTPUT_DIR = os.path.join("src", "job_search_results", "weekday")
APPLIED_FILE = os.path.join("src", "applied", "weekday.json")

EXCLUDE_TITLE_KEYWORDS = [
    "senior", "sr.", "lead", "principal", "staff", "manager", "head", "director",
    "vp", "architect", "chief", "cto", "expert", "specialist", "partner", "founder",
    "ca articled", "chartered accountant", "sales", "business development", "telesales",
    "telecaller", "operations executive", "recruiter", "talent acquisition", "graphic designer",
    "video editor", "content creator", "accountant", "audit associate", "legal"
]

TECH_KEYWORDS = [
    "software", "sde", "developer", "engineer", "python", "ai", "ml", "machine learning",
    "data", "backend", "full stack", "fullstack", "frontend", "intern", "trainee",
    "graduate", "fresher", "nlp", "computer vision", "analytics", "qa", "test"
]

def get_build_id():
    """Fetch current Next.js buildId from Weekday homepage or return default."""
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/jobs/fresher-jobs",
            headers={"User-Agent": USER_AGENT}
        )
        with urllib.request.urlopen(req, timeout=8) as res:
            html = res.read().decode("utf-8", errors="ignore")
            match = re.search(r'"buildId":"([a-zA-Z0-9_-]+)"', html)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"[!] Warning: Could not detect live buildId ({e}), using fallback: {DEFAULT_BUILD_ID}")
    return DEFAULT_BUILD_ID

def fetch_feed(build_id, path_slug):
    """Fetch JSON data for a specific jobs feed path."""
    url = f"{BASE_URL}/_next/data/{build_id}/jobs/{path_slug}.json"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
            return data.get("pageProps", {}).get("jobs", [])
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"[!] Error fetching {path_slug}: HTTP {e.code}")
    except Exception as e:
        print(f"[!] Error fetching {path_slug}: {e}")
    return []

def is_qualified(job):
    """Strict evaluation against Fresher / SDE / AI / ML / Python / India criteria."""
    title = (job.get("title") or "").strip().lower()
    snippet = (job.get("snippet") or "").strip().lower()
    skills = [s.lower() for s in (job.get("skills") or [])]
    location = (job.get("location") or "").strip().lower()
    work_model = (job.get("workModel") or "").strip().lower()
    exp_str = (job.get("experience") or "").strip().lower()

    # Title exclusions
    for kw in EXCLUDE_TITLE_KEYWORDS:
        # Avoid false positives like "lead" matching "lead generation" if needed, but here simple matching
        if re.search(rf"\b{re.escape(kw)}\b", title):
            return False, f"Title excluded by keyword: {kw}"

    # Experience filter: Must be <= 2 years
    # Weekday exp examples: "0–1 yrs", "1+ yrs", "1–2 yrs", "0–2 yrs", "1–5 yrs", "2–4 yrs"
    if exp_str:
        # Check for 3+, 4+, 5+
        if re.search(r"[3-9]\+\s*yrs", exp_str):
            return False, f"Experience too high: {exp_str}"
        # If range like 3–6 yrs or 4-8 yrs
        range_match = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*yrs", exp_str)
        if range_match:
            min_exp = int(range_match.group(1))
            if min_exp >= 3:
                return False, f"Min experience >= 3: {exp_str}"

    # Location filter: India or Remote
    is_india = any(loc in location for loc in [
        "india", "bengaluru", "bangalore", "hyderabad", "pune", "delhi", "mumbai",
        "gurgaon", "gurugram", "noida", "chennai", "kolkata", "ahmedabad", "remote"
    ])
    is_remote = "remote" in work_model or "remote" in location
    if not (is_india or is_remote):
        return False, f"Non-India location: {location}"

    # Tech stack / Title relevance
    combined_text = f"{title} {' '.join(skills)} {snippet}"
    has_tech = any(re.search(rf"\b{re.escape(k)}\b", combined_text) for k in TECH_KEYWORDS)
    if not has_tech:
        return False, "Non-tech or unrelated role"

    # Strict language rule: Skip pure Java/C++ if Python is absent
    exclusive_java_cpp = (
        ("java" in combined_text or "c++" in combined_text) and
        not any(t in combined_text for t in ["python", "machine learning", "data", "ai", "javascript", "react"])
    )
    if exclusive_java_cpp:
        return False, "Exclusive Java/C++ without Python/Data"

    return True, "Qualified"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(APPLIED_FILE), exist_ok=True)

    # Load existing applied URLs
    applied_urls = set()
    if os.path.exists(APPLIED_FILE):
        try:
            with open(APPLIED_FILE, "r", encoding="utf-8") as f:
                applied_data = json.load(f)
                for item in applied_data:
                    if "url" in item:
                        applied_urls.add(item["url"])
                    if "job_id" in item:
                        applied_urls.add(item["job_id"])
        except Exception:
            pass

    print(f"[*] Starting Weekday Fresher Jobs Extraction...")
    build_id = get_build_id()
    print(f"[*] Using Next.js BuildId: {build_id}")

    # Build targets
    feed_paths = []
    # Fresher general pages
    feed_paths.append("fresher-jobs")
    for i in range(2, 51):
        feed_paths.append(f"fresher-jobs-{i}")
    
    # Targeted categories
    targeted = [
        "python-developer-fresher-jobs", "it-fresher-jobs",
        "data-analyst-fresher-jobs", "remote-fresher-jobs",
        "internship-jobs"
    ]
    for cat in targeted:
        feed_paths.append(cat)
        for i in range(2, 6):
            feed_paths.append(f"{cat}-{i}")

    print(f"[*] Querying {len(feed_paths)} feed paths concurrently...")
    raw_jobs = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=12) as executor:
        future_to_path = {executor.submit(fetch_feed, build_id, p): p for p in feed_paths}
        for future in as_completed(future_to_path):
            jobs = future.result()
            if jobs:
                raw_jobs.extend(jobs)

    elapsed = time.time() - start_time
    print(f"[+] Harvested {len(raw_jobs)} raw job records in {elapsed:.2f}s")

    # Deduplicate by ID
    unique_jobs = {}
    for j in raw_jobs:
        job_id = j.get("id") or j.get("url")
        if job_id and job_id not in unique_jobs:
            unique_jobs[job_id] = j

    print(f"[+] Deduplicated to {len(unique_jobs)} distinct jobs.")

    # Filter qualified fresher jobs
    qualified_jobs = []
    skipped_reasons = {}

    for job in unique_jobs.values():
        job_url = job.get("url") or ""
        # Ensure url points to application tab
        if not job_url:
            continue
        if job_url in applied_urls or job.get("id") in applied_urls:
            continue

        ok, reason = is_qualified(job)
        if ok:
            # Append tab=application
            clean_url = job_url.split("?")[0]
            job["apply_url"] = f"{clean_url}?tab=application"
            qualified_jobs.append(job)
        else:
            skipped_reasons[reason] = skipped_reasons.get(reason, 0) + 1

    print(f"[+] Total Qualified Fresher Jobs: {len(qualified_jobs)}")
    print(f"[*] Filter summary: {dict(list(skipped_reasons.items())[:6])}")

    # Save master list
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    master_file = os.path.join(OUTPUT_DIR, f"weekday_fresher_harvest_{date_str}.json")
    with open(master_file, "w", encoding="utf-8") as f:
        json.dump(qualified_jobs, f, indent=2)
    print(f"[+] Saved master qualified jobs to: {master_file}")

    # Split into 4 balanced batches
    num_batches = 4
    batches = [[] for _ in range(num_batches)]
    for idx, job in enumerate(qualified_jobs):
        batches[idx % num_batches].append(job)

    for i in range(num_batches):
        batch_file = os.path.join(OUTPUT_DIR, f"weekday_queue_batch{i+1}.json")
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump(batches[i], f, indent=2)
        print(f"[+] Batch {i+1}: {len(batches[i])} jobs -> {batch_file}")

    # Save summary manifest
    manifest = {
        "harvest_date": date_str,
        "build_id": build_id,
        "total_harvested": len(raw_jobs),
        "total_unique": len(unique_jobs),
        "total_qualified": len(qualified_jobs),
        "batch_counts": [len(b) for b in batches],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    manifest_file = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[+] Extraction and batch partitioning complete!")

if __name__ == "__main__":
    main()
