"""
Consolidates Hirist batch run progress files into the authoritative applied ledger
and updates batch queues.
"""

import os
import json
import glob
from datetime import datetime, timezone

def consolidate():
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    progress_dir = os.path.join("src", "application_progress", "hirist")
    batch_dir = os.path.join("src", "job_search_results", "hirist", "batches")
    applied_dir = os.path.join("src", "applied")
    os.makedirs(applied_dir, exist_ok=True)

    applied_file = os.path.join(applied_dir, f"hirist_applied_{today_str}.json")

    # Load existing applied ledger if exists
    existing_applied = []
    seen_ids = set()
    if os.path.exists(applied_file):
        try:
            with open(applied_file, "r", encoding="utf-8") as f:
                d = json.load(f)
                if isinstance(d, dict):
                    entries = d.get("applied", [])
                elif isinstance(d, list):
                    entries = d
                else:
                    entries = []
                for item in entries:
                    jid = item.get("jobId") or item.get("id")
                    if jid and int(jid) not in seen_ids:
                        seen_ids.add(int(jid))
                        existing_applied.append(item)
        except Exception as e:
            print(f"Warning reading existing ledger: {e}")

    # Inspect all batch progress files for today
    pattern = os.path.join(progress_dir, f"hirist_progress_batch_*_{today_str}.json")
    files = sorted(glob.glob(pattern))

    total_applied = len(existing_applied)
    total_parked = 0
    total_already_applied = 0
    batch_summaries = {}

    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            b_id = data.get("batch") or data.get("batch_id")
            sprint = data.get("sprint", 1)
            b_key = f"batch_{b_id}_sprint_{sprint}"
            results = data.get("all_results", []) + data.get("results", [])
            
            b_applied = 0
            b_parked = 0
            b_already = 0

            for res in results:
                jid = res.get("jobId") or res.get("id")
                status = res.get("status")
                if status == "applied":
                    b_applied += 1
                    if jid and int(jid) not in seen_ids:
                        seen_ids.add(int(jid))
                        existing_applied.append(res)
                        total_applied += 1
                elif status in ["parked_assessment", "parked"]:
                    b_parked += 1
                    total_parked += 1
                elif status in ["already_applied", "skipped_applied"]:
                    b_already += 1
                    total_already_applied += 1

            batch_summaries[b_key] = {
                "applied": b_applied,
                "parked": b_parked,
                "already_applied": b_already,
                "total_processed": len(results)
            }
        except Exception as e:
            print(f"Error processing {fp}: {e}")

    # Save consolidated applied ledger
    payload = {
        "platform": "hirist",
        "date": today_str,
        "total_applied": len(existing_applied),
        "total_parked_assessments": total_parked,
        "total_already_applied": total_already_applied,
        "batch_breakdown": batch_summaries,
        "applied": existing_applied
    }

    with open(applied_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"\n[CONSOLIDATION COMPLETE]")
    print(f"Total Confirmed Applied Applications: {len(existing_applied)}")
    print(f"Saved to: {applied_file}")
    for b_name, b_stat in batch_summaries.items():
        print(f"  {b_name}: {b_stat['applied']} applied / {b_stat['total_processed']} processed")

    return len(existing_applied)

if __name__ == "__main__":
    consolidate()
