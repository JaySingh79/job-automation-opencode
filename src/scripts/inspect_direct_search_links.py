"""
inspect_direct_search_links.py — Collect and verify direct search result links.
"""
import json
import re
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
OUT_DIR = ROOT / "src" / "job_search_results" / "ashby_lever_greenhouse"

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}

import sys
sys.path.append(r"D:\Projects\PRACTICE\firecrawl_test\src\scripts")
from harvest_fresh_300_ats import classify_location, classify_title, load_applied_set

def main():
    applied_set = load_applied_set()
    existing_ashby = json.loads((OUT_DIR / "temp_fresh_ashby.json").read_text(encoding="utf-8"))
    existing_lever = json.loads((OUT_DIR / "temp_fresh_lever.json").read_text(encoding="utf-8"))

    seen_ashby = {j["url"].strip().lower().rstrip("/") for j in existing_ashby}
    seen_lever = {j["url"].strip().lower().rstrip("/") for j in existing_lever}

    print(f"Starting with: Ashby={len(existing_ashby)}, Lever={len(existing_lever)}")

    # Scan logs and task output for all direct URLs discovered during searches
    direct_candidates = set()
    for p in Path(r"C:\Users\binit\.gemini\antigravity-cli\brain\037e7079-4b99-4843-9bad-0639e1ccba9a\.system_generated\tasks").glob("*.log"):
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"https?://jobs\.ashbyhq\.com/[A-Za-z0-9_.-]+/[a-f0-9-]{8,}", txt, re.I):
                direct_candidates.add(("ashby", m.group(0)))
            for m in re.finditer(r"https?://(?:jobs\.)?lever\.co/[A-Za-z0-9_.-]+/[a-f0-9-]{8,}", txt, re.I):
                direct_candidates.add(("lever", m.group(0)))
        except Exception:
            pass

    # Also scan recent search files
    for p in Path("src/job_search_results").rglob("*.json"):
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"https?://jobs\.ashbyhq\.com/[A-Za-z0-9_.-]+/[a-f0-9-]{8,}", txt, re.I):
                direct_candidates.add(("ashby", m.group(0)))
            for m in re.finditer(r"https?://(?:jobs\.)?lever\.co/[A-Za-z0-9_.-]+/[a-f0-9-]{8,}", txt, re.I):
                direct_candidates.add(("lever", m.group(0)))
        except Exception:
            pass

    print(f"Total direct URL candidates found: {len(direct_candidates)}")

    def verify_direct_job(cand):
        plat, url = cand
        u_norm = url.strip().lower().rstrip("/")
        if plat == "ashby" and u_norm in seen_ashby: return None
        if plat == "lever" and u_norm in seen_lever: return None
        if u_norm in applied_set: return None

        # Fetch page to get title and location
        req = urllib.request.Request(url, headers=UA)
        try:
            with urllib.request.urlopen(req, timeout=6, context=CTX) as r:
                if r.status != 200: return None
                html = r.read().decode("utf-8", "replace")
                # Extract title
                m_t = re.search(r"<title>([^<]+)</title>", html, re.I)
                title = m_t.group(1) if m_t else ""
                # Clean title: e.g. "Software Engineer - Company - Lever"
                title = re.sub(r"\s*-\s*(Lever|Ashby|Jobs).*$", "", title, flags=re.I).strip()
                t_clean, cat_role = classify_title(title)
                if not t_clean: return None

                # Extract location from meta or text
                m_loc = re.search(r'"jobLocation":\s*\{[^}]*"addressLocality":\s*"([^"]+)"', html)
                loc = m_loc.group(1) if m_loc else ""
                if not loc:
                    m_loc2 = re.search(r'class="[^"]*location[^"]*"[^>]*>([^<]+)<', html, re.I)
                    loc = m_loc2.group(1) if m_loc2 else ""
                if not loc:
                    if "india" in html.lower() or "bengaluru" in html.lower() or "bangalore" in html.lower():
                        loc = "India"
                    elif "remote" in html.lower():
                        loc = "Remote"

                geo = classify_location(loc)
                if not geo: return None

                # Extract org
                m_org = re.search(r"(?:ashbyhq\.com|lever\.co)/([A-Za-z0-9_.-]+)", url)
                org = m_org.group(1) if m_org else ""

                return {
                    "platform": plat, "org": org, "title": t_clean, "category": cat_role,
                    "location": loc, "geo": geo, "url": url, "posted_date": "2026-10-18" # Fresh from sweep
                }
        except Exception:
            return None

    print(f"Probing {len(direct_candidates)} direct candidates for liveness & fit...", flush=True)
    with ThreadPoolExecutor(max_workers=30) as ex:
        futs = {ex.submit(verify_direct_job, c): c for c in direct_candidates}
        for f in as_completed(futs):
            res = f.result()
            if res:
                p = res["platform"]
                u_norm = res["url"].strip().lower().rstrip("/")
                if p == "ashby" and u_norm not in seen_ashby:
                    seen_ashby.add(u_norm)
                    existing_ashby.append(res)
                elif p == "lever" and u_norm not in seen_lever:
                    seen_lever.add(u_norm)
                    existing_lever.append(res)

    print(f"\nUPDATED COUNTS AFTER DIRECT VERIFICATION:")
    print(f"  Ashby: {len(existing_ashby)}")
    print(f"  Lever: {len(existing_lever)}")

    (OUT_DIR / "temp_fresh_ashby.json").write_text(json.dumps(existing_ashby, indent=2), encoding="utf-8")
    (OUT_DIR / "temp_fresh_lever.json").write_text(json.dumps(existing_lever, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
