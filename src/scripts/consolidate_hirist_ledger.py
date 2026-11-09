import json
import glob

def extract_applied(data):
    applied = []
    if "applied_jobs" in data and len(data["applied_jobs"]) > 0:
        for j in data["applied_jobs"]:
            applied.append(j)
    elif "all_results" in data:
        for r in data["all_results"]:
            if r.get("status") == "applied":
                applied.append(r)
    return applied

def main():
    ledger_path = 'src/applied/hirist_applied_2026-11-05.json'
    with open(ledger_path, 'r', encoding='utf-8') as f:
        ledger = json.load(f)

    existing_applied = ledger.get('applied', [])
    seen_ids = set()
    for j in existing_applied:
        jid = str(j.get('job_id') or j.get('jobId') or j.get('id'))
        seen_ids.add(jid)

    print(f"Existing in ledger: {len(existing_applied)}")

    # Add Sprints 4, 5, 6
    sprint_files = sorted(glob.glob('src/application_progress/hirist/hirist_progress_additional_*_2026-11-05.json'))
    added = 0
    for p in sprint_files:
        with open(p, 'r', encoding='utf-8') as f:
            d = json.load(f)
            items = extract_applied(d)
            for j in items:
                jid = str(j.get('job_id') or j.get('jobId') or j.get('id'))
                if jid not in seen_ids:
                    seen_ids.add(jid)
                    # Normalize record structure
                    rec = {
                        "job_id": int(jid),
                        "application_id": j.get('applicationId') or j.get('application_id'),
                        "title": j.get('title', 'Unknown Title'),
                        "company": j.get('company', 'Unknown Company'),
                        "applied_at": j.get('appliedAt') or j.get('applied_at') or "2026-11-05T18:45:00Z"
                    }
                    existing_applied.append(rec)
                    added += 1

    print(f"Added {added} new unique applications to ledger.")
    print(f"New total in ledger: {len(existing_applied)}")

    ledger['applied'] = existing_applied
    ledger['total_applied'] = len(existing_applied)
    ledger['additional_applied_sprints_4_to_6'] = added

    with open(ledger_path, 'w', encoding='utf-8') as f:
        json.dump(ledger, f, indent=2)

    print(f"Updated {ledger_path} successfully.")

if __name__ == '__main__':
    main()
