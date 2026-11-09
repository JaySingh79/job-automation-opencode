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
    applied_ids = set()
    with open('src/applied/hirist_applied_2026-11-05.json', 'r', encoding='utf-8') as f:
        base = json.load(f)
        print(f"Baseline in ledger (Sprints 1-3): {len(base['applied'])}")
        for j in base['applied']:
            jid = str(j.get('job_id') or j.get('jobId') or j.get('id'))
            applied_ids.add(jid)

    sprint4_files = sorted(glob.glob('src/application_progress/hirist/hirist_progress_additional_batch_*_2026-11-05.json'))
    s4_applied = []
    for p in sprint4_files:
        with open(p, 'r', encoding='utf-8') as f:
            d = json.load(f)
            items = extract_applied(d)
            for j in items:
                jid = str(j.get('job_id') or j.get('jobId') or j.get('id'))
                if jid not in applied_ids:
                    applied_ids.add(jid)
                    s4_applied.append(j)

    print(f"Sprint 4 unique additional applied: {len(s4_applied)}")

    sprint5_files = sorted(glob.glob('src/application_progress/hirist/hirist_progress_additional_sprint5_batch_*_2026-11-05.json'))
    s5_applied = []
    for p in sprint5_files:
        with open(p, 'r', encoding='utf-8') as f:
            d = json.load(f)
            items = extract_applied(d)
            for j in items:
                jid = str(j.get('job_id') or j.get('jobId') or j.get('id'))
                if jid not in applied_ids:
                    applied_ids.add(jid)
                    s5_applied.append(j)

    print(f"Sprint 5 unique additional applied: {len(s5_applied)}")

    sprint6_files = sorted(glob.glob('src/application_progress/hirist/hirist_progress_additional_sprint6_batch_*_2026-11-05.json'))
    s6_applied = []
    for p in sprint6_files:
        with open(p, 'r', encoding='utf-8') as f:
            d = json.load(f)
            items = extract_applied(d)
            for j in items:
                jid = str(j.get('job_id') or j.get('jobId') or j.get('id'))
                if jid not in applied_ids:
                    applied_ids.add(jid)
                    s6_applied.append(j)

    print(f"Sprint 6 unique additional applied: {len(s6_applied)}")

    total_additional = len(s4_applied) + len(s5_applied) + len(s6_applied)
    print(f"Total additional applied: {total_additional}")
    print(f"Total cumulative applied today: {len(base['applied']) + total_additional}")
    print(f"Target met: {total_additional >= 200} (Surplus: {total_additional - 200})")

if __name__ == '__main__':
    main()
