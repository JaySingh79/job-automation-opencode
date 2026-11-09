import json

with open("src/job_search_results/2026-10-17-fresh-100-final.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Also check already applied URLs
with open("src/applied/jobs_applied.json", "r", encoding="utf-8") as f:
    applied_data = json.load(f)
applied_urls = {j.get("url", "").rstrip("/") for j in applied_data}

jobs = data.get("jobs", data)
print(f"Total jobs in fresh-100-final: {len(jobs)}")
fresh_jobs = []
for j in jobs:
    url = j.get("url", "").rstrip("/")
    if url not in applied_urls:
        fresh_jobs.append(j)

print(f"Pending unapplied jobs in this file: {len(fresh_jobs)}")
for idx, j in enumerate(fresh_jobs[:20]):
    print(f"{idx+1}. [{j.get('platform')}] {j.get('org') or j.get('company')} - {j.get('title')} ({j.get('location')})")
    print(f"   URL: {j.get('url')}")
