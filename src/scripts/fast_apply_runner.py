"""
fast_apply_runner.py — High-speed autonomous application runner for 100 fresh jobs
across Ashby, Lever, and Greenhouse under full submit authority.
Single-tab sequential execution: Navigate -> Fill -> Attach Resume -> Submit -> Verify -> Close Tab -> Next.
In-memory state accumulator: Zero mid-way pausing for file updates.
Atomic persistence post-run: Appends to src/applied/jobs_applied.json and updates progress files.
"""

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
JOBS_FILE = ROOT / "src" / "job_search_results" / "2026-10-18-fresh-100-ashby-lever-greenhouse.json"
AUTH_FILE = ROOT / "src" / "submit_permisssions" / "fresh100_submit_authority_2026-10-18.json"
APPLIED_LEDGER = ROOT / "src" / "applied" / "jobs_applied.json"
PROGRESS_SUMMARY = ROOT / "src" / "application_progress" / "2026-10-18-session-summary.json"

PROFILE = {
    "first_name": "Jay",
    "last_name": "Singh",
    "full_name": "Jay Singh",
    "email": "jays.iitkgp@gmail.com",
    "phone": "+91-8651274328",
    "phone_digits": "8651274328",
    "location": "Gaya, Bihar, India",
    "city": "Gaya",
    "state": "Bihar",
    "country": "India",
    "current_company": "Pibit AI (YC W21)",
    "linkedin": "https://linkedin.com/in/jay-singh-ds/",
    "github": "https://github.com/JaySingh79",
    "portfolio": "https://jaysingh.vercel.app/",
    "experience_years": "1.5",
    "experience_months": "18",
    "notice_period": "Immediate",
    "expected_ctc": "22-26 LPA (negotiable)",
    "expected_ctc_numeric": "22",
    "current_ctc": "0",
    "authorized_in_india": "Yes",
    "needs_sponsorship": "No",
    "relocate": "Yes",
    "gender": "Male"
}

RESUMES = {
    "GenAI_DS": str(ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf"),
    "ML_Vision": str(ROOT / "Resumes" / "Resume ML_Vision 5th Aug.pdf"),
    "ML_Vision_RL": str(ROOT / "Resumes" / "Resume ML_Vision_RL_PPO 7th Aug.pdf")
}

def check_authority():
    if not AUTH_FILE.exists():
        raise RuntimeError("Submit authority file missing!")
    auth = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
    if not auth.get("allow_submit"):
        raise RuntimeError("Submit authority allow_submit is not True!")
    print("Submit authority verified: TRUE")

def fill_greenhouse(page: Page, job: dict) -> dict:
    url = job["url"]
    resume_path = RESUMES.get(job.get("resume_variant", "GenAI_DS"), RESUMES["GenAI_DS"])
    
    # Check if page is on apply form or need to click Apply
    page.goto(url, timeout=30000, wait_until="domcontentloaded")
    time.sleep(2)
    
    # 1. Personal textboxes
    if page.locator("#first_name").count() > 0:
        page.fill("#first_name", PROFILE["first_name"])
    if page.locator("#last_name").count() > 0:
        page.fill("#last_name", PROFILE["last_name"])
    if page.locator("#email").count() > 0:
        page.fill("#email", PROFILE["email"])
    if page.locator("#phone").count() > 0:
        page.fill("#phone", PROFILE["phone"])
        
    # Generic attribute selectors for greenhouse
    for sel, val in [
        ("input[name*='first_name']", PROFILE["first_name"]),
        ("input[name*='last_name']", PROFILE["last_name"]),
        ("input[name*='email']", PROFILE["email"]),
        ("input[name*='phone']", PROFILE["phone"]),
    ]:
        try:
            if page.locator(sel).count() > 0 and not page.locator(sel).first.input_value():
                page.locator(sel).first.fill(val)
        except Exception:
            pass

    # 2. Resume upload
    file_inputs = page.locator("input[type='file']")
    if file_inputs.count() > 0:
        try:
            file_inputs.first.set_input_files(resume_path)
            time.sleep(1)
        except Exception as e:
            print(f"    Resume attach error: {e}")

    # 3. Custom screening questions
    # LinkedIn
    for sel in ["input[autocomplete*='linkedin']", "input[aria-label*='LinkedIn' i]", "input[id*='linkedin' i]"]:
        try:
            if page.locator(sel).count() > 0 and not page.locator(sel).first.input_value():
                page.locator(sel).first.fill(PROFILE["linkedin"])
        except Exception:
            pass

    # Location / City
    for sel in ["input[aria-label*='Location' i]", "input[id*='location' i]"]:
        try:
            if page.locator(sel).count() > 0 and not page.locator(sel).first.input_value():
                page.locator(sel).first.fill(PROFILE["location"])
        except Exception:
            pass

    # Dropdowns / Comboboxes
    try:
        selects = page.locator("select")
        for i in range(selects.count()):
            sel = selects.nth(i)
            text_all = sel.inner_text().lower()
            if "india" in text_all:
                for opt in sel.locator("option").all():
                    if "india" in opt.inner_text().lower():
                        sel.select_option(value=opt.get_attribute("value"))
                        break
            elif "yes" in text_all and "no" in text_all:
                # check question label
                lbl = ""
                try:
                    lbl = page.evaluate("(el) => el.closest('div,label')?.innerText || ''", sel.element_handle).lower()
                except Exception:
                    pass
                if "sponsorship" in lbl or "visa" in lbl:
                    for opt in sel.locator("option").all():
                        if opt.inner_text().strip().lower() == "no":
                            sel.select_option(value=opt.get_attribute("value"))
                            break
                elif "authorized" in lbl or "relocate" in lbl or "agree" in lbl:
                    for opt in sel.locator("option").all():
                        if opt.inner_text().strip().lower() == "yes":
                            sel.select_option(value=opt.get_attribute("value"))
                            break
    except Exception:
        pass

    # Country react-select if present
    try:
        country_input = page.locator("input[required]:not([name]):not([id])")
        if country_input.count() > 0 and country_input.first.is_visible():
            country_input.first.fill("India")
            time.sleep(0.5)
            page.keyboard.press("Enter")
    except Exception:
        pass

    # 4. Submit
    submit_btn = None
    for btn_sel in ["button[type='submit']", "input[type='submit']", "#submit_app", "button:has-text('Submit Application')"]:
        if page.locator(btn_sel).count() > 0 and page.locator(btn_sel).first.is_visible():
            submit_btn = page.locator(btn_sel).first
            break
            
    if not submit_btn:
        return {"status": "skipped", "reason": "No visible submit button found"}
        
    submit_btn.click()
    time.sleep(4)
    
    # 5. Verify confirmation
    current_url = page.url
    body_text = page.locator("body").inner_text()[:1000].lower()
    
    confirmed = any(term in current_url.lower() or term in body_text for term in [
        "confirmation", "thank you", "application has been received", "received your application", "landed safely"
    ])
    
    return {
        "status": "applied" if confirmed else "submitted_unconfirmed",
        "confirmation_url": current_url,
        "verification_evidence": body_text[:200]
    }

def fill_lever(page: Page, job: dict) -> dict:
    url = job["url"]
    resume_path = RESUMES.get(job.get("resume_variant", "GenAI_DS"), RESUMES["GenAI_DS"])
    
    # Ensure URL ends in /apply if direct posting page
    apply_url = url if url.endswith("/apply") else f"{url.rstrip('/')}/apply"
    page.goto(apply_url, timeout=30000, wait_until="domcontentloaded")
    time.sleep(2)
    
    # 1. Textboxes
    if page.locator("input[name='name']").count() > 0:
        page.fill("input[name='name']", PROFILE["full_name"])
    if page.locator("input[name='email']").count() > 0:
        page.fill("input[name='email']", PROFILE["email"])
    if page.locator("input[name='phone']").count() > 0:
        page.fill("input[name='phone']", PROFILE["phone"])
    if page.locator("input[name='org']").count() > 0:
        page.fill("input[name='org']", PROFILE["current_company"])
    if page.locator("input[name='urls[LinkedIn]']").count() > 0:
        page.fill("input[name='urls[LinkedIn]']", PROFILE["linkedin"])
    if page.locator("input[name='urls[GitHub]']").count() > 0:
        page.fill("input[name='urls[GitHub]']", PROFILE["github"])
    if page.locator("input[name='urls[Portfolio]']").count() > 0:
        page.fill("input[name='urls[Portfolio]']", PROFILE["portfolio"])
        
    # Location
    if page.locator("input[name='location']").count() > 0:
        page.fill("input[name='location']", PROFILE["location"])

    # 2. Resume upload
    file_input = page.locator("input[type='file']")
    if file_input.count() > 0:
        try:
            file_input.first.set_input_files(resume_path)
            time.sleep(1.5)
        except Exception as e:
            print(f"    Resume attach error: {e}")

    # Re-fill location after upload (Lever bug)
    if page.locator("input[name='location']").count() > 0:
        page.fill("input[name='location']", PROFILE["location"])

    # 3. Custom dropdowns & radios
    try:
        selects = page.locator("select")
        for i in range(selects.count()):
            sel = selects.nth(i)
            text_all = sel.inner_text().lower()
            if "india" in text_all:
                for opt in sel.locator("option").all():
                    if "india" in opt.inner_text().lower():
                        sel.select_option(value=opt.get_attribute("value"))
                        break
            elif "yes" in text_all and "no" in text_all:
                lbl = ""
                try:
                    lbl = page.evaluate("(el) => el.closest('div')?.innerText || ''", sel.element_handle).lower()
                except Exception:
                    pass
                if "sponsorship" in lbl or "visa" in lbl:
                    for opt in sel.locator("option").all():
                        if opt.inner_text().strip().lower() == "no":
                            sel.select_option(value=opt.get_attribute("value"))
                            break
                elif "authorized" in lbl or "relocate" in lbl:
                    for opt in sel.locator("option").all():
                        if opt.inner_text().strip().lower() == "yes":
                            sel.select_option(value=opt.get_attribute("value"))
                            break
    except Exception:
        pass

    # 4. Submit
    submit_btn = page.locator("#btn-submit, button[type='submit'], button:has-text('Submit application')")
    if submit_btn.count() == 0 or not submit_btn.first.is_visible():
        return {"status": "skipped", "reason": "No visible submit button found on Lever"}
        
    submit_btn.first.click()
    time.sleep(4)
    
    current_url = page.url
    body_text = page.locator("body").inner_text()[:1000].lower()
    
    confirmed = any(term in current_url.lower() or term in body_text for term in [
        "/applied", "thank you", "application submitted", "received"
    ])
    
    return {
        "status": "applied" if confirmed else "submitted_unconfirmed",
        "confirmation_url": current_url,
        "verification_evidence": body_text[:200]
    }

def fill_ashby(page: Page, job: dict) -> dict:
    url = job["url"]
    resume_path = RESUMES.get(job.get("resume_variant", "GenAI_DS"), RESUMES["GenAI_DS"])
    
    page.goto(url, timeout=30000, wait_until="domcontentloaded")
    time.sleep(2)
    
    # If there's an Apply tab / button, click it
    apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply for this job')")
    if apply_btn.count() > 0 and apply_btn.first.is_visible():
        try:
            apply_btn.first.click()
            time.sleep(1)
        except Exception:
            pass

    # 1. Inputs
    for sel, val in [
        ("input[name*='name' i]", PROFILE["full_name"]),
        ("input[name*='email' i]", PROFILE["email"]),
        ("input[name*='phone' i]", PROFILE["phone"]),
    ]:
        try:
            if page.locator(sel).count() > 0 and not page.locator(sel).first.input_value():
                page.locator(sel).first.fill(val)
        except Exception:
            pass

    # LinkedIn / URLs
    for sel in ["input[aria-label*='LinkedIn' i]", "input[id*='linkedin' i]"]:
        try:
            if page.locator(sel).count() > 0 and not page.locator(sel).first.input_value():
                page.locator(sel).first.fill(PROFILE["linkedin"])
        except Exception:
            pass

    # 2. Resume upload
    file_input = page.locator("input[type='file']")
    if file_input.count() > 0:
        try:
            file_input.first.set_input_files(resume_path)
            time.sleep(1.5)
        except Exception as e:
            print(f"    Resume attach error: {e}")

    # Location combobox
    try:
        loc_box = page.locator("div[role='combobox']:has-text('Start typing'), input[placeholder*='Start typing' i]")
        if loc_box.count() > 0 and loc_box.first.is_visible():
            loc_box.first.click()
            page.keyboard.type("India")
            time.sleep(1)
            page.keyboard.press("Enter")
    except Exception:
        pass

    # 3. Submit
    submit_btn = page.locator("button:has-text('Submit Application'), button[type='submit']")
    if submit_btn.count() == 0 or not submit_btn.first.is_visible():
        return {"status": "skipped", "reason": "No visible submit button found on Ashby"}
        
    submit_btn.first.click()
    time.sleep(4)
    
    current_url = page.url
    body_text = page.locator("body").inner_text()[:1000].lower()
    
    confirmed = any(term in current_url.lower() or term in body_text for term in [
        "/submitted", "thank you", "application submitted", "received"
    ])
    
    return {
        "status": "applied" if confirmed else "submitted_unconfirmed",
        "confirmation_url": current_url,
        "verification_evidence": body_text[:200]
    }

def main():
    print("=== HIGH SPEED FAST APPLY RUNNER START ===")
    check_authority()
    
    jobs_data = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
    jobs = jobs_data.get("jobs", [])
    print(f"Loaded {len(jobs)} jobs to apply.")
    
    # In-memory tracking lists (ZERO mid-way file writes per user instructions)
    applied_records = []
    skipped_records = []
    
    start_time = time.time()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        
        for idx, job in enumerate(jobs, 1):
            plat = job["platform"]
            org = job["org"]
            title = job["title"]
            url = job["url"]
            print(f"\n[{idx}/100] ({plat.upper()}) {org} — {title[:40]}...")
            
            page = context.new_page()
            result = None
            try:
                if plat == "greenhouse":
                    result = fill_greenhouse(page, job)
                elif plat == "lever":
                    result = fill_lever(page, job)
                elif plat == "ashby":
                    result = fill_ashby(page, job)
                else:
                    result = {"status": "skipped", "reason": f"Unknown platform {plat}"}
            except PlaywrightTimeout:
                result = {"status": "skipped", "reason": "Page load timed out"}
            except Exception as e:
                result = {"status": "skipped", "reason": f"Execution error: {type(e).__name__}: {str(e)[:100]}"}
            finally:
                page.close()
                
            status = result.get("status", "unknown")
            print(f"    Result: {status.upper()} | {result.get('reason') or result.get('confirmation_url')}")
            
            record = {
                "company": org,
                "role": title,
                "url": url,
                "platform": plat,
                "location": job.get("location", ""),
                "resume": job.get("resume_variant", "GenAI_DS"),
                "status": status,
                "applied_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "verification": result.get("verification_evidence", ""),
                "details": result
            }
            
            if status in ["applied", "submitted_unconfirmed"]:
                applied_records.append(record)
            else:
                skipped_records.append(record)
                
        browser.close()
        
    duration = time.time() - start_time
    print(f"\n=== RUN FINISHED in {duration:.1f}s ===")
    print(f"Total Applied: {len(applied_records)}")
    print(f"Total Skipped/Blocked: {len(skipped_records)}")
    
    # ATOMIC POST-RUN PERSISTENCE (Strictly after 100 jobs per user instruction)
    print("\nPersisting final records to ledgers...")
    
    # 1. Update src/applied/jobs_applied.json
    ledger_entries = []
    if APPLIED_LEDGER.exists():
        try:
            ledger_entries = json.loads(APPLIED_LEDGER.read_text(encoding="utf-8"))
            if not isinstance(ledger_entries, list):
                ledger_entries = []
        except Exception:
            ledger_entries = []
            
    for rec in applied_records:
        ledger_entries.append({
            "company": rec["company"],
            "role": rec["role"],
            "url": rec["url"],
            "platform": rec["platform"],
            "location": rec["location"],
            "resume": rec["resume"],
            "status": "applied",
            "date": rec["applied_date"],
            "verification": rec["verification"]
        })
        
    APPLIED_LEDGER.write_text(json.dumps(ledger_entries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(applied_records)} new entries to {APPLIED_LEDGER} (Total now: {len(ledger_entries)})")
    
    # 2. Update jobs file with status
    for job in jobs:
        m_app = next((r for r in applied_records if r["url"] == job["url"]), None)
        if m_app:
            job["applied"] = True
            job["applied_at"] = m_app["applied_date"]
            job["status"] = m_app["status"]
        else:
            m_skip = next((r for r in skipped_records if r["url"] == job["url"]), None)
            job["applied"] = False
            job["status"] = m_skip["status"] if m_skip else "skipped"
            job["skip_reason"] = m_skip["details"].get("reason") if m_skip else ""
            
    JOBS_FILE.write_text(json.dumps(jobs_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated {JOBS_FILE} with application statuses.")
    
    # 3. Write session summary
    summary = {
        "session_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_jobs_processed": len(jobs),
        "total_applied": len(applied_records),
        "total_skipped": len(skipped_records),
        "duration_seconds": round(duration, 1),
        "applied_jobs": applied_records,
        "skipped_jobs": skipped_records
    }
    PROGRESS_SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote session progress report to {PROGRESS_SUMMARY}")
    print("=== PIPELINE COMPLETE ===")

if __name__ == "__main__":
    main()
