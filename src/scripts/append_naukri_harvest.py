#!/usr/bin/env python3
"""Helper script to append and deduplicate harvested Naukri job records."""

import json
import sys
from pathlib import Path

DATA_FILE = Path("src/job_search_results/naukri/naukri_fresher_high_ctc_harvest.json")


def append_jobs(batch_file: str):
    with open(batch_file, "r", encoding="utf-8") as f:
        new_jobs = json.load(f)

    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {
            "harvest_target": "300-500 Fresher AI/ML, Data Science, and SDE jobs (CTC >= 15 LPA)",
            "total_jobs": 0,
            "jobs": [],
        }

    existing_ids = {j["job_id"] for j in data["jobs"]}
    existing_urls = {j["url"] for j in data["jobs"]}

    added = 0
    for j in new_jobs:
        jid = j.get("job_id")
        url = j.get("url")
        if jid and jid in existing_ids:
            continue
        if url and url in existing_urls:
            continue
        existing_ids.add(jid)
        existing_urls.add(url)
        data["jobs"].append(j)
        added += 1

    data["total_jobs"] = len(data["jobs"])

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Added {added} new unique jobs. Total pool size: {data['total_jobs']}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        append_jobs(sys.argv[1])
    else:
        print("Usage: uv run --no-project python src/scripts/append_naukri_harvest.py <batch_json_path>")
