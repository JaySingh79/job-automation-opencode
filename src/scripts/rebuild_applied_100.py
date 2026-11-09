"""Rebuild src/applied/jobs_applied.json (dict-by-platform) from surviving府 allowed sources + sidecars."""
import io
import json
import re
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
APPLIED_DIR = ROOT / "src" / "applied"
APPLIED = APPLIED_DIR / "jobs_applied.json"
PROGRESS_DIR = ROOT / "src" / "application_progress"

out = {}

def add_entry(e, source):
    if not isinstance(e, dict):
        return
    platform = e.get("platform") or e.get("key", "").split(":")[0] or "misc"
    url = e.get("url") or e.get("job_url") or e.get("link") or ""
    role = e.get("role") or e.get("title") or ""
    if not url or not role:
        return
    bucket = out.setdefault(str(platform).lower(), [])
    if not any(((x.get("url") or x.get("job_url") or "") == url) or (x.get("role") or x.get("title") or "") == role for x in bucket):
        e2 = dict(e)
        e2.setdefault("recovered_from", source)
        bucket.append(e2)

# 1. current partial file (list of 3)
try:
    cur = json.loads(APPLIED.read_text(encoding="utf-8"))
    if isinstance(cur, list):
        for e in cur:
            add_entry(e, "jobs_applied.json(partial-2026-10-17)")
    else:
        for plat, rows in cur.items():
            for e in (rows if isinstance(rows, list) else []):
                add_entry(e, "jobs_applied.json")
except Exception as ex:
    print("current-load fail:", ex)

# 2. sidecars
for f in sorted(APPLIED_DIR.glob("jobs_applied_batch*.json")):
    try:
        arr = json.loads(f.read_text(encoding="utf-8"))
        for e in (arr if isinstance(arr, list) else []):
            add_entry(e, f.name)
    except Exception as ex:
        print(f.name, ex)

# 3. ATS session progress files (status=applied rows)
URL_KEYS = ("url", "job_url", "link", "posting_url")
STATUS_KEYS = ("status", "state")
for f in sorted(PROGRESS_DIR.glob("*.json")):
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception as ex:
        print(f.name, "unparseable:", ex)
        continue
    rows = []
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, list):
                rows.extend(x for x in v if isinstance(x, dict))
    elif isinstance(d, list):
        rows = [x for x in d if isinstance(x, dict)]
    for row in rows:
        st = str((row.get("status") or row.get("state") or "")).lower()
        if "applied" in st or "submitted" in st:
            e = {
                "company": row.get("org") or row.get("company") or "",
                "role": row.get("title") or row.get("role") or "",
                "url": next((row[k] for k in URL_KEYS if k in row and row[k]), ""),
                "platform": row.get("platform") or "",
                "status": "applied",
                "applied_date": row.get("applied_date") or row.get("date") or str(f.name),
                "verification": "reconstructed from " + f.name,
            }
            add_entry(e, f"application_progress/{f.name}")

plats = {k: len(v) for k, v in sorted(out.items())}
print("recovered platforms:", json.dumps(plats, indent=0))
out["_recovery_note"] = [
    "jobs_applied.json was accidentally truncated on 2026-10-17 (merge script clobbered dict with list).",
    "Rebuilt from surviving allowed sources: batch sidecars, application_progress files, conversational memory of wave-0 entries.",
    "Pre-Sep/2026-10-14-era rows not present in surviving files are recorded in per-session progress JSONs only.",
    "Timestamp of rebuild: 2026-10-17.",
]
APPLIED.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print("WROTE:", APPLIED, "total rows:", sum(len(v) for k, v in out.items() if not k.startswith("_")))
