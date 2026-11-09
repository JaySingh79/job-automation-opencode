"""
probe_tech_companies_lever_ashby.py — Test ~120 tech startup slugs on Lever and Ashby.
"""
import json
import re
import ssl
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

OCT_1_2026 = datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp()
CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0"}

import sys
sys.path.append(r"D:\Projects\PRACTICE\firecrawl_test\src\scripts")
from harvest_fresh_300_ats import classify_location, classify_title, load_applied_set, fetch_json
from harvest_fresh_monthly_ats import fetch_lever_fresh, fetch_ashby_fresh

CANDIDATES = [
    # Prominent Indian & global tech startups / scaleups
    "neuron7", "mindtickle", "avoca", "aiprise", "smallest", "buildai", "build-ai",
    "thelevel.ai", "firstwork", "invideo", "pocketfm", "lentra", "perfios", "indmoney",
    "smallcase", "cultfit", "curefit", "zopper", "turtlemint", "acko", "godigit", "digit",
    "navi", "jupiter", "superops", "loconav", "yellow-ai", "yellowai", "haptik", "verloop",
    "superannotate", "vahan", "apna", "okcredit", "dukaan", "dealshare", "citymall",
    "glowroad", "nobroker", "ofbusiness", "moglix", "ninjacart", "bijak", "waycool",
    "reshamandi", "bijnis", "elasticrun", "blackbuck", "delhivery", "xpressbees", "blowhorn",
    "loadshare", "letstransport", "cogoport", "wizfreight", "scrut", "vanta", "drata",
    "secureframe", "auditboard", "quora", "mastra", "sandboxaq", "bio", "mimolabs",
    "handshake", "mapbox", "sycamore", "clickhouse", "retool", "posthog", "cal.com",
    "raycast", "dub", "superhuman", "glean", "collinear", "demandbase", "gradera",
    "tolken", "meraki-labs", "bjakcareer", "spector-ai", "ahl-saafai", "ema",
    "browserstack", "hasura", "clevertap", "chargebee", "postman", "whatfix", "leadSquared",
    "leadsquared", "signeasy", "kissflow", "wingify", "vwo", "browserstack", "hackerearth",
    "recro", "scaler", "interviewbit", "masaischool", "newtonschool", "crio", "almabetter",
    "springboard", "upgrad", "simplilearn", "eruditus", "greatlearning", "vedantu",
    "byjus", "unacademy", "physicswallah", "pw", "classplus", "teachmint", "toppr",
    "doubtnut", "adda247", "testbook", "oliveboard", "gradeup", "unstop", "dare2compete"
]

def main():
    applied_set = load_applied_set()
    existing_ashby = json.loads(Path("src/job_search_results/ashby_lever_greenhouse/temp_fresh_ashby.json").read_text(encoding="utf-8"))
    existing_lever = json.loads(Path("src/job_search_results/ashby_lever_greenhouse/temp_fresh_lever.json").read_text(encoding="utf-8"))

    seen_ashby = {j["url"].strip().lower().rstrip("/") for j in existing_ashby}
    seen_lever = {j["url"].strip().lower().rstrip("/") for j in existing_lever}

    print(f"Current verified: Ashby={len(existing_ashby)}, Lever={len(existing_lever)}")

    def probe_a(slug):
        try:
            return fetch_ashby_fresh(slug, applied_set)
        except Exception:
            return []

    def probe_l(slug):
        try:
            return fetch_lever_fresh(slug, applied_set)
        except Exception:
            return []

    print(f"Testing {len(CANDIDATES)} candidate slugs against Ashby & Lever APIs...", flush=True)
    with ThreadPoolExecutor(max_workers=30) as ex:
        futs_a = {ex.submit(probe_a, s): s for s in CANDIDATES}
        futs_l = {ex.submit(probe_l, s): s for s in CANDIDATES}

        for f in as_completed(futs_a):
            for j in f.result():
                u_norm = j["url"].strip().lower().rstrip("/")
                if u_norm not in seen_ashby and u_norm not in applied_set:
                    seen_ashby.add(u_norm)
                    existing_ashby.append(j)

        for f in as_completed(futs_l):
            for j in f.result():
                u_norm = j["url"].strip().lower().rstrip("/")
                if u_norm not in seen_lever and u_norm not in applied_set:
                    seen_lever.add(u_norm)
                    existing_lever.append(j)

    print(f"\nUPDATED AFTER PROBE:")
    print(f"  Ashby: {len(existing_ashby)}")
    print(f"  Lever: {len(existing_lever)}")

    Path("src/job_search_results/ashby_lever_greenhouse/temp_fresh_ashby.json").write_text(json.dumps(existing_ashby, indent=2), encoding="utf-8")
    Path("src/job_search_results/ashby_lever_greenhouse/temp_fresh_lever.json").write_text(json.dumps(existing_lever, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
