"""
Process and partition fresh AI/ML and SDE candidates for the 200 additional applications sweep.
"""

import os
import json

def main():
    raw_path = r"C:\Users\binit\.gemini\antigravity-cli\brain\2d4ae85a-6edc-4124-9a36-9936051afc21\.system_generated\steps\309\output.txt"
    with open(raw_path, "r", encoding="utf-8") as f:
        text = f.read()

    idx = text.find("{")
    if idx == -1:
        raise ValueError("No JSON found")

    decoder = json.JSONDecoder()
    raw_data, _ = decoder.raw_decode(text[idx:])
    jobs = raw_data.get("jobs", [])
    print(f"Total parsed unapplied candidates: {len(jobs)}")

    # Save master additional harvest
    out_dir = os.path.join("src", "job_search_results", "hirist")
    master_file = os.path.join(out_dir, "hirist_additional_200_harvest_2026-11-05.json")
    with open(master_file, "w", encoding="utf-8") as f:
        json.dump({"total": len(jobs), "jobs": jobs}, f, indent=2)
    print(f"Saved master additional pool to {master_file}")

    # We need 200 additional applications.
    # To net 200 applications with an ~65% apply rate, 310 candidates is ideal (62 per worker).
    selected = jobs[:310]
    batch_dir = os.path.join(out_dir, "batches")
    os.makedirs(batch_dir, exist_ok=True)

    num_workers = 5
    batch_size = len(selected) // num_workers
    for i in range(num_workers):
        b_jobs = selected[i * batch_size : (i + 1) * batch_size] if i < num_workers - 1 else selected[i * batch_size :]
        out_batch = os.path.join(batch_dir, f"hirist_additional_batch_{i+1}_2026-11-05.json")
        with open(out_batch, "w", encoding="utf-8") as f:
            json.dump({
                "worker": i + 1,
                "target_applied": 40,
                "total_candidates": len(b_jobs),
                "jobs": b_jobs
            }, f, indent=2)
        print(f"Worker {i+1}: {len(b_jobs)} jobs written to {out_batch}")

if __name__ == "__main__":
    main()
