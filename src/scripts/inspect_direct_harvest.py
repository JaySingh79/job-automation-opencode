"""
inspect_direct_harvest.py — Process direct URLs discovered by Firecrawl.
"""
import json
import re
from pathlib import Path

OUT_DIR = Path("src/job_search_results/ashby_lever_greenhouse")
gh_jobs = json.loads((OUT_DIR / "temp_fresh_gh.json").read_text(encoding="utf-8"))
ashby_jobs = json.loads((OUT_DIR / "temp_fresh_ashby.json").read_text(encoding="utf-8"))
lever_jobs = json.loads((OUT_DIR / "temp_fresh_lever.json").read_text(encoding="utf-8"))

print(f"Existing Verified Board API Jobs (posted >= 2026-10-01):")
print(f"  Greenhouse: {len(gh_jobs)}")
print(f"  Ashby:      {len(ashby_jobs)}")
print(f"  Lever:      {len(lever_jobs)}")
