#!/usr/bin/env python3
"""Targeted search for Staff, Principal, and EM in AI/Data across 5 Indian startups."""

import json
import re
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.scripts.serpapi_search import run_search

targets = [
    ("Zepto", 'site:in.linkedin.com/in/ Zepto "Engineering Manager" OR "Staff" OR "Principal" "Machine Learning" OR "Data"'),
    ("CRED", 'site:in.linkedin.com/in/ CRED "Engineering Manager" OR "Staff" OR "Principal" "Machine Learning" OR "Data"'),
    ("Darwinbox", 'site:in.linkedin.com/in/ Darwinbox "Engineering Manager" OR "Staff" OR "Principal" "AI" OR "Data"'),
    ("Ather Energy", 'site:in.linkedin.com/in/ "Ather Energy" "Engineering Manager" OR "Principal" OR "Staff" "Data" OR "AI"'),
    ("Moneyview", 'site:in.linkedin.com/in/ Moneyview "Engineering Manager" OR "Principal" OR "Staff" "Data" OR "AI"'),
]

candidates = []

for company, query in targets:
    print(f"[*] Querying for {company}...")
    res_str = run_search(query, num_pages=1, gl="in", hl="en")
    try:
        data = json.loads(res_str)
        items = data.get("response", [])
        for item in items:
            title = item.get("title", "")
            link = item.get("link", "")
            # Extract clean name from LinkedIn title: "Name - Title - Company | LinkedIn"
            name = title.split("-")[0].split("|")[0].split("–")[0].strip()
            # Filter out non-people titles (e.g. "Top 20 Engineering Manager...", "Jobs at...")
            if not name or "Jobs" in name or "Top " in name or len(name.split()) > 4:
                continue
            candidates.append({
                "company": company,
                "name": name,
                "linkedin_title": title,
                "linkedin_url": link,
                "snippet": item.get("snippet", "")
            })
    except Exception as e:
        print(f"[-] Error parsing: {e}")

print(f"\n[*] Filtered {len(candidates)} real candidates across the 5 companies.")
Path("src/job_search_results/targeted_10_ai_leads.json").write_text(json.dumps(candidates, indent=2), encoding="utf-8")
for idx, c in enumerate(candidates[:15], 1):
    print(f"{idx}. {c['name']} @ {c['company']} -> {c['linkedin_url']}")
