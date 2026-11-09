"""
test_board_apis.py — Fast probe of known Ashby, Lever, Greenhouse org APIs.
"""
import json
import re
import ssl
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from collections import Counter

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}

INDIA = [
    "india", "bengaluru", "bangalore", "hyderabad", "pune", "mumbai", "gurgaon",
    "gurugram", "noida", "chennai", "delhi", "kolkata", "ahmedabad", "jaipur",
    "indore", "nagpur", "kochi", "vadodara", "surat", "chandigarh", "mysore", "remote - india"
]
BLOCK_GEO = [
    "united states", "u.s.", "(us)", "us only", "north america", "canada",
    "europe", "emea", "london", "berlin", "france", "germany", "singapore", "australia",
    "new york", "san francisco", "toronto", "ontario", "sweden", "netherlands",
    "(uk)", "britain", "spain", "italy", "poland", "mexico", "brazil", "dubai",
    "uae", "indonesia", "philippines", "nigeria", "kenya", "ukraine", "tokyo", "japan"
]

EXCL_WORDS = re.compile(
    r"\b(senior|sr\.?|principal|staff|lead|manager|director|head|architect|president|vp|chief|"
    r"frontend|front-end|front end|qa|quality|recruiting|sales|marketing|growth|"
    r"customer|business|financial|legal|design|supply|clinical|revenue|operations|"
    r"account executive|product manager|content|copywriter|tax|consultant|specialist|specialists)\b", re.I)

LEVEL_TAIL = re.compile(r"(engineer|developer|scientist|sde|analyst)\s*[-(]?\s*(ii|iii|iv|v|2|3|4|5)\b", re.I)

REQ_WORDS = re.compile(
    r"\b(software|developer|engineer|sde|machine learning|\bml\b|\bai\b|llm|genai|generative|"
    r"data|nlp|intern|trainee|graduate|applied|research|backend|back-end|fullstack|full-stack|"
    r"python|deep learning|computer vision|nlp|nlp/llm|artificial intelligence)\b", re.I)

JAVA_CPP_EXCLUSIVE = re.compile(r"\b(java developer|c\+\+ developer|golang developer|android developer|ios developer|swift developer)\b", re.I)

def loc_verdict(location: str):
    if not location:
        return None
    l = location.lower()
    if any(t in l for t in INDIA):
        return "india"
    if any(b in l for b in BLOCK_GEO):
        return None
    if "remote" in l or "apac" in l or "worldwide" in l or "global" in l or "anywhere" in l:
        return "remote"
    return None

def title_verdict(title: str):
    if not title:
        return None
    t = title.strip()
    if EXCL_WORDS.search(t) or LEVEL_TAIL.search(t):
        return None
    if JAVA_CPP_EXCLUSIVE.search(t):
        return None
    if not REQ_WORDS.search(t):
        return None
    return True

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=12, context=CTX) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def probe_lever(org):
    jobs = []
    try:
        data = fetch(f"https://api.lever.co/v0/postings/{org}?mode=json")
        for j in data or []:
            if not isinstance(j, dict):
                continue
            cat = j.get("categories") or {}
            loc = cat.get("location") or ""
            title = j.get("text") or ""
            if title_verdict(title) and loc_verdict(loc):
                jobs.append({
                    "platform": "lever",
                    "org": org,
                    "title": title,
                    "location": loc,
                    "geo": loc_verdict(loc),
                    "url": j.get("hostedUrl") or f"https://jobs.lever.co/{org}/{j.get('id')}",
                    "id": j.get("id"),
                })
    except Exception:
        pass
    return jobs

def probe_ashby(org):
    jobs = []
    try:
        data = fetch(f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true")
        for j in (data.get("jobs") or []):
            loc = j.get("location") or ""
            title = j.get("title") or ""
            if title_verdict(title) and loc_verdict(loc):
                ident = j.get("id")
                jobs.append({
                    "platform": "ashby",
                    "org": org,
                    "title": title,
                    "location": loc,
                    "geo": loc_verdict(loc),
                    "url": f"https://jobs.ashbyhq.com/{org}/{ident}",
                    "id": ident,
                })
    except Exception:
        pass
    return jobs

def probe_greenhouse(org):
    jobs = []
    try:
        data = fetch(f"https://boards-api.greenhouse.io/v1/boards/{org}/jobs")
        for j in (data.get("jobs") or []):
            loc_obj = j.get("location")
            loc = loc_obj.get("name") if isinstance(loc_obj, dict) else (loc_obj or "")
            title = j.get("title") or ""
            if title_verdict(title) and loc_verdict(loc):
                ident = j.get("id")
                jobs.append({
                    "platform": "greenhouse",
                    "org": org,
                    "title": title,
                    "location": loc,
                    "geo": loc_verdict(loc),
                    "url": j.get("absolute_url") or f"https://job-boards.greenhouse.io/{org}/jobs/{ident}",
                    "id": str(ident),
                })
    except Exception:
        pass
    return jobs

def main():
    # Gather orgs from search results
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

    print(f"Targeting: Lever={len(lever_orgs)} orgs, Ashby={len(ashby_orgs)} orgs, Greenhouse={len(gh_orgs)} orgs")

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

    print(f"Total live jobs found: {len(all_jobs)}")
    c = Counter(j["platform"] for j in all_jobs)
    print(f"By Platform: {dict(c)}")

if __name__ == "__main__":
    main()
