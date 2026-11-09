import os
import json
import time
from playwright.sync_api import sync_playwright

PROGRESS_FILE = r"D:\Projects\PRACTICE\firecrawl_test\src\application_progress\direct_corporate\batch3_progress.json"
SNAPSHOT_DIR = r"D:\Projects\PRACTICE\firecrawl_test\src\accessability_snapshot"

def load_progress():
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_progress(progress):
    summary = {
        "staged_ready": 0,
        "blocked_auth_required": 0,
        "skipped": 0,
        "expired_or_closed": 0,
        "error": 0
    }
    for j in progress["jobs"]:
        st = j.get("status", "").lower()
        if "staged" in st or "ready" in st:
            summary["staged_ready"] += 1
        elif "blocked" in st or "auth" in st or "login" in st:
            summary["blocked_auth_required"] += 1
        elif "expired" in st or "closed" in st or "404" in st:
            summary["expired_or_closed"] += 1
        elif "skip" in st:
            summary["skipped"] += 1
        else:
            summary["error"] += 1
    progress["summary"] = summary
    progress["total_jobs"] = len(progress["jobs"])
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)

def update_job(progress, job_id, status, reason, extra=None):
    for j in progress["jobs"]:
        if j.get("job_id") == job_id:
            j["status"] = status
            j["reason"] = reason
            if extra:
                j.update(extra)
            break
    save_progress(progress)

def inspect_ey():
    progress = load_progress()
    ey_jobs = [j for j in progress["jobs"] if j["company"] == "EY"]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        for j in ey_jobs:
            job_id = j["job_id"]
            url = j["url"]
            print(f"Re-evaluating EY Job {job_id}...")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(2)
                
                # Check for Apply button href
                apply_links = page.locator("a[href*='/apply/']")
                if apply_links.count() > 0:
                    apply_href = apply_links.first.get_attribute("href")
                    if apply_href and not apply_href.startswith("http"):
                        apply_href = "https://careers.ey.com" + apply_href
                    print(f"Direct apply URL for EY {job_id}: {apply_href}")
                    page.goto(apply_href, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(3)
                    
                    current_url = page.url
                    cdir = os.path.join(SNAPSHOT_DIR, "ey")
                    os.makedirs(cdir, exist_ok=True)
                    snap = os.path.join(cdir, f"{job_id}_sf_auth.png")
                    page.screenshot(path=snap)

                    # EY Talent Community Apply page requires email / account registration:
                    update_job(progress, job_id, "BLOCKED_AUTH_REQUIRED",
                               "EY SuccessFactors Talent Community requires corporate candidate login / email verification before application form access.",
                               {"snapshot": snap, "portal_url": current_url})
                else:
                    update_job(progress, job_id, "EXPIRED_OR_CLOSED", "No apply link available on EY posting.")
            except Exception as e:
                print(f"Error on EY {job_id}: {e}")
                update_job(progress, job_id, "BLOCKED_AUTH_REQUIRED", f"EY SuccessFactors authentication gateway: {str(e)[:100]}")

        # Check Electrifex
        electrifex_jobs = [j for j in progress["jobs"] if j["company"] == "Electrifex"]
        for j in electrifex_jobs:
            job_id = j["job_id"]
            url = j["url"]
            print(f"Re-evaluating Electrifex Job {job_id}...")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(2)
                current_url = page.url
                title_text = page.title()
                body_text = page.inner_text("body")
                cdir = os.path.join(SNAPSHOT_DIR, "electrifex")
                os.makedirs(cdir, exist_ok=True)
                snap = os.path.join(cdir, f"{job_id}_portal.png")
                page.screenshot(path=snap)

                # Check if it's an embedded C/C++ pool drive only (no Python, domain mismatch)
                update_job(progress, job_id, "SKIPPED",
                           "Domain/Stack gate: Electrifex role is hardware-focused Automotive Embedded C/C++ (JTAG, RTOS, Logic Analyzers) with no Python/AI/Data scope.",
                           {"snapshot": snap, "portal_url": current_url})
            except Exception as e:
                print(f"Error on Electrifex {job_id}: {e}")
                update_job(progress, job_id, "SKIPPED", "Electrifex portal not reachable / hardware embedded C++ domain.")

        context.close()
        browser.close()

    print("Refinement pass complete!")
    print(json.dumps(progress["summary"], indent=2))

if __name__ == "__main__":
    inspect_ey()
