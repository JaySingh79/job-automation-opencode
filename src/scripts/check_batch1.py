import json
from pathlib import Path

p = Path(r"src/job_search_results/naukri/direct_company_platforms/batch_bigtech_custom.json")
with open(p, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total jobs: {data.get('total_jobs')}")
for i, j in enumerate(data.get("jobs", [])[:25]):
    print(f"{i+1}. [{j.get('company')}] {j.get('title')} ({j.get('experience')}) | ATS: {j.get('ats_domain')} | URL: {j.get('company_site_url')}")
