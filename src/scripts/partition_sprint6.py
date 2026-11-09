import json
import os

with open('src/job_search_results/hirist/hirist_additional_200_harvest_2026-11-05.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    all_jobs = data['jobs']

sprint6_pool = all_jobs[395:425]  # 30 jobs
print(f"Total jobs for Sprint 6: {len(sprint6_pool)}")

os.makedirs('src/job_search_results/hirist/batches', exist_ok=True)

# 5 batches of 6 jobs each
batch_size = 6
for i in range(5):
    batch = sprint6_pool[i*batch_size : (i+1)*batch_size]
    batch_file = f'src/job_search_results/hirist/batches/hirist_additional_sprint6_batch_{i+1}_2026-11-05.json'
    with open(batch_file, 'w', encoding='utf-8') as f:
        json.dump(batch, f, indent=2)
    print(f"Created Batch {i+1}: {len(batch)} jobs -> {batch_file}")
