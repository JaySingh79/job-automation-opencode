import json
import os
import sys

def main():
    json_path = os.path.join("src", "job_search_results", "naukri", "direct_company_platforms", "batch_phenom_radancy.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"Total jobs: {len(data['jobs'])}")
    for i, j in enumerate(data['jobs']):
        print(f"{i+1:02d}. [{j['company']}] {j['title']} (Exp: {j.get('experience')}) - {j['company_site_url']}")

if __name__ == "__main__":
    main()
