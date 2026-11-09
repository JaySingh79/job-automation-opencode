import json
from pathlib import Path
from collections import Counter

path = Path("src/job_search_results/naukri/direct_company_platforms/custom_company_careers.json")
data = json.loads(path.read_text(encoding="utf-8"))

jobs = data.get("jobs", [])
print(f"Total jobs: {len(jobs)}")

domain_counts = Counter(j.get("ats_domain") for j in jobs)
print("\nTop 20 Domains:")
for d, count in domain_counts.most_common(20):
    print(f"  {d}: {count}")

print("\nSample prominent companies and URLs:")
prominent = ["google", "apple", "payu", "barclays", "ey", "crisil", "synopsys", "tesco", "wayfair"]
found = {}
for j in jobs:
    co = j.get("company", "").lower()
    for p in prominent:
        if p in co and p not in found:
            found[p] = (j.get("company"), j.get("title"), j.get("company_site_url"), j.get("ats_domain"))

for p, info in found.items():
    print(f"[{p.upper()}] Company: {info[0]} | Title: {info[1]} | URL: {info[2]} | Domain: {info[3]}")
