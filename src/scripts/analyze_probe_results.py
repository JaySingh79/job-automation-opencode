"""
analyze_probe_results.py — Deduplicate against applied records and analyze counts.
"""
import json
import re
from pathlib import Path
from collections import Counter

# Run the probe and gather details
import sys
sys.path.append(r"D:\Projects\PRACTICE\firecrawl_test\src\scripts")
from test_board_apis import main as probe_main, probe_lever, probe_ashby, probe_greenhouse, loc_verdict, title_verdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. Load applied URLs/keys
applied_urls = set()
for f in [Path('jobs_applied.json'), Path('src/applied/jobs_applied.json'), Path('src/applied/ashby.json'), Path('src/applied/lever.json'), Path('src/applied/greenhouse.json')]:
    if f.exists():
        try:
            data = json.loads(f.read_text(encoding='utf-8', errors='replace'))
            if isinstance(data, list):
                for item in data:
                    u = item.get('url') or item.get('job_url')
                    if u: applied_urls.add(u.strip().lower().rstrip('/'))
            elif isinstance(data, dict):
                for k, v in data.items():
                    applied_urls.add(k.strip().lower().rstrip('/'))
                    if isinstance(v, dict) and v.get('url'):
                        applied_urls.add(v['url'].strip().lower().rstrip('/'))
        except Exception:
            pass

p_audit = Path('src/application_progress/ashby_lever_greenhouse/2026-11-06-200-submit-audit.jsonl')
if p_audit.exists():
    for line in p_audit.read_text(encoding='utf-8', errors='replace').splitlines():
        if line.strip():
            try:
                row = json.loads(line)
                u = row.get('url')
                if u: applied_urls.add(u.strip().lower().rstrip('/'))
            except Exception:
                pass

print(f"Loaded {len(applied_urls)} applied/attempted URLs to exclude.")

# Gather orgs
lever_orgs = set()
ashby_orgs = set()
gh_orgs = set()
for p in Path("src/job_search_results").rglob("*.json"):
    try:
        content = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"https?://(?:jobs\.)?lever\.co/([A-Za-z0-9_.-]+)", content, re.I):
            s = m.group(1).lower().strip("/")
            if s not in ("v0", "search", "apply", "postings"): lever_orgs.add(s)
        for m in re.finditer(r"https?://jobs\.ashbyhq\.com/([A-Za-z0-9_.-]+)", content, re.I):
            s = m.group(1).lower().strip("/")
            if s not in ("api", "posting-api", "job-board"): ashby_orgs.add(s)
        for m in re.finditer(r"https?://(?:job-boards\.|boards\.)?greenhouse\.io/([A-Za-z0-9_-]+)", content, re.I):
            s = m.group(1).lower().strip("/")
            if s not in ("v1", "boards", "embed", "api", "jobs"): gh_orgs.add(s)
    except Exception:
        pass

all_jobs = []
with ThreadPoolExecutor(max_workers=20) as ex:
    futs = []
    for org in lever_orgs:
        futs.append(ex.submit(probe_lever, org))
    for org in ashby_orgs:
        futs.append(ex.submit(probe_ashby, org))
    for org in gh_orgs:
        futs.append(ex.submit(probe_greenhouse, org))

    for f in as_completed(futs):
        res = f.result()
        if res:
            all_jobs.extend(res)

print(f"Raw live jobs fetched: {len(all_jobs)}")

# Filter out applied URLs
fresh_jobs = []
for j in all_jobs:
    u = j['url'].strip().lower().rstrip('/')
    if u in applied_urls:
        continue
    # Normalize comparison key
    fresh_jobs.append(j)

print(f"Fresh unapplied live jobs: {len(fresh_jobs)}")
c = Counter(j["platform"] for j in fresh_jobs)
print(f"Fresh unapplied by platform: {dict(c)}")

# Check role distribution
role_types = Counter()
for j in fresh_jobs:
    t = j['title'].lower()
    if 'machine learning' in t or 'ml' in t or 'computer vision' in t or 'deep learning' in t:
        role_types['ML / Vision'] += 1
    elif 'ai' in t or 'llm' in t or 'genai' in t:
        role_types['GenAI / LLM / AI'] += 1
    elif 'data' in t:
        role_types['Data Science / Analytics'] += 1
    elif 'software' in t or 'sde' in t or 'developer' in t or 'backend' in t or 'python' in t:
        role_types['SDE / Backend / SWE'] += 1
    else:
        role_types['Other Technical'] += 1

print(f"Role distribution: {dict(role_types)}")
