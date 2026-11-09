import json
from pathlib import Path

p = Path(r"src/job_search_results/naukri/direct_company_platforms/batch_bigtech_custom.json")
with open(p, "r", encoding="utf-8") as f:
    data = json.load(f)

jobs = data.get("jobs", [])

print(f"Total jobs in batch: {len(jobs)}")

# Let's inspect companies and titles
valid_fresher_jobs = []
skipped_jobs = []

for idx, j in enumerate(jobs):
    title = j.get("title", "").strip()
    exp = j.get("experience", "").strip()
    company = j.get("company", "").strip()
    url = j.get("company_site_url", "").strip()
    skills = [s.lower() for s in j.get("skills", [])]
    
    # Check experience & title rules:
    # 0-2 YoE target, <=2 YoE. Skip 3+ YoE or 'Senior', 'Staff', 'Lead', 'Principal'.
    is_senior = any(w in title.lower() for w in ["senior", "sr.", "lead", "staff", "principal", "architect", "manager", "director"])
    
    # Check Java/C++ exclusive stack
    tech_str = " ".join(skills)
    only_java_cpp = False
    if ("java" in tech_str or "c++" in tech_str) and "python" not in tech_str and "machine learning" not in tech_str and "ai" not in tech_str:
        only_java_cpp = True
        
    reason = []
    if is_senior:
        reason.append("Senior title")
    if only_java_cpp:
        reason.append("Exclusively Java/C++ without Python")
    if "wordpress" in title.lower() or "php" in title.lower() or "unity" in title.lower():
        reason.append("Irrelevant stack (WordPress/PHP/Unity)")
        
    if reason:
        skipped_jobs.append((idx, j, ", ".join(reason)))
    else:
        valid_fresher_jobs.append((idx, j))

print(f"Valid/Target candidate jobs: {len(valid_fresher_jobs)}")
print(f"Skipped jobs by rule: {len(skipped_jobs)}")

print("\n--- TOP 15 VALID JOBS ---")
for idx, j in valid_fresher_jobs[:15]:
    print(f"#{idx+1} [{j.get('company')}] {j.get('title')} ({j.get('experience')}) | ATS: {j.get('ats_domain')}")
    print(f"     URL: {j.get('company_site_url')}")
