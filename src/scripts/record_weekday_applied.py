import os
import re
import json
from datetime import datetime

APPLIED_PATH = os.path.join("src", "applied", "weekday.json")
PROGRESS_PATH = os.path.join("src", "application_progress", "weekday", "weekday_progress.json")
STEP_OUTPUT_PATH = r"C:/Users/binit/.gemini/antigravity-cli/brain/aefd17d8-3f98-4b80-a8ec-42c6e96da24d/.system_generated/steps/214/output.txt"

def main():
    os.makedirs(os.path.dirname(APPLIED_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(PROGRESS_PATH), exist_ok=True)

    existing_applied = []
    if os.path.exists(APPLIED_PATH):
        try:
            with open(APPLIED_PATH, "r", encoding="utf-8") as f:
                existing_applied = json.load(f)
        except Exception:
            existing_applied = []

    existing_ids = {x.get("job_id") for x in existing_applied}

    with open(STEP_OUTPUT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # The output is formatted as: ### Result \n "[\n  { ... }\n]"
    lines = content.splitlines()
    json_lines = []
    capture = False
    for line in lines:
        if line.startswith('### Result'):
            capture = True
            continue
        if capture and line.startswith('### Ran Playwright code'):
            break
        if capture:
            json_lines.append(line)

    raw_json_str = "\n".join(json_lines).strip()
    # If wrapped in quotes
    if raw_json_str.startswith('"') and raw_json_str.endswith('"'):
        # Decode json string literal
        inner = json.loads(raw_json_str)
        items = json.loads(inner)
    else:
        items = json.loads(raw_json_str)

    new_applied = 0
    for it in items:
        if it.get("status") in ["applied", "submitted_unconfirmed"]:
            if it.get("job_id") not in existing_ids:
                existing_applied.append({
                    "job_id": it["job_id"],
                    "title": it["title"],
                    "company": it["company"],
                    "url": it["url"],
                    "applied_at": it.get("timestamp") or datetime.now().isoformat(),
                    "status": it["status"],
                    "details": it.get("details"),
                    "worker": it.get("worker")
                })
                existing_ids.add(it["job_id"])
                new_applied += 1

    with open(APPLIED_PATH, "w", encoding="utf-8") as f:
        json.dump(existing_applied, f, indent=2)

    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "last_sprint": datetime.now().isoformat(),
            "total_applied": len(existing_applied),
            "sprint_results": items
        }, f, indent=2)

    print(f"[+] Successfully recorded {new_applied} new applications!")
    print(f"[+] Total applications in persistent ledger {APPLIED_PATH}: {len(existing_applied)}")

if __name__ == "__main__":
    main()
