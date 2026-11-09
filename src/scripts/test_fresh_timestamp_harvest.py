"""
test_fresh_timestamp_harvest.py — Probe for jobs strictly posted >= 2026-10-01.
"""
import json
import re
import ssl
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from collections import Counter

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}

OCT_1_2026 = datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp()

# Import helper functions
import sys
sys.path.append(r"D:\Projects\PRACTICE\firecrawl_test\src\scripts")
from harvest_fresh_300_ats import (
    classify_location, classify_title, load_applied_set,
    fetch_json
)

# Load org sets
lever_orgs = set()
ashby_orgs = set()
gh_orgs = set()

# Scan search results and scripts for known orgs
for p in Path("src/job_search_results").rglob("*.json"):
    try:
        content = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"https?://(?:jobs\.)?lever\.co/([A-Za-z0-9_.-]+)", content, re.I):
            s = m.group(1).lower().strip("/")
            if s not in ("v0", "search", "apply", "postings", "jobtwine"): lever_orgs.add(s)
        for m in re.finditer(r"https?://jobs\.ashbyhq\.com/([A-Za-z0-9_.-]+)", content, re.I):
            s = m.group(1).lower().strip("/")
            if s not in ("api", "posting-api", "job-board"): ashby_orgs.add(s)
        for m in re.finditer(r"https?://(?:job-boards\.|boards\.)?greenhouse\.io/([A-Za-z0-9_-]+)", content, re.I):
            s = m.group(1).lower().strip("/")
            if s not in ("v1", "boards", "embed", "api", "jobs"): gh_orgs.add(s)
    except Exception:
        pass

# Add extra discovered orgs
extra_lever = [
    "binance", "brillio-2", "coupa", "drivetrain", "enablecomp", "equativ",
    "everbridge", "ewor", "farfetch", "galepartners", "gohighlevel", "hevodata",
    "lingarogroup", "merklescience", "offchainlabs", "outcomesai", "paytm",
    "policyme", "portcast", "porter", "saviynt", "shopback-2", "shyftlabs",
    "smart-working-solutions", "supermove", "teamsnap", "trackmind", "veeva",
    "weekdayworks", "zimperium", "cars24", "spinny", "apna", "sharechat",
    "glance", "coindcx", "mpl", "dream11", "clevertap", "weloglobal", "tsmg", "jobgether"
]
for o in extra_lever: lever_orgs.add(o)

extra_ashby = [
    "abridge", "aiprise", "baseten", "brainco", "cartesia", "clerk", "cognition",
    "cohere", "cursor", "cynlr", "elevenlabs", "emergence", "fal-ai", "gecko-robotics",
    "hex", "jerry.ai", "lgads", "linear", "magic", "mistral.ai", "modal", "notion",
    "opslevel", "perplexity", "pika", "pinecone", "poolside", "posthog", "quora",
    "reka", "resend", "runway", "sarvam", "sierra", "sift", "skylo", "suno",
    "tessera-labs", "tolken", "warp", "weaviate", "hirehangar", "playpowerlabs",
    "careway", "korza", "ande", "duna", "espa", "yotta", "simular", "realmalliance",
    "gptzero", "meraki-labs", "bio", "aiprojects", "bjakcareer", "spector-ai",
    "gradera", "interview-kickstart", "ahl-saafai", "buildai", "ema"
]
for o in extra_ashby: ashby_orgs.add(o)

extra_gh = [
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
    "thoughtworks", "yugabyte", "gravitonresearchcapital", "gleanwork"
]
for o in extra_gh: gh_orgs.add(o)

applied_set = load_applied_set()

def probe_lever_fresh(org):
    jobs = []
    try:
        data = fetch_json(f"https://api.lever.co/v0/postings/{org}?mode=json")
        for j in (data or []):
            if not isinstance(j, dict): continue
            ca = j.get("createdAt")
            if not ca or (ca / 1000.0) < OCT_1_2026:
                continue
            title = j.get("text") or ""
            t_clean, cat_role = classify_title(title)
            if not t_clean: continue
            cat = j.get("categories") or {}
            loc = cat.get("location") or ""
            geo = classify_location(loc)
            if not geo: continue
            u = j.get("hostedUrl") or f"https://jobs.lever.co/{org}/{j.get('id')}"
            if u.strip().lower().rstrip("/") in applied_set: continue
            post_date = datetime.fromtimestamp(ca / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")
            jobs.append({
                "platform": "lever", "org": org, "title": t_clean, "category": cat_role,
                "location": loc, "geo": geo, "url": u, "posted_date": post_date, "created_at": ca
            })
    except Exception:
        pass
    return jobs

def probe_ashby_fresh(org):
    jobs = []
    try:
        data = fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true")
        for j in (data.get("jobs") or []):
            pub = j.get("publishedAt")
            if not pub: continue
            try:
                dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                if dt.timestamp() < OCT_1_2026: continue
                post_date = dt.strftime("%Y-%m-%d")
            except Exception:
                continue
            title = j.get("title") or ""
            t_clean, cat_role = classify_title(title)
            if not t_clean: continue
            loc = j.get("location") or ""
            all_locs = [loc] + [sec.get("location") or "" for sec in (j.get("secondaryLocations") or [])]
            geo = None
            for l_cand in all_locs:
                geo = classify_location(l_cand)
                if geo:
                    loc = l_cand
                    break
            if not geo: continue
            ident = j.get("id")
            u = f"https://jobs.ashbyhq.com/{org}/{ident}"
            if u.strip().lower().rstrip("/") in applied_set: continue
            jobs.append({
                "platform": "ashby", "org": org, "title": t_clean, "category": cat_role,
                "location": loc, "geo": geo, "url": u, "posted_date": post_date, "published_at": pub
            })
    except Exception:
        pass
    return jobs

def probe_gh_fresh(org):
    jobs = []
    try:
        data = fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{org}/jobs")
        for j in (data.get("jobs") or []):
            up = j.get("updated_at")
            if not up: continue
            try:
                dt = datetime.fromisoformat(up.replace("Z", "+00:00"))
                if dt.timestamp() < OCT_1_2026: continue
                post_date = dt.strftime("%Y-%m-%d")
            except Exception:
                continue
            title = j.get("title") or ""
            t_clean, cat_role = classify_title(title)
            if not t_clean: continue
            loc_obj = j.get("location")
            loc = loc_obj.get("name") if isinstance(loc_obj, dict) else (loc_obj or "")
            geo = classify_location(loc)
            if not geo: continue
            ident = str(j.get("id"))
            u = j.get("absolute_url") or f"https://job-boards.greenhouse.io/{org}/jobs/{ident}"
            if u.strip().lower().rstrip("/") in applied_set: continue
            jobs.append({
                "platform": "greenhouse", "org": org, "title": t_clean, "category": cat_role,
                "location": loc, "geo": geo, "url": u, "posted_date": post_date, "updated_at": up
            })
    except Exception:
        pass
    return jobs

def main():
    print(f"Probing with STRICT POSTING DATE >= 2026-10-01 (<37 days old)...")
    print(f"Orgs: Lever={len(lever_orgs)}, Ashby={len(ashby_orgs)}, Greenhouse={len(gh_orgs)}")

    lever_jobs = []
    ashby_jobs = []
    gh_jobs = []

    with ThreadPoolExecutor(max_workers=25) as ex:
        futs_l = {ex.submit(probe_lever_fresh, o): o for o in lever_orgs}
        futs_a = {ex.submit(probe_ashby_fresh, o): o for o in ashby_orgs}
        futs_g = {ex.submit(probe_gh_fresh, o): o for o in gh_orgs}

        for f in as_completed(futs_l):
            lever_jobs.extend(f.result())
        for f in as_completed(futs_a):
            ashby_jobs.extend(f.result())
        for f in as_completed(futs_g):
            gh_jobs.extend(f.result())

    print(f"\nStrictly Fresh (<= 37 days) Unapplied Results:")
    print(f"  Lever: {len(lever_jobs)}")
    print(f"  Ashby: {len(ashby_jobs)}")
    print(f"  Greenhouse: {len(gh_jobs)}")

if __name__ == "__main__":
    main()
