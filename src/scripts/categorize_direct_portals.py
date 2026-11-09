import json
from pathlib import Path
from collections import Counter

path = Path("src/job_search_results/naukri/direct_company_platforms/custom_company_careers.json")
data = json.loads(path.read_text(encoding="utf-8"))

jobs = data.get("jobs", [])
print(f"Total jobs: {len(jobs)}")

domain_groups = {}
for j in jobs:
    d = j.get("ats_domain", "unknown")
    if d not in domain_groups:
        domain_groups[d] = []
    domain_groups[d].append(j)

# Sort by count descending
sorted_domains = sorted(domain_groups.items(), key=lambda x: len(x[1]), reverse=True)

print("\n--- Domain Breakdown ---")
for d, j_list in sorted_domains:
    cos = set(j["company"] for j in j_list)
    print(f"{d} ({len(j_list)} jobs): {', '.join(list(cos)[:3])}")
