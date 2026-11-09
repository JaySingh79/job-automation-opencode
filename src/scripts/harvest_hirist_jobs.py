"""
Harvest all AI/ML jobs from Hirist matching the 0-3 yrs query URL across all pages.
Saves structured job listings to src/job_search_results/hirist/
"""

import os
import sys
import json
import time
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone

def slugify(text: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', text).strip('-').lower()
    return slug

def harvest_hirist_jobs(category_id: int = 14, min_exp: int = 0, max_exp: int = 3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.hirist.tech/',
    }

    page = 0
    size = 20
    all_jobs = []
    seen_ids = set()

    print(f"Starting Hirist harvest for Category={category_id}, min_exp={min_exp}, max_exp={max_exp}...")

    total_pages = 1
    while page < total_pages:
        url = f"https://gladiator.hirist.tech/job/category/?minexp={min_exp}&maxexp={max_exp}&categoryId={category_id}&page={page}&size={size}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as res:
                data = json.loads(res.read().decode('utf-8'))
                
                total_jobs = data.get('totalJobs', 0)
                total_pages = data.get('totalPages', total_pages)
                has_more = data.get('hasMore', True)
                job_list = data.get('data', [])

                if not job_list:
                    print(f"Page {page}: No jobs returned. Ending pagination.")
                    break

                for j in job_list:
                    jid = j.get('id')
                    if not jid or jid in seen_ids:
                        continue
                    seen_ids.add(jid)

                    title = j.get('title', '')
                    company = j.get('companyData', {}).get('companyName', '') or j.get('company', '')
                    min_e = j.get('min', 0)
                    max_e = j.get('max', 0)
                    locations = [loc.get('name') for loc in j.get('locations', []) if loc.get('name')]
                    loc_str = " | ".join(locations) if locations else "India"
                    tags = [t.get('name') for t in j.get('tags', []) if t.get('name')]
                    
                    slug = slugify(f"{company} {title}" if company and company.lower() not in title.lower() else title)
                    canonical_url = f"https://www.hirist.tech/j/{slug}-{jid}?ref=cl_br"
                    
                    job_obj = {
                        "id": jid,
                        "title": title,
                        "company": company,
                        "min": min_e,
                        "max": max_e,
                        "exp": f"{min_e}-{max_e} yrs",
                        "location": loc_str,
                        "tags": tags,
                        "url": canonical_url,
                        "status": "pending",
                        "applied": j.get('applied', False),
                        "createdTime": j.get('createdTime'),
                    }
                    all_jobs.append(job_obj)

                print(f"Harvested Page {page + 1}/{total_pages} (Jobs on page: {len(job_list)}, Total cumulative: {len(all_jobs)})")
                page += 1
                time.sleep(0.3)

                if not has_more:
                    break

        except urllib.error.HTTPError as e:
            print(f"HTTP Error on page {page}: {e.code} {e.reason}")
            time.sleep(1.0)
            page += 1
        except Exception as e:
            print(f"Error on page {page}: {e}")
            time.sleep(1.0)
            page += 1

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir = os.path.join("src", "job_search_results", "hirist")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"hirist_ai_ml_0-3yrs_{date_str}.json")

    # Filter according to user instruction: 0-3 yrs range
    # Hirist API returns overlapping ranges, so we filter to jobs where min <= 3
    filtered_jobs = [j for j in all_jobs if j.get("min", 0) <= 3]

    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "source": f"https://www.hirist.tech/c/ai-ml-jobs?minexp={min_exp}&maxexp={max_exp}",
        "category_id": category_id,
        "total_harvested": len(all_jobs),
        "total_filtered_0_to_3yrs": len(filtered_jobs),
        "jobs": filtered_jobs
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"\n[DONE] Successfully saved {len(filtered_jobs)} jobs to {out_file}")
    return out_file, len(filtered_jobs)

if __name__ == "__main__":
    harvest_hirist_jobs()
