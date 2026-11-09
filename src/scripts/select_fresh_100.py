"""select_fresh_100.py — pick the strongest 100 from the 2026-10-17 harvest pool."""
import json
import re
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
POOL = ROOT / "src" / "job_search_results" / "2026-10-17-harvest-pool.json"
OUT = ROOT / "src" / "job_search_results" / "2026-10-17-fresh-100-final.json"

data = json.loads(POOL.read_text(encoding="utf-8"))
jobs = data["jobs"]

EXPLICIT_JUNIOR = re.compile(r"\b(intern|internship|trainee|graduate|grad|associate|junior|jr\.?|entry|fresher|i)\b", re.I)
GOOD_WORD = re.compile(r"\b(software|sde|backend|back-end|full\s?stack|full-stack|data|machine|learning|\bml\b|\bai\b|llm|engineer|developer|scientist|devops|platform|research)\b", re.I)


def score(j):
    s = 0.0
    if j.get("geo_tag") == "india":
        s += 3
    t = (j.get("title") or "")
    tl = t.lower()
    if EXPLICIT_JUNIOR.search(t):
        s += 2
    if re.search(r"\bsenior\b", tl):
        s -= 10
    if j.get("updated", "") >= "2026-10-01":
        s += 0.5
    return s


seen_org = {}
picked = []
for k, j in enumerate(sorted(jobs, key=score, reverse=True)):
    org = j["org"]
    if seen_org.get(org, 0) >= 4:
        continue
    seen_org[org] = seen_org.get(org, 0) + 1
    picked.append(j)

# cap at 100 with platform balance preference
out = picked[:100]
OUT.write_text(json.dumps({"date": "2026-10-17", "count": len(out), "jobs": out}, indent=1, ensure_ascii=False), encoding="utf-8")

from collections import Counter
print("FINAL COUNT:", len(out))
print("BY PLATFORM:", dict(Counter(j["platform"] for j in out)))
print("BY GEO:", dict(Counter(j["geo_tag"] for j in out)))
print("BY ORG (top):", dict(Counter(j["org"] for j in out).most_common(15)))
print("-" * 60)
for j in out[:120]:
    print(f'{j["platform"][0].upper():<1} | {(j["title"] or "")[:64]:<64} | {(j["location"] or "")[:44]:<44} | {j["org"][:22]:<22} | {j["url"][:80]}')
