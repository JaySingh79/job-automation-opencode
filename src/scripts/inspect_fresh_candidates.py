"""
inspect_fresh_candidates.py — Deep inspect fresh candidates for Ashby, Lever, Greenhouse.
"""
import json
import re
from pathlib import Path
from collections import Counter

# Load the fresh jobs by re-running probe logic with full job data
import sys
sys.path.append(r"D:\Projects\PRACTICE\firecrawl_test\src\scripts")
from test_board_apis import fetch, loc_verdict, title_verdict
from concurrent.futures import ThreadPoolExecutor, as_completed

INDIA = [
    "india", "bengaluru", "bangalore", "hyderabad", "pune", "mumbai", "gurgaon",
    "gurugram", "noida", "chennai", "delhi", "kolkata", "ahmedabad", "jaipur",
    "indore", "nagpur", "kochi", "vadodara", "surat", "chandigarh", "mysore"
]
BLOCK_GEO = [
    "united states", "u.s.", "(us)", "us only", "north america", "canada",
    "europe", "emea", "london", "berlin", "france", "germany", "singapore", "australia",
    "new york", "san francisco", "toronto", "ontario", "sweden", "netherlands",
    "(uk)", "britain", "spain", "italy", "poland", "mexico", "brazil", "dubai",
    "uae", "indonesia", "philippines", "nigeria", "kenya", "ukraine", "tokyo", "japan"
]

EXCL_SENIOR = re.compile(
    r"\b(senior|sr\.?|principal|staff|lead|manager|director|head|architect|president|vp|chief|"
    r"level (?:ii|iii|iv|v|2|3|4|5)|tier 3|tier 4)\b", re.I
)
EXCL_ROLE = re.compile(
    r"\b(recruiter|sales|marketing|account executive|customer success|operations|clinical|"
    r"legal|finance|tax|compliance|graphic|designer|product designer|content writer|copywriter|"
    r"hardware|supply chain|office manager|receptionist|executive assistant)\b", re.I
)
TARGET_ROLE = re.compile(
    r"\b(machine learning|\bml\b|\bai\b|llm|genai|generative ai|data scientist|data engineer|"
    r"data analyst|nlp|computer vision|deep learning|software engineer|software developer|"
    r"sde|backend|back-end|fullstack|full-stack|python|applied scientist|research engineer|"
    r"developer|programmer|intern|trainee|fresher|graduate engineer|sde-1|sde 1|sde-i|sde i)\b", re.I
)

# Load applied URLs
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

def inspect_title(title):
    if not title: return False
    if EXCL_SENIOR.search(title): return False
    if EXCL_ROLE.search(title): return False
    if not TARGET_ROLE.search(title): return False
    return True

def inspect_loc(loc):
    if not loc: return None
    l = loc.lower()
    if any(t in l for t in INDIA):
        return "India"
    if any(b in l for b in BLOCK_GEO):
        return None
    if any(r in l for r in ["remote", "apac", "worldwide", "global", "anywhere"]):
        return "Remote"
    return None

def fetch_lever(org):
    jobs = []
    try:
        data = fetch(f"https://api.lever.co/v0/postings/{org}?mode=json")
        for j in data or []:
            if not isinstance(j, dict): continue
            t = j.get("text") or ""
            cat = j.get("categories") or {}
            l = cat.get("location") or ""
            g = inspect_loc(l)
            if g and inspect_title(t):
                u = j.get("hostedUrl") or f"https://jobs.lever.co/{org}/{j.get('id')}"
                if u.strip().lower().rstrip('/') not in applied_urls:
                    jobs.append({
                        "platform": "lever",
                        "org": org,
                        "title": t,
                        "location": l,
                        "geo": g,
                        "url": u,
                        "id": j.get("id"),
                        "work_type": cat.get("commitment") or "Full-time",
                        "team": cat.get("team") or "Engineering",
                    })
    except Exception:
        pass
    return jobs

def fetch_ashby(org):
    jobs = []
    try:
        data = fetch(f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true")
        for j in (data.get("jobs") or []):
            t = j.get("title") or ""
            l = j.get("location") or ""
            g = inspect_loc(l)
            if g and inspect_title(t):
                ident = j.get("id")
                u = f"https://jobs.ashbyhq.com/{org}/{ident}"
                if u.strip().lower().rstrip('/') not in applied_urls:
                    jobs.append({
                        "platform": "ashby",
                        "org": org,
                        "title": t,
                        "location": l,
                        "geo": g,
                        "url": u,
                        "id": ident,
                        "work_type": j.get("employmentType") or "Full-time",
                        "team": j.get("department") or "Engineering",
                    })
    except Exception:
        pass
    return jobs

def fetch_greenhouse(org):
    jobs = []
    try:
        data = fetch(f"https://boards-api.greenhouse.io/v1/boards/{org}/jobs")
        for j in (data.get("jobs") or []):
            t = j.get("title") or ""
            loc_obj = j.get("location")
            l = loc_obj.get("name") if isinstance(loc_obj, dict) else (loc_obj or "")
            g = inspect_loc(l)
            if g and inspect_title(t):
                ident = str(j.get("id"))
                u = j.get("absolute_url") or f"https://job-boards.greenhouse.io/{org}/jobs/{ident}"
                if u.strip().lower().rstrip('/') not in applied_urls:
                    jobs.append({
                        "platform": "greenhouse",
                        "org": org,
                        "title": t,
                        "location": l,
                        "geo": g,
                        "url": u,
                        "id": ident,
                        "work_type": "Full-time",
                        "team": "Engineering",
                        "updated_at": j.get("updated_at") or "",
                    })
    except Exception:
        pass
    return jobs

def main():
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

    lever_jobs = []
    ashby_jobs = []
    gh_jobs = []

    with ThreadPoolExecutor(max_workers=20) as ex:
        futs_l = {ex.submit(fetch_lever, o): o for o in lever_orgs}
        futs_a = {ex.submit(fetch_ashby, o): o for o in ashby_orgs}
        futs_g = {ex.submit(fetch_greenhouse, o): o for o in gh_orgs}

        for f in as_completed(futs_l):
            lever_jobs.extend(f.result())
        for f in as_completed(futs_a):
            ashby_jobs.extend(f.result())
        for f in as_completed(futs_g):
            gh_jobs.extend(f.result())

    print(f"STRICT FILTER COUNTS:")
    print(f"  Lever: {len(lever_jobs)}")
    print(f"  Ashby: {len(ashby_jobs)}")
    print(f"  Greenhouse: {len(gh_jobs)}")

    # Print sample titles from each
    print("\nSample Lever jobs:")
    for j in lever_jobs[:5]:
        print(f"  [{j['org']}] {j['title']} ({j['location']}) -> {j['url']}")

    print("\nSample Ashby jobs:")
    for j in ashby_jobs[:5]:
        print(f"  [{j['org']}] {j['title']} ({j['location']}) -> {j['url']}")

    print("\nSample Greenhouse jobs:")
    for j in gh_jobs[:5]:
        print(f"  [{j['org']}] {j['title']} ({j['location']}) -> {j['url']}")

    # Save complete raw lists for further curation
    Path("src/job_search_results/ashby_lever_greenhouse").mkdir(parents=True, exist_ok=True)
    with open("src/job_search_results/ashby_lever_greenhouse/raw_fresh_lever.json", "w", encoding="utf-8") as f:
        json.dump(lever_jobs, f, indent=2)
    with open("src/job_search_results/ashby_lever_greenhouse/raw_fresh_ashby.json", "w", encoding="utf-8") as f:
        json.dump(ashby_jobs, f, indent=2)
    with open("src/job_search_results/ashby_lever_greenhouse/raw_fresh_greenhouse.json", "w", encoding="utf-8") as f:
        json.dump(gh_jobs, f, indent=2)

if __name__ == "__main__":
    main()
