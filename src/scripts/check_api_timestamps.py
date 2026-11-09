"""
check_api_timestamps.py — Check timestamp distribution of board API jobs.
"""
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Threshold: ~35 days ago from 2026-11-07 -> 2026-10-01
OCT_1_2026 = datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp()
NOW = datetime(2026, 11, 7, 12, 0, 0, tzinfo=timezone.utc).timestamp()

print(f"Oct 1, 2026 epoch: {OCT_1_2026}")
print(f"Current approx epoch: {NOW}")

f_all = Path("src/job_search_results/ashby_lever_greenhouse/2026-11-07-fresh-300-ashby-lever-greenhouse.json")
if f_all.exists():
    data = json.loads(f_all.read_text(encoding="utf-8"))
    jobs = data["jobs"]
    print(f"Loaded {len(jobs)} jobs from previous batch.")

    fresh_count = 0
    stale_count = 0
    unknown_count = 0

    for j in jobs:
        ts = None
        # Lever has created_at (int ms)
        if j.get("created_at"):
            ts = j["created_at"] / 1000.0
        # Ashby has published_at (ISO str)
        elif j.get("published_at"):
            try:
                # e.g. 2026-10-15T...
                dt = datetime.fromisoformat(j["published_at"].replace("Z", "+00:00"))
                ts = dt.timestamp()
            except Exception:
                pass
        # Greenhouse has updated_at (ISO str)
        elif j.get("updated_at"):
            try:
                dt = datetime.fromisoformat(j["updated_at"].replace("Z", "+00:00"))
                ts = dt.timestamp()
            except Exception:
                pass

        if ts is not None:
            if ts >= OCT_1_2026:
                fresh_count += 1
            else:
                stale_count += 1
        else:
            unknown_count += 1

    print(f"Timestamp analysis of previous 300:")
    print(f"  Posted >= Oct 1, 2026 (<37 days old): {fresh_count}")
    print(f"  Posted < Oct 1, 2026 (>37 days old):  {stale_count}")
    print(f"  Unknown date:                          {unknown_count}")
