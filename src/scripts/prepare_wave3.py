import json

with open("src/job_search_results/2026-10-17-fresh-100-final.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("src/applied/jobs_applied.json", "r", encoding="utf-8") as f:
    applied = json.load(f)
applied_urls = {j.get("url", "").rstrip("/") for j in applied}

jobs = data.get("jobs", data)
unapplied = [j for j in jobs if j.get("url", "").rstrip("/") not in applied_urls]

print(f"Total unapplied: {len(unapplied)}")
for idx, j in enumerate(unapplied[:15]):
    print(f"[{idx}] {j.get('platform')} | {j.get('org') or j.get('company')} | {j.get('title')} | {j.get('location')}")
    print(f"     URL: {j.get('url')}")
