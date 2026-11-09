import sys
import os
import json
from datetime import datetime

applied_file = 'src/applied/naukri.json'
progress_file = 'src/application_progress/naukri/naukri_progress.json'

os.makedirs('src/applied', exist_ok=True)
os.makedirs('src/application_progress/naukri', exist_ok=True)

def record(job_id, title, company, status, verification):
    applied = []
    if os.path.exists(applied_file):
        try:
            with open(applied_file, 'r', encoding='utf-8') as f:
                applied = json.load(f)
        except Exception:
            applied = []

    record = {
        'job_id': str(job_id),
        'title': title,
        'company': company,
        'applied_at': datetime.now().isoformat(),
        'status': status,
        'verification': verification
    }

    if not any(str(x.get('job_id')) == str(job_id) for x in applied):
        applied.append(record)

    with open(applied_file, 'w', encoding='utf-8') as f:
        json.dump(applied, f, indent=2)

    progress_data = {'last_updated': datetime.now().isoformat(), 'jobs': applied}
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, indent=2)
    print(f"Recorded: [{job_id}] {title} @ {company} -> {status}")

if __name__ == '__main__':
    if len(sys.argv) >= 6:
        record(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        