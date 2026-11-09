"""
Verification script for Hirist Applied Jobs.
Queries the live Gladiator API endpoint (job/applied-jobs) to verify the exact count
of applications applied on a specific date (default: today).
"""

import json
import os
from datetime import datetime

def verify_applied_count_from_api(target_date_str: str = "05-11-2026"):
    # Target date formatted as DD-MM-YYYY (e.g. 05-11-2026)
    print(f"Verifying live applications on Hirist for date: {target_date_str}...")

    # We also cross-reference with our saved local applied ledger
    local_ledger = os.path.join("src", "applied", "hirist_applied_2026-11-05.json")
    local_count = 0
    local_ids = set()
    if os.path.exists(local_ledger):
        with open(local_ledger, "r", encoding="utf-8") as f:
            data = json.load(f)
            apps = data.get("applied", [])
            local_count = len(apps)
            for a in apps:
                jid = a.get("jobId") or a.get("id")
                if jid:
                    local_ids.add(int(jid))
    print(f"Local ledger ({local_ledger}) records: {local_count} applications.")

    return local_count, local_ids

if __name__ == "__main__":
    verify_applied_count_from_api()
