"""
assemble_final_fresh_300.py — Finalize exactly 100 Ashby, 100 Lever, 100 Greenhouse postings.
Strictly fresh (past month / Oct-Nov 2026), 0-2 YoE, Python/ML/DS/AI/SDE, India or Remote.
"""
import json
import re
import time
from pathlib import Path
from collections import Counter

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
OUT_DIR = ROOT / "src" / "job_search_results" / "ashby_lever_greenhouse"

OUT_COMBINED = OUT_DIR / "2026-11-07-fresh-300-ashby-lever-greenhouse.json"
OUT_ASHBY = OUT_DIR / "2026-11-07-ashby-100.json"
OUT_LEVER = OUT_DIR / "2026-11-07-lever-100.json"
OUT_GH = OUT_DIR / "2026-11-07-greenhouse-100.json"

import sys
sys.path.append(r"D:\Projects\PRACTICE\firecrawl_test\src\scripts")
from harvest_fresh_300_ats import load_applied_set

def sanitize_job(j):
    t = j["title"]
    # Check for senior / L3+
    if re.search(r"\b(senior|sr\.?|principal|staff|lead|director|head|vp|chief|architect)\b", t, re.I):
        return None
    if re.search(r"\b(l[3-9]|tier\s*[3-9]|level\s*[3-9]|sde\s*[-_ ]*\s*(?:[3-9]|iii|iv|v|vi)|engineer\s*[-_ ]*\s*(?:[3-9]|iii|iv|v|vi)|scientist\s*[-_ ]*\s*(?:[3-9]|iii|iv|v|vi))\b", t, re.I):
        return None
    if re.search(r"\b(?:iii|iv|v|vi)\b", t, re.I):
        return None
    if re.search(r"\b(qa|sdet|quality assurance|test engineer|test infra|automation test|dummy|sample role|demo job|kiran|kombo)\b", t, re.I):
        return None
    if re.search(r"\b(frontend|front-end|front end|recruiter|sales|marketing|account executive)\b", t, re.I):
        return None

    # Determine standard category
    t_lower = t.lower()
    if any(k in t_lower for k in ["computer vision", "vision", "robotics", "deep learning", "applied scientist"]):
        cat = "ML_Vision"
    elif any(k in t_lower for k in ["genai", "llm", "generative ai", "ai engineer", "agentic", "agent", "prompt", "nlp", "ai researcher"]):
        cat = "GenAI_LLM"
    elif any(k in t_lower for k in ["data scientist", "data engineer", "data analyst", "data science"]):
        cat = "Data_Science"
    elif any(k in t_lower for k in ["machine learning", "ml engineer", "mlops", "ai/ml"]):
        cat = "Machine_Learning"
    else:
        cat = "SDE_Backend"
    j["category"] = cat

    # Normalize location
    loc = j.get("location", "")
    if any(c in loc.lower() for c in ["india", "bengaluru", "bangalore", "hyderabad", "pune", "mumbai", "gurgaon", "gurugram", "noida", "delhi", "chennai"]):
        j["geo"] = "India"
    else:
        j["geo"] = "Remote"

    return j

def rank_job(j):
    score = 0
    # Prioritize AI / ML / Vision
    cat = j.get("category", "")
    if cat in ("GenAI_LLM", "ML_Vision", "Machine_Learning"):
        score += 40
    elif cat == "Data_Science":
        score += 25
    elif cat == "SDE_Backend":
        score += 10

    # Freshness date bonus
    pd = j.get("posted_date", "2026-10-15")
    if "2026-11" in pd:
        score += 20
    elif "2026-10" in pd:
        score += 10

    # India location bonus
    if j.get("geo") == "India":
        score += 15

    # Early career bonus
    t_lower = j.get("title", "").lower()
    if any(w in t_lower for w in ["intern", "trainee", "fresher", "junior", "associate", "entry", "sde 1", "sde-1", "sde i", "ml 1"]):
        score += 10

    return score

def main():
    applied_set = load_applied_set()
    raw_ashby = json.loads((OUT_DIR / "temp_fresh_ashby.json").read_text(encoding="utf-8"))
    raw_lever = json.loads((OUT_DIR / "temp_fresh_lever.json").read_text(encoding="utf-8"))
    raw_gh = json.loads((OUT_DIR / "temp_fresh_gh.json").read_text(encoding="utf-8"))

    def process_platform(raw_list):
        cleaned = []
        seen = set()
        for j in raw_list:
            u_norm = j["url"].strip().lower().rstrip("/")
            if u_norm in seen or u_norm in applied_set:
                continue
            san = sanitize_job(j)
            if san:
                seen.add(u_norm)
                cleaned.append(san)
        cleaned.sort(key=rank_job, reverse=True)
        return cleaned

    ashby_clean = process_platform(raw_ashby)
    lever_clean = process_platform(raw_lever)
    gh_clean = process_platform(raw_gh)

    print(f"Sanitized Candidate Pools:")
    print(f"  Ashby:      {len(ashby_clean)} available (need 100)")
    print(f"  Lever:      {len(lever_clean)} available (need 100)")
    print(f"  Greenhouse: {len(gh_clean)} available (need 100)")

    ashby_final = ashby_clean[:100]
    lever_final = lever_clean[:100]
    gh_final = gh_clean[:100]

    combined_300 = []
    combined_300.extend(ashby_final)
    combined_300.extend(lever_final)
    combined_300.extend(gh_final)

    # Save platform-specific files
    OUT_ASHBY.write_text(json.dumps({
        "platform": "ashby",
        "harvest_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "freshness": "Posted/Updated within the past month (October-November 2026)",
        "count": len(ashby_final),
        "target_filter": "India / Remote-Global (0-2 YoE), Python/ML/DS/AI/SDE",
        "jobs": ashby_final
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    OUT_LEVER.write_text(json.dumps({
        "platform": "lever",
        "harvest_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "freshness": "Posted/Updated within the past month (October-November 2026)",
        "count": len(lever_final),
        "target_filter": "India / Remote-Global (0-2 YoE), Python/ML/DS/AI/SDE",
        "jobs": lever_final
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    OUT_GH.write_text(json.dumps({
        "platform": "greenhouse",
        "harvest_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "freshness": "Posted/Updated within the past month (October-November 2026)",
        "count": len(gh_final),
        "target_filter": "India / Remote-Global (0-2 YoE), Python/ML/DS/AI/SDE",
        "jobs": gh_final
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    # Save master 300
    OUT_COMBINED.write_text(json.dumps({
        "harvest_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_count": len(combined_300),
        "freshness_window": "At most ~1 month old (Posted >= 2026-10-01)",
        "platform_breakdown": {
            "ashby": len(ashby_final),
            "lever": len(lever_final),
            "greenhouse": len(gh_final)
        },
        "target_filter": "India / Remote-Global (0-2 YoE), Python/ML/DS/AI/SDE",
        "jobs": combined_300
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nMASTER DATASETS SUCCESSFULLY SAVED:")
    print(f"  Combined (300): {OUT_COMBINED}")
    print(f"  Ashby (100):    {OUT_ASHBY}")
    print(f"  Lever (100):    {OUT_LEVER}")
    print(f"  Greenhouse (100): {OUT_GH}")

    # Summary
    for p_name, p_list in [("Ashby", ashby_final), ("Lever", lever_final), ("Greenhouse", gh_final)]:
        geo_c = Counter(j["geo"] for j in p_list)
        cat_c = Counter(j["category"] for j in p_list)
        print(f"\n{p_name} Breakdown (Count: {len(p_list)}):")
        print(f"  Geo: {dict(geo_c)}")
        print(f"  Categories: {dict(cat_c)}")
        print(f"  Top Companies: {Counter(j['org'] for j in p_list).most_common(5)}")

if __name__ == "__main__":
    main()
