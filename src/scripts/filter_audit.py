"""
filter_audit.py — Identify and eliminate any L3+, test, dummy, or senior roles.
"""
import json
import re
from pathlib import Path

f_comb = Path("src/job_search_results/ashby_lever_greenhouse/2026-11-07-fresh-300-ashby-lever-greenhouse.json")
data = json.loads(f_comb.read_text(encoding="utf-8"))

flagged = []
for j in data["jobs"]:
    t = j["title"].lower()
    o = j["org"].lower()
    reasons = []
    if re.search(r"\b(l[3-9]|tier\s*[3-9]|level\s*[3-9]|sde\s*[3-9]|sde\s*[-_ ]?(?:iii|iv|v)|engineer\s*[-_ ]?(?:iii|iv|v))\b", t):
        reasons.append("L3+ level indicator")
    if re.search(r"\b(test|dummy|demo|staging|sample|kiran)\b", t):
        reasons.append("Test/Dummy posting")
    if reasons:
        flagged.append((j["platform"], j["org"], j["title"], reasons))

print(f"Total flagged out of 300: {len(flagged)}")
for p, org, t, reasons in flagged:
    print(f"  [{p}] {org}: '{t}' -> {', '.join(reasons)}")
