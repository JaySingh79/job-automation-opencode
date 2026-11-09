import json
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
PROG = ROOT / "src" / "application_progress" / "2026-10-17-fresh-100-progress.json"

d = json.loads(PROG.read_text(encoding="utf-8"))
jobs = d.get("jobs", d if isinstance(d, list) else [])
hit = 0
for row in jobs:
    k = row.get("key", "")
    if "gitlab" in k and "8775507002" in k:
        old = row.get("status")
        row["status"] = "applied"
        row["why"] = "submitted during wave-0 run before user-cancel; /confirmation 'Thank you for applying' verified 2026-10-17"
        if old != "applied":
            d.setdefault("summary", {})
            s = d.get("summary")
            s["applied"] = s.get("applied", 0) + 1
            for kk in list(s):
                if old in kk and s[kk] > 0:
                    s[kk] -= 1
        hit += 1
    elif "gitlab" in k:
        row.setdefault("detail", "")
        row["detail"] = (str(row.get("detail", "")) + " [2026-10-17] never submitted (~80% filled then user-cancelled); file 战 not submitted").strip()
        hit += 1
# fix accidental mojibake word if any
for row in jobs:
    for key in ("detail", "why", "reason"):
        v = row.get(key)
        if isinstance(v, str):
            row[key] = v.replace("file 战 not submitted", "file; not submitted")
d.setdefault("summary", {})
json.dump(d, PROG.open("w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("rows hit:", hit, "summary:", d.get("summary"))

side = ROOT / "src" / "applied" / "jobs_applied_batchR1_gitlab.json"
side.write_text(json.dumps([{
    "company": "GitLab",
    "role": "Site Reliability Engineer - Cells Infrastructure",
    "url": "https://boarding.gitlab.io/-/jobs/8775507002",
    "jobid": "8775507002",
    "platform": "greenhouse",
    "status": "applied",
    "date": "2026-10-17",
    "note": "Submitted during wave-0 run pre-cancel; /confirmation verified 2026-10-17 on live tab snapshot"
}], indent=1, ensure_ascii=False), encoding="utf-8")
print("sidecar written:", side)
