import json
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
INPUT_FILE = ROOT / "src" / "job_search_results" / "naukri" / "direct_company_platforms" / "custom_company_careers.json"
OUT_DIR = ROOT / "src" / "job_search_results" / "naukri" / "direct_company_platforms"

data = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
jobs = data.get("jobs", [])

batch_bigtech = []
batch_phenom = []
batch_successfactors = []

# Domain classification sets
PHENOM_RADANCY_DOMAINS = {
    "search.jobs.barclays",
    "careers.synopsys.com",
    "career.crisil.com",
    "careers.moodys.com",
    "careers.amd.com",
    "careers.insight.com",
    "higher.gs.com",
    "jobsearch.harman.com",
    "careers.ralphlauren.com",
    "careers.infor.com"
}

SUCCESSFACTORS_HRCLOUD_DOMAINS = {
    "careers.ey.com",
    "careers.payu.in",
    "careers-akasa.peoplestrong.com",
    "avataarcareers.turbohire.co",
    "career.hrone.cloud",
    "myjobs.adp.com",
    "mandsc.applytojob.com",
    "jobs.micro1.ai",
    "jobs.reczee.com",
    "talents.electrifex.com",
    "career.utplindia.in",
    "careers.medpace.com",
    "careers.newtonschool.co"
}

for j in jobs:
    domain = j.get("ats_domain", "").lower()
    co = j.get("company", "").lower()

    if domain in PHENOM_RADANCY_DOMAINS or "barclays" in co or "synopsys" in co or "crisil" in co:
        batch_phenom.append(j)
    elif domain in SUCCESSFACTORS_HRCLOUD_DOMAINS or "ey" == co or "payu" in co or "peoplestrong" in domain or "turbohire" in domain:
        batch_successfactors.append(j)
    else:
        batch_bigtech.append(j)

print(f"Total input jobs: {len(jobs)}")
print(f"Batch 1 (BigTech & Bespoke): {len(batch_bigtech)}")
print(f"Batch 2 (Phenom & Radancy): {len(batch_phenom)}")
print(f"Batch 3 (SuccessFactors & HR Cloud): {len(batch_successfactors)}")

out1 = OUT_DIR / "batch_bigtech_custom.json"
out2 = OUT_DIR / "batch_phenom_radancy.json"
out3 = OUT_DIR / "batch_successfactors_cloud.json"

out1.write_text(json.dumps({"batch": "bigtech_custom", "total_jobs": len(batch_bigtech), "jobs": batch_bigtech}, indent=2), encoding="utf-8")
out2.write_text(json.dumps({"batch": "phenom_radancy", "total_jobs": len(batch_phenom), "jobs": batch_phenom}, indent=2), encoding="utf-8")
out3.write_text(json.dumps({"batch": "successfactors_cloud", "total_jobs": len(batch_successfactors), "jobs": batch_successfactors}, indent=2), encoding="utf-8")

print("Batches written successfully!")
