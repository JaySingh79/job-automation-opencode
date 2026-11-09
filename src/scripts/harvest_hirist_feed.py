"""
Script to process harvested Hirist jobfeed data, deduplicate, filter against prior applications,
and split into 5 balanced batches for parallel subagent execution.
"""

import os
import json
import glob
from datetime import datetime, timezone

def main():
    raw_path = r"C:\Users\binit\.gemini\antigravity-cli\brain\2d4ae85a-6edc-4124-9a36-9936051afc21\.system_generated\steps\73\output.txt"
    with open(raw_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Find the JSON substring
    idx = text.find("{")
    if idx == -1:
        raise ValueError("Could not find JSON object in output.txt")
    
    decoder = json.JSONDecoder()
    raw_data, _ = decoder.raw_decode(text[idx:])
    jobs = raw_data.get("jobs", [])
    print(f"Total raw harvested jobs: {len(jobs)}")

    # Load all previously applied job IDs across all files
    applied_ids = set()
    for fp in glob.glob("src/applied/*hirist*.json"):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        jid = item.get("jobId") or item.get("id")
                        if jid:
                            applied_ids.add(int(jid))
                elif isinstance(data, dict):
                    entries = data.get("applied", []) + data.get("applied_jobs", []) + data.get("jobs", [])
                    for item in entries:
                        jid = item.get("jobId") or item.get("id")
                        if jid:
                            applied_ids.add(int(jid))
        except Exception as e:
            print(f"Warning reading {fp}: {e}")

    print(f"Found {len(applied_ids)} previously applied Hirist job IDs.")

    # Filter out already applied or applied==1
    candidates = []
    seen = set()
    for j in jobs:
        jid = int(j["id"])
        if jid in seen or jid in applied_ids or j.get("applied") == 1:
            continue
        seen.add(jid)

        # Exclude non-India unless remote
        loc = (j.get("location") or "").lower()
        if loc and not any(ind in loc for ind in ["india", "bangalore", "bengaluru", "hyderabad", "pune", "gurgaon", "gurugram", "noida", "delhi", "mumbai", "chennai", "remote"]):
            continue

        candidates.append(j)

    print(f"Total eligible unapplied candidates: {len(candidates)}")

    # Sort candidates:
    # 1. min <= 2 first (fresh / early career)
    # 2. sourceFeed '0-1' then '2-3'
    # 3. newer createdTime if available
    def sort_key(job):
        min_e = job.get("min", 0)
        feed_prio = 0 if job.get("sourceFeed") == "0-1" else 1
        tier = 0 if min_e <= 2 else 1
        return (tier, feed_prio, min_e)

    candidates.sort(key=sort_key)

    # Save master queue
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir = os.path.join("src", "job_search_results", "hirist")
    batch_dir = os.path.join(out_dir, "batches")
    os.makedirs(batch_dir, exist_ok=True)

    master_file = os.path.join(out_dir, f"hirist_feed_harvest_{today_str}.json")
    with open(master_file, "w", encoding="utf-8") as f:
        json.dump({
            "harvest_date": today_str,
            "total_candidates": len(candidates),
            "jobs": candidates
        }, f, indent=2)
    print(f"Saved master candidates list to {master_file}")

    # We need to apply to 100 jobs. To ensure we safely hit 100 even if some require assessments,
    # let's select 130 jobs (26 per batch across 5 batches).
    target_total = min(len(candidates), 130)
    selected = candidates[:target_total]
    print(f"Selected {len(selected)} jobs for 5 batches (~{len(selected)//5} per batch)")

    # Partition into 5 batches evenly
    num_batches = 5
    batch_size = (len(selected) + num_batches - 1) // num_batches
    for i in range(num_batches):
        batch_jobs = selected[i * batch_size : (i + 1) * batch_size]
        for b_job in batch_jobs:
            b_job["batch_index"] = i + 1
            b_job["status"] = "pending"
        
        batch_file = os.path.join(batch_dir, f"hirist_batch_{i+1}_{today_str}.json")
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump({
                "batch_id": i + 1,
                "date": today_str,
                "target_applied": 20,
                "total_jobs": len(batch_jobs),
                "jobs": batch_jobs
            }, f, indent=2)
        print(f"Batch {i+1}: {len(batch_jobs)} jobs written to {batch_file}")

if __name__ == "__main__":
    main()
