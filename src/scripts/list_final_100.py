import json
from pathlib import Path
p = Path(r"D:\Projects\PRACTICE\firecrawl_test\src\job_search_results\2026-10-17-fresh-100-final.json")
d = json.loads(p.read_text(encoding="utf-8"))
for i, j in enumerate(d["jobs"], 1):
    if i > 90:
        print(f"{i:>3} {j['platform'][0].upper()} {j['org'][:22]:<22} {(j['title'] or '')[:54]:<54} {(j['location'] or '')[:32]:<32} | {j['url'][-58:]}")
