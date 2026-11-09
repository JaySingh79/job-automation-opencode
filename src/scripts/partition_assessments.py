import json
import os

with open('src/job_search_results/hirist/hirist_parked_assessments_pool_2026-11-05.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

print(f"Total jobs to partition: {len(jobs)}")

os.makedirs('src/job_search_results/hirist/batches', exist_ok=True)

# 5 batches
num_batches = 5
batch_size = (len(jobs) + num_batches - 1) // num_batches

for i in range(num_batches):
    batch = jobs[i*batch_size : (i+1)*batch_size]
    batch_file = f'src/job_search_results/hirist/batches/hirist_assessment_batch_{i+1}_2026-11-05.json'
    with open(batch_file, 'w', encoding='utf-8') as f:
        json.dump(batch, f, indent=2)
    print(f"Batch {i+1}: {len(batch)} jobs -> {batch_file}")
