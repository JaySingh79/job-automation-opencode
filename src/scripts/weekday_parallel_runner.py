import os
import sys
import json
import argparse
from datetime import datetime

QUEUE_DIR = os.path.join("src", "job_search_results", "weekday")
APPLIED_FILE = os.path.join("src", "applied", "weekday.json")
PROGRESS_DIR = os.path.join("src", "application_progress", "weekday")

def get_applied_urls():
    applied = set()
    if os.path.exists(APPLIED_FILE):
        try:
            with open(APPLIED_FILE, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    if "url" in item:
                        applied.add(item["url"].split("?")[0].strip().rstrip("/"))
                    if "job_id" in item:
                        applied.add(item["job_id"].strip())
        except Exception:
            pass
    return applied

def get_batch_slice(batch_num, limit=10):
    applied = get_applied_urls()
    batch_file = os.path.join(QUEUE_DIR, f"weekday_queue_batch{batch_num}.json")
    if not os.path.exists(batch_file):
        return []
    with open(batch_file, "r", encoding="utf-8") as f:
        jobs = json.load(f)
    
    candidates = []
    for j in jobs:
        clean_url = (j.get("url") or "").split("?")[0].strip().rstrip("/")
        jid = (j.get("id") or "").strip()
        if clean_url in applied or jid in applied:
            continue
        candidates.append({
            "id": jid,
            "title": j.get("title"),
            "company": j.get("company"),
            "url": j.get("url"),
            "apply_url": j.get("apply_url")
        })
        if len(candidates) >= limit:
            break
    return candidates

def get_sprint_workload(per_batch=10):
    workload = {}
    for b in range(1, 5):
        workload[f"worker_{b}"] = get_batch_slice(b, limit=per_batch)
    return workload

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10, help="Jobs per worker")
    args = parser.parse_args()

    workload = get_sprint_workload(per_batch=args.limit)
    total = sum(len(jobs) for jobs in workload.values())
    print(f"[*] Prepared workload for {total} jobs ({args.limit} per worker):")
    for w, jobs in workload.items():
        print(f"  {w}: {len(jobs)} jobs")
        for j in jobs[:2]:
            print(f"    - {j['title']} @ {j['company']}")

    os.makedirs(PROGRESS_DIR, exist_ok=True)
    sprint_file = os.path.join(PROGRESS_DIR, "current_sprint.json")
    with open(sprint_file, "w", encoding="utf-8") as f:
        json.dump(workload, f, indent=2)
    print(f"[+] Saved sprint workload to: {sprint_file}")
