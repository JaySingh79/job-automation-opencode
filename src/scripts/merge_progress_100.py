import json
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
PROG_DIR = ROOT / "src" / "application_progress"
APPLIED_DIR = ROOT / "src" / "applied"
PROG = PROG_DIR / "2026-10-17-fresh-100-progress.json"
APPLIED = APPLIED_DIR / "jobs_applied.json"
BATCH = __import__("sys").argv[1] if len(__import__("sys").argv) > 1 else "A"

by = {}
for f in sorted(PROG_DIR.glob(f"batch*_job*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    if d.get("status") in ("applied", "skipped_expired", "skipped_senior_or_mismatch", "failed", "skipped_user_skip"):
        by[d["key"]] = d
        print("merge:", f.name, "->", d["status"])

p = json.loads(PROG.read_text(encoding="utf-8"))
for r in p["jobs"]:
    d = by.get(r["key"])
    if d:
        r["status"] = d["status"]
        r["reason"] = d.get("reason", "")
        r["datetime"] = d.get("datetime", "")
json.dump(p, PROG.open("w", encoding="utf-8"), indent=1, ensure_ascii=False)
c = {}
for r in p["jobs"]:
    c[r["status"]] = c.get(r["status"], 0) + 1
print("summary:", c)

apd = json.loads(APPLIED.read_text(encoding="utf-8"))
changed = 0
for f in sorted(APPLIED_DIR.glob(f"jobs_applied_batch{BATCH}*.json")):
    arr = json.loads(f.read_text(encoding="utf-8"))
    for e in arr:
        platform = str(e.get("platform") or "misc").lower()
        url = e.get("url") or e.get("job_url") or ""
        role = e.get("role") or e.get("title") or ""
        if isinstance(apd, dict):
            bucket = apd.setdefault(platform, [])
            if not any(((x.get("url") or x.get("job_url") or "") == url) or (x.get("role") or x.get("title") or "") == role for x in bucket):
                bucket.append(e)
                changed += 1
        elif isinstance(apd, list):
            if not any(((x.get("url") or x.get("job_url") or "") == url) for x in apd):
                apd.append(e)
                changed += 1
print("applied appended:", changed, "total:", sum(len(v) for k, v in apd.items()) if isinstance(apd, dict) else len(apd))
json.dump(apd, APPLIED.open("w", encoding="utf-8"), indent=1, ensure_ascii=False)
