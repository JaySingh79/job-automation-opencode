import json
import random

with open('src/job_search_results/hirist/hirist_parked_assessments_pool_2026-11-05.json', 'r', encoding='utf-8') as f:
    pool = json.load(f)

with open('src/applied/hirist_applied_2026-11-05.json', 'r', encoding='utf-8') as f:
    ledger = json.load(f)
    app_ids = {str(j.get('job_id') or j.get('id')) for j in ledger.get('applied', [])}

unapp = [j for j in pool if str(j['id']) not in app_ids]
print(f"Total unapplied in pool: {len(unapp)}")

random.seed(42)
sample = random.sample(unapp, 5)
with open('src/job_search_results/hirist/test_5_sample.json', 'w', encoding='utf-8') as f:
    json.dump(sample, f, indent=2)

for i, j in enumerate(sample):
    print(f"{i+1}. ID={j['id']} | {j['title']} ({j['company']})")
