"""
check_roman_and_levels.py
"""
import json
import re
from pathlib import Path

f_comb = Path("src/job_search_results/ashby_lever_greenhouse/2026-11-07-fresh-300-ashby-lever-greenhouse.json")
data = json.loads(f_comb.read_text(encoding="utf-8"))

flagged = []
for j in data["jobs"]:
    t = j["title"]
    # Check for III, IV, V, L3, L4, L5, Senior, Lead
    if re.search(r"\b(iii|iv|v|3|4|5)\b", t, re.I):
        # We need to distinguish between 'Python 3' or 'SDE 1' vs 'Engineer III', 'Level 4', etc.
        if re.search(r"(?:engineer|developer|scientist|sde|analyst|associate)\s*[-_ ]*(?:[3-9]|iii|iv|v)\b", t, re.I):
            flagged.append((j["platform"], j["org"], t, "Level 3+ designation"))
        elif re.search(r"\b(?:iii|iv|v)\b", t, re.I):
            flagged.append((j["platform"], j["org"], t, "Roman numeral III+"))
        elif re.search(r"\b(?:tier\s*[3-9]|level\s*[3-9]|l[3-9])\b", t, re.I):
            flagged.append((j["platform"], j["org"], t, "Tier/Level 3+"))

print(f"Flagged level 3+ items: {len(flagged)}")
for p, o, t, r in flagged:
    print(f"  [{p}] {o}: '{t}' -> {r}")
