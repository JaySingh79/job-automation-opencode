import json
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
SRC = ROOT / "src" / "job_search_results" / "2026-10-17-fresh-100-final.json"
OUT = ROOT / "src" / "job_search_results" / "2026-10-17-fresh-100-waves.json"
PROG = ROOT / "src" / "application_progress" / "2026-10-17-fresh-100-progress.json"

d = json.loads(SRC.read_text(encoding="utf-8"))
jobs = d["jobs"]

groups = {"greenhouse": [], "ashby": [], "lever": []}
for j in jobs:
    groups[j["platform"]].append(j)

# waves of ~10
waves = []
for platform, wl in [("greenhouse", [10, 10, 10, 8]), ("ashby", [10, 10, 10, 4]), ("lever", [10, 10, 8])]:
    it = iter(groups[platform])
    for n in wl:
        waves.append([])

# pack sequentially
wave_index = 0
cur_len = 0
sizes = {0: 10, 1: 10, 2: 10, 3: 8, 4: 10, 5: 10, 6: 10, 7: 4, 8: 10, 9: 10, 10: 8}
size_iter = iter(sizes.items())
wave_key, cur_size = next(size_iter)
waves_meta = []
rows_in = 0
wave_rows = []
wave_id = 0
for platform in ["greenhouse", "ashby", "lever"]:
    for j in groups[platform]:
        if cur_len >= cur_size:
            waves_meta.append({"wave": wave_id, "platform": platform, "jobs": wave_rows})
            wave_id += 1
            wave_rows = []
            cur_len = 0
            wave_key, cur_size = next(size_iter)
        j2 = dict(j)
        j2["wave"] = wave_id
        wave_rows.append(j2)
        cur_len += 1
        rows_in += 1
    if wave_rows:
        waves_meta.append({"wave": wave_id, "platform": platform, "jobs": wave_rows})
        wave_id += 1
        wave_rows = []
        cur_len = 0

OUT.write_text(json.dumps({"date": "2026-10-17", "total": rows_in, "waves": waves_meta}, indent=1, ensure_ascii=False), encoding="utf-8")

all_rows = []
for w in waves_meta:
    for j in w["jobs"]:
        all_rows.append({"key": j["key"], "title": j["title"], "org": j["org"], "url": j["url"], "wave": j["wave"], "status": "queued"})
prog = {"date": "2026-10-17", "total": rows_in,
        "summary": {"applied": 0, "skipped_expired": 0, "skipped_senior_or_mismatch": 0, "failed": 0},
        "jobs": all_rows}
PROG.write_text(json.dumps(prog, indent=1, ensure_ascii=False), encoding="utf-8")
PROG.write_text(json.dumps(prog, indent=1, ensure_ascii=False), encoding="utf-8")
print("WAVES:", [(w["wave"], w["platform"], len(w["jobs"])) for w in waves_meta])
print("PROGRESS FILE:", PROG, "rows:", len(prog["jobs"]))
