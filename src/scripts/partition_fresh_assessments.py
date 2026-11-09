import json
import os

with open('src/job_search_results/hirist/hirist_parked_assessments_pool_2026-11-05.json', 'r', encoding='utf-8') as f:
    pool = json.load(f)

with open('src/applied/hirist_applied_2026-11-05.json', 'r', encoding='utf-8') as f:
    ledger = json.load(f)
    applied_ids = {str(j.get('job_id') or j.get('id')) for j in ledger.get('applied', [])}

unapplied = [j for j in pool if str(j['id']) not in applied_ids]
print(f"Total unapplied jobs to partition: {len(unapplied)}")

os.makedirs('src/job_search_results/hirist/batches', exist_ok=True)

num_batches = 5
batch_size = (len(unapplied) + num_batches - 1) // num_batches

for i in range(num_batches):
    batch = unapplied[i*batch_size : (i+1)*batch_size]
    batch_file = f'src/job_search_results/hirist/batches/hirist_assessment_batch_{i+1}_2026-11-06.json'
    with open(batch_file, 'w', encoding='utf-8') as f:
        json.dump(batch, f, indent=2)
    print(f"Batch {i+1}: {len(batch)} jobs -> {batch_file}")
