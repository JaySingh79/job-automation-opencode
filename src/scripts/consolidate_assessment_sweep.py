import json
import glob

def main():
    ledger_path = 'src/applied/hirist_applied_2026-11-05.json'
    with open(ledger_path, 'r', encoding='utf-8') as f:
        ledger = json.load(f)

    existing = ledger.get('applied', [])
    seen_ids = set()
    for j in existing:
        jid = str(j.get('job_id') or j.get('jobId') or j.get('id'))
        seen_ids.add(jid)

    print(f"Existing in ledger: {len(existing)}")

    # Collect from all 5 assessment progress files
    progress_files = sorted(glob.glob('src/application_progress/hirist/hirist_progress_assessment_batch_*.json'))
    added = 0

    for p in progress_files:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                d = json.load(f)
                
                # Check results or jobs
                items = d.get('results', []) or d.get('jobs', [])
                if not items and 'applied_jobs' in d:
                    items = d['applied_jobs']

                for item in items:
                    jid = str(item.get('id') or item.get('job_id') or item.get('jobId'))
                    status = item.get('status', 'applied')
                    if jid and jid != 'None' and status in ['applied', 'already_applied']:
                        if jid not in seen_ids:
                            seen_ids.add(jid)
                            rec = {
                                "job_id": int(jid),
                                "title": item.get('title', 'Unknown Title'),
                                "company": item.get('company', 'Unknown Company'),
                                "applied_at": "2026-11-06T11:00:00Z",
                                "flow": "screening_assessment_completed"
                            }
                            existing.append(rec)
                            added += 1
        except Exception as e:
            print(f"Error reading {p}: {e}")

    print(f"Added {added} newly applied assessment jobs to master ledger.")
    print(f"Total applications now in master ledger: {len(existing)}")

    ledger['applied'] = existing
    ledger['total_applied'] = len(existing)
    ledger['assessment_sweep_applied_2026-11-06'] = added

    with open(ledger_path, 'w', encoding='utf-8') as f:
        json.dump(ledger, f, indent=2)

    print(f"Updated {ledger_path} successfully.")

if __name__ == '__main__':
    main()
