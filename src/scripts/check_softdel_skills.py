import json
from pathlib import Path

BATCH_FILE = Path(r"src/job_search_results/naukri/direct_company_platforms/batch_bigtech_custom.json")
with open(BATCH_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for j in data["jobs"]:
    if "softdel" in j.get("company", "").lower():
        print(j.get("title"))
        print(j.get("skills"))
        print(j.get("experience"))
