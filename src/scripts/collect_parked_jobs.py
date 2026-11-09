import json
import glob

def main():
    applied_ids = set()
    with open('src/applied/hirist_applied_2026-11-05.json', 'r', encoding='utf-8') as f:
        ledger = json.load(f)
        for j in ledger.get('applied', []):
            jid = str(j.get('job_id') or j.get('jobId') or j.get('id'))
            applied_ids.add(jid)

    applied_ids.add('1680685')
    applied_ids.add('1652792')

    parked_jobs = {}

    all_files = sorted(glob.glob('src/application_progress/hirist/hirist_progress_*.json'))
    for p in all_files:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                d = json.load(f)
                if isinstance(d, str):
                    d = json.loads(d)
                if not isinstance(d, dict):
                    continue
                
                for r in d.get('all_results', []):
                    if isinstance(r, dict) and r.get('status') == 'parked_assessment':
                        jid = str(r.get('id') or r.get('jobId') or r.get('job_id'))
                        if jid not in applied_ids and jid not in parked_jobs:
                            parked_jobs[jid] = {
                                "id": int(jid),
                                "title": r.get('title', 'Unknown Title'),
                                "company": r.get('company', 'Unknown Company')
                            }

                for jid in d.get('parked_job_ids', []):
                    sjid = str(jid)
                    if sjid not in applied_ids and sjid not in parked_jobs:
                        parked_jobs[sjid] = {
                            "id": int(sjid),
                            "title": "Unknown Title",
                            "company": "Unknown Company"
                        }
        except Exception as e:
            print(f"Error reading {p}: {e}")

    print(f"Total unique unapplied parked assessment jobs: {len(parked_jobs)}")
    
    with open('src/job_search_results/hirist/hirist_parked_assessments_pool_2026-11-05.json', 'w', encoding='utf-8') as f:
        json.dump(list(parked_jobs.values()), f, indent=2)
    print("Saved pool to src/job_search_results/hirist/hirist_parked_assessments_pool_2026-11-05.json")

if __name__ == '__main__':
    main()
