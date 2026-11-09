"""
harvest_fresh_300_ats.py — Discover and curate 100 Ashby, 100 Lever, 100 Greenhouse jobs.
Targets: India / Remote-Global (India-eligible), ML / DS / AI / SDE (0-2 YoE).
Pruned of any test postings, L3+ levels, or QA/Test-engineering roles.
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
OUT_DIR = ROOT / "src" / "job_search_results" / "ashby_lever_greenhouse"
OUT_COMBINED = OUT_DIR / "2026-11-07-fresh-300-ashby-lever-greenhouse.json"
OUT_ASHBY = OUT_DIR / "2026-11-07-ashby-100.json"
OUT_LEVER = OUT_DIR / "2026-11-07-lever-100.json"
OUT_GH = OUT_DIR / "2026-11-07-greenhouse-100.json"

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}

# ----------------- GEOGRAPHY FILTER -----------------
INDIA_CITIES = [
    "india", "bengaluru", "bangalore", "hyderabad", "pune", "mumbai", "gurgaon",
    "gurugram", "noida", "chennai", "delhi", "kolkata", "ahmedabad", "jaipur",
    "indore", "nagpur", "kochi", "vadodara", "surat", "chandigarh", "mysore",
    "karnataka", "maharashtra", "telangana", "tamil nadu", "haryana", "uttar pradesh"
]

BLOCK_GEO = [
    "united states", "u.s.", "(us)", "us only", "north america", "canada",
    "europe", "emea", "london", "berlin", "france", "germany", "singapore", "australia",
    "new york", "san francisco", "toronto", "ontario", "sweden", "netherlands",
    "(uk)", "britain", "spain", "italy", "poland", "mexico", "brazil", "dubai",
    "uae", "indonesia", "philippines", "nigeria", "kenya", "ukraine", "tokyo", "japan",
    "latin america", "latam", "austria", "belgium", "switzerland", "ireland", "dublin"
]

REMOTE_KEYWORDS = [
    "remote", "anywhere", "worldwide", "global", "work from anywhere", "apac", "distributed"
]

def classify_location(loc_str: str):
    if not loc_str:
        return None
    l = loc_str.lower()
    if any(city in l for city in INDIA_CITIES):
        return "India"
    if any(b in l for b in BLOCK_GEO):
        if any(city in l for city in INDIA_CITIES):
            return "India"
        return None
    if any(r in l for r in REMOTE_KEYWORDS):
        return "Remote"
    return None

# ----------------- SENIORITY & ROLE FILTER -----------------
EXCL_SENIOR = re.compile(
    r"\b(senior|sr\.?|principal|staff|lead|director|head|vp|vice president|chief|architect|"
    r"level (?:[3-9]|iii|iv|v|vi)|tier [3-9]|"
    r"(?:sde|engineer|developer|scientist|analyst|associate)\s*[-_ ]*\s*(?:[3-9]|iii|iv|v|vi)\b|"
    r"\b(?:iii|iv|v|vi)\b|"
    r"l[3-9]\b|partner|founding engineer|founding designer|engineering manager|tech lead)\b", re.I
)

EXCL_NON_TECH = re.compile(
    r"\b(recruiter|recruiting|sales|account executive|business development|marketing|growth manager|"
    r"customer success|customer support|support engineer|operations associate|clinical|legal|finance|"
    r"payroll|tax|compliance|graphic designer|ui/ux designer|product designer|copywriter|content|"
    r"frontend|front-end|front end|"
    r"hardware engineer|supply chain|office manager|receptionist|executive assistant|event coordinator)\b", re.I
)

EXCL_TEST_QA = re.compile(
    r"\b(qa|sdet|quality assurance|test engineer|test infra|automation test|dummy|sample role|demo job|kiran|kombo)\b|(?:\btest\b)", re.I
)

TARGET_TECH = re.compile(
    r"\b(machine learning|\bml\b|\bai\b|llm|genai|generative ai|data scientist|data engineer|"
    r"data analyst|computer vision|deep learning|software engineer|software developer|"
    r"sde|backend|back-end|fullstack|full-stack|python|applied scientist|research engineer|"
    r"developer|programmer|intern|trainee|fresher|graduate engineer|sde-1|sde 1|sde-i|sde i|"
    r"ai engineer|mlops|ai researcher|nlp|algorithm engineer)\b", re.I
)

EXCL_LANGUAGE_RESTRICTED = re.compile(
    r"\b(senior java|java developer|c\+\+ developer|embedded c\+\+|ios developer|swift developer|"
    r"android developer|flutter developer|react native developer)\b", re.I
)

def classify_title(title: str):
    if not title:
        return None, None
    t = title.strip()
    if EXCL_SENIOR.search(t):
        return None, None
    if EXCL_NON_TECH.search(t):
        return None, None
    if EXCL_TEST_QA.search(t):
        return None, None
    if EXCL_LANGUAGE_RESTRICTED.search(t):
        return None, None
    if not TARGET_TECH.search(t):
        return None, None

    # Categorize
    t_lower = t.lower()
    if any(k in t_lower for k in ["computer vision", "vision", "robotics", "deep learning", "applied scientist"]):
        category = "ML_Vision"
    elif any(k in t_lower for k in ["genai", "llm", "generative ai", "ai engineer", "agentic", "agent", "prompt", "nlp", "ai researcher"]):
        category = "GenAI_LLM"
    elif any(k in t_lower for k in ["data scientist", "data engineer", "data analyst", "data science"]):
        category = "Data_Science"
    elif any(k in t_lower for k in ["machine learning", "ml engineer", "mlops", "ai/ml"]):
        category = "Machine_Learning"
    else:
        category = "SDE_Backend"

    return t, category

# ----------------- APPLIED EXCLUSIONS -----------------
def load_applied_set():
    applied = set()
    for p in ROOT.glob("src/applied/*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
            if isinstance(data, list):
                for item in data:
                    u = item.get("url") or item.get("job_url")
                    if u: applied.add(u.strip().lower().rstrip("/"))
            elif isinstance(data, dict):
                for k, v in data.items():
                    applied.add(k.strip().lower().rstrip("/"))
                    if isinstance(v, dict) and v.get("url"):
                        applied.add(v["url"].strip().lower().rstrip("/"))
        except Exception:
            pass

    p_root = ROOT / "jobs_applied.json"
    if p_root.exists():
        try:
            data = json.loads(p_root.read_text(encoding="utf-8", errors="replace"))
            if isinstance(data, list):
                for item in data:
                    u = item.get("url")
                    if u: applied.add(u.strip().lower().rstrip("/"))
        except Exception:
            pass

    p_audit = ROOT / "src/application_progress/ashby_lever_greenhouse/2026-11-06-200-submit-audit.jsonl"
    if p_audit.exists():
        for line in p_audit.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip():
                try:
                    row = json.loads(line)
                    u = row.get("url")
                    if u: applied.add(u.strip().lower().rstrip("/"))
                except Exception:
                    pass

    return applied

# ----------------- FETCH LOGIC -----------------
def fetch_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=10, context=CTX) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def fetch_lever_org(org, applied_set):
    jobs = []
    try:
        data = fetch_json(f"https://api.lever.co/v0/postings/{org}?mode=json")
        for j in (data or []):
            if not isinstance(j, dict):
                continue
            title = j.get("text") or ""
            t_clean, cat_role = classify_title(title)
            if not t_clean:
                continue
            cat = j.get("categories") or {}
            loc = cat.get("location") or ""
            geo = classify_location(loc)
            if not geo:
                continue
            u = j.get("hostedUrl") or f"https://jobs.lever.co/{org}/{j.get('id')}"
            u_norm = u.strip().lower().rstrip("/")
            if u_norm in applied_set:
                continue
            jobs.append({
                "platform": "lever",
                "org": org,
                "title": t_clean,
                "category": cat_role,
                "location": loc,
                "geo": geo,
                "url": u,
                "id": j.get("id"),
                "work_type": cat.get("commitment") or "Full-time",
                "team": cat.get("team") or "Engineering",
                "created_at": j.get("createdAt"),
            })
    except Exception:
        pass
    return jobs

def fetch_ashby_org(org, applied_set):
    jobs = []
    try:
        data = fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true")
        for j in (data.get("jobs") or []):
            title = j.get("title") or ""
            t_clean, cat_role = classify_title(title)
            if not t_clean:
                continue
            loc = j.get("location") or ""
            all_locs = [loc]
            for sec in (j.get("secondaryLocations") or []):
                all_locs.append(sec.get("location") or "")
            geo = None
            for l_cand in all_locs:
                geo = classify_location(l_cand)
                if geo:
                    loc = l_cand
                    break
            if not geo:
                continue
            ident = j.get("id")
            u = f"https://jobs.ashbyhq.com/{org}/{ident}"
            u_norm = u.strip().lower().rstrip("/")
            if u_norm in applied_set:
                continue
            jobs.append({
                "platform": "ashby",
                "org": org,
                "title": t_clean,
                "category": cat_role,
                "location": loc,
                "geo": geo,
                "url": u,
                "id": ident,
                "work_type": j.get("employmentType") or "Full-time",
                "team": j.get("department") or "Engineering",
                "published_at": j.get("publishedAt"),
            })
    except Exception:
        pass
    return jobs

def fetch_greenhouse_org(org, applied_set):
    jobs = []
    try:
        data = fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{org}/jobs")
        for j in (data.get("jobs") or []):
            title = j.get("title") or ""
            t_clean, cat_role = classify_title(title)
            if not t_clean:
                continue
            loc_obj = j.get("location")
            loc = loc_obj.get("name") if isinstance(loc_obj, dict) else (loc_obj or "")
            geo = classify_location(loc)
            if not geo:
                continue
            ident = str(j.get("id"))
            u = j.get("absolute_url") or f"https://job-boards.greenhouse.io/{org}/jobs/{ident}"
            u_norm = u.strip().lower().rstrip("/")
            if u_norm in applied_set:
                continue
            jobs.append({
                "platform": "greenhouse",
                "org": org,
                "title": t_clean,
                "category": cat_role,
                "location": loc,
                "geo": geo,
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
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    applied_set = load_applied_set()
    print(f"Loaded {len(applied_set)} previously applied/attempted URLs for exclusion.", flush=True)

    lever_orgs = {
        "binance", "brillio-2", "coupa", "drivetrain", "enablecomp", "equativ",
        "everbridge", "ewor", "farfetch", "galepartners", "gohighlevel", "hevodata",
        "lingarogroup", "merklescience", "offchainlabs", "outcomesai",
        "paytm", "policyme", "portcast", "porter", "saviynt", "shopback-2", "shyftlabs",
        "smart-working-solutions", "supermove", "teamsnap", "trackmind", "veeva",
        "weekdayworks", "zimperium", "cars24", "spinny", "apna", "sharechat",
        "glance", "coindcx", "mpl", "dream11", "clevertap"
    }

    ashby_orgs = {
        "abridge", "aiprise", "baseten", "brainco", "cartesia", "clerk", "cognition",
        "cohere", "cursor", "cynlr", "elevenlabs", "emergence", "fal-ai", "gecko-robotics",
        "hex", "jerry.ai", "lgads", "linear", "magic", "mistral.ai", "modal", "notion",
        "opslevel", "perplexity", "pika", "pinecone", "poolside", "posthog", "quora",
        "reka", "resend", "runway", "sarvam", "sierra", "sift", "skylo", "suno",
        "tessera-labs", "tolken", "warp", "weaviate", "hirehangar", "playpowerlabs",
        "careway", "korza", "ande", "duna", "espa", "yotta", "simular", "realmalliance",
        "gptzero", "meraki-labs", "bio", "aiprojects", "bjakcareer", "spector-ai"
    }

    greenhouse_orgs = {
        "affirm", "anthropic", "brex", "carta", "checkr", "chime", "cloudflare",
        "coinbase", "databricks", "datadog", "elastic", "figma", "fireblocks", "fivetran",
        "gemini", "gitlab", "groww", "gusto", "hackerrank", "honeycomb", "inmobi",
        "lattice", "launchdarkly", "mercury", "mongodb", "monzo", "n26", "neo4j",
        "newrelic", "pagerduty", "ramp", "remote", "robinhood", "rubrik", "scaleai",
        "stripe", "togetherai", "vercel", "turing", "enterpret", "rzr", "anteriad",
        "doordashindia", "dscout", "lynxanalytics", "interviewkickstart", "singlestore",
        "bitgo", "platformscience", "nirmata", "commerceiq", "anaplan", "gupshup",
        "zetwerk", "cloudsek", "coherehealth", "redwoodsoftware", "jumio", "greedygame",
        "easyship", "tegnaindia", "thetradedesk", "browserstack", "hasura", "urbancompany",
        "skildai-careers", "postman", "okta", "deliveroo", "zetaglobal", "instacart",
        "thoughtworks", "yugabyte"
    }

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
                if s not in ("v1", "boards", "embed", "api", "jobs"): greenhouse_orgs.add(s)
        except Exception:
            pass

    lever_candidates = []
    ashby_candidates = []
    gh_candidates = []

    with ThreadPoolExecutor(max_workers=25) as ex:
        futs_l = {ex.submit(fetch_lever_org, o, applied_set): o for o in lever_orgs}
        futs_a = {ex.submit(fetch_ashby_org, o, applied_set): o for o in ashby_orgs}
        futs_g = {ex.submit(fetch_greenhouse_org, o, applied_set): o for o in greenhouse_orgs}

        for f in as_completed(futs_l):
            res = f.result()
            if res: lever_candidates.extend(res)
        for f in as_completed(futs_a):
            res = f.result()
            if res: ashby_candidates.extend(res)
        for f in as_completed(futs_g):
            res = f.result()
            if res: gh_candidates.extend(res)

    def dedup_jobs(jobs):
        seen = set()
        deduped = []
        for j in jobs:
            u_norm = j["url"].strip().lower().rstrip("/")
            if u_norm not in seen:
                seen.add(u_norm)
                deduped.append(j)
        return deduped

    lever_dedup = dedup_jobs(lever_candidates)
    ashby_dedup = dedup_jobs(ashby_candidates)
    gh_dedup = dedup_jobs(gh_candidates)

    print(f"Pristine unique unapplied live jobs:", flush=True)
    print(f"  Lever: {len(lever_dedup)}", flush=True)
    print(f"  Ashby: {len(ashby_dedup)}", flush=True)
    print(f"  Greenhouse: {len(gh_dedup)}", flush=True)

    def rank_job(j):
        score = 0
        cat = j.get("category", "")
        if cat in ("GenAI_LLM", "ML_Vision", "Machine_Learning"):
            score += 50
        elif cat == "Data_Science":
            score += 35
        elif cat == "SDE_Backend":
            score += 20

        if j.get("geo") == "India":
            score += 20
        elif j.get("geo") == "Remote":
            score += 10

        t_lower = j.get("title", "").lower()
        if any(w in t_lower for w in ["intern", "trainee", "fresher", "junior", "associate", "entry", "sde 1", "sde-1", "sde i"]):
            score += 15

        return score

    lever_dedup.sort(key=rank_job, reverse=True)
    ashby_dedup.sort(key=rank_job, reverse=True)
    gh_dedup.sort(key=rank_job, reverse=True)

    ashby_top100 = ashby_dedup[:100]
    lever_top100 = lever_dedup[:100]
    gh_top100 = gh_dedup[:100]

    combined_300 = []
    combined_300.extend(ashby_top100)
    combined_300.extend(lever_top100)
    combined_300.extend(gh_top100)

    OUT_ASHBY.write_text(json.dumps({
        "platform": "ashby",
        "harvest_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(ashby_top100),
        "target_filter": "India/Remote-Global (0-2 YoE), Python/ML/DS/AI/SDE",
        "jobs": ashby_top100
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    OUT_LEVER.write_text(json.dumps({
        "platform": "lever",
        "harvest_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(lever_top100),
        "target_filter": "India/Remote-Global (0-2 YoE), Python/ML/DS/AI/SDE",
        "jobs": lever_top100
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    OUT_GH.write_text(json.dumps({
        "platform": "greenhouse",
        "harvest_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(gh_top100),
        "target_filter": "India/Remote-Global (0-2 YoE), Python/ML/DS/AI/SDE",
        "jobs": gh_top100
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    OUT_COMBINED.write_text(json.dumps({
        "harvest_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_count": len(combined_300),
        "platform_breakdown": {
            "ashby": len(ashby_top100),
            "lever": len(lever_top100),
            "greenhouse": len(gh_top100)
        },
        "target_filter": "India/Remote-Global (0-2 YoE), Python/ML/DS/AI/SDE",
        "jobs": combined_300
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nSUCCESSFULLY WROTE MASTER ATS HARVEST DATASETS:", flush=True)
    print(f"  Combined (300): {OUT_COMBINED}", flush=True)
    print(f"  Ashby (100):    {OUT_ASHBY}", flush=True)
    print(f"  Lever (100):    {OUT_LEVER}", flush=True)
    print(f"  Greenhouse (100): {OUT_GH}", flush=True)

if __name__ == "__main__":
    main()
