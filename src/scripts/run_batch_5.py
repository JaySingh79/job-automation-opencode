"""
run_batch_5.py — Parallel batch runner for 5 concurrent job applications.
Runs up to 5 isolated Chromium browser instances concurrently to prevent any tab contention.
Enforces:
  1. Mandatory 4x human smooth scroll (25%, 50%, 75%, 100%).
  2. Sequential top-to-bottom field entry.
  3. Randomized human delays between fields (800ms - 2200ms).
  4. Server-side confirmation verification before recording success.
  5. Automatic Greenhouse email OTP retrieval if challenged.
"""

import json
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
sys.path.insert(0, str(ROOT / "src" / "scripts"))

PROFILE = {
    "first_name": "Jay",
    "last_name": "Singh",
    "full_name": "Jay Singh",
    "email": "jays.iitkgp@gmail.com",
    "phone": "+91-8651274328",
    "location": "Gaya, Bihar, India",
    "city": "Gaya",
    "state": "Bihar",
    "country": "India",
    "postal_code": "823001",
    "current_company": "Pibit AI (YC W21)",
    "previous_company": "Pascal AI Labs",
    "linkedin": "https://linkedin.com/in/jay-singh-ds/",
    "github": "https://github.com/JaySingh79",
    "portfolio": "https://jaysingh.vercel.app/",
    "experience_years": "1.5",
    "experience_months": "18",
    "expected_ctc": "22-26 LPA (negotiable)",
    "expected_ctc_numeric": "2200000",
    "current_ctc": "0",
    "notice_period": "Immediate",
    "authorized_in_india": "Yes",
    "needs_sponsorship": "No"
}

RESUME_MAP = {
    "GenAI_DS": str(ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf"),
    "ML_Vision": str(ROOT / "Resumes" / "Resume ML_Vision 5th Aug.pdf"),
    "ML_Vision_RL": str(ROOT / "Resumes" / "Resume ML_Vision_RL_PPO 7th Aug.pdf")
}

def human_delay(min_s: float = 0.8, max_s: float = 2.0):
    time.sleep(random.uniform(min_s, max_s))

def human_scroll_4x(page):
    try:
        total_height = page.evaluate("() => document.documentElement.scrollHeight || document.body.scrollHeight || 2500")
        for q in [0.25, 0.50, 0.75, 1.0]:
            target_y = int(total_height * q)
            page.evaluate(f"window.scrollTo({{ top: {target_y}, behavior: 'smooth' }})")
            time.sleep(random.uniform(0.4, 0.8))
        page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        time.sleep(random.uniform(0.5, 1.0))
    except Exception as e:
        print(f"[Scroll warning]: {e}", file=sys.stderr)

def setup_react_helpers(page):
    page.evaluate('''() => {
        window.setReactInput = (target, val) => {
            let el = null;
            if (typeof target === 'string') {
                el = document.getElementById(target) || document.querySelector(target);
            } else if (target instanceof HTMLElement) {
                el = target;
            }
            if (!el) return false;
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set
                        || Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
            if (setter) setter.call(el, val); else el.value = val;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.dispatchEvent(new FocusEvent('blur', { bubbles: true }));
            return true;
        };
    }''')

def fill_greenhouse_job(page, job, resume_path):
    url = job["url"]
    org = job.get("org", "company")
    print(f"[{org}] Navigating to {url}...")
    page.goto(url, timeout=40000, wait_until="domcontentloaded")
    human_delay(1.5, 2.5)

    # 1. 4x Scroll
    human_scroll_4x(page)
    setup_react_helpers(page)
    human_delay(0.5, 1.0)

    # 2. Sequential Step 1: Personal Info
    contact_fields = [
        ('input[aria-label*="First Name" i], input[name*="first_name"], #first_name, [id="first_name"]', PROFILE["first_name"]),
        ('input[aria-label*="Last Name" i], input[name*="last_name"], #last_name, [id="last_name"]', PROFILE["last_name"]),
        ('input[aria-label*="Email" i], input[name*="email"], #email, [id="email"]', PROFILE["email"]),
        ('input[aria-label*="Phone" i], input[name*="phone"], #phone, [id="phone"]', PROFILE["phone"]),
        ('input[autocomplete*="linkedin"], input[id*="linkedin" i], input[name*="linkedin" i]', PROFILE["linkedin"]),
        ('input[id*="website" i], input[id*="portfolio" i], input[name*="website" i]', PROFILE["portfolio"]),
    ]
    for sel, val in contact_fields:
        try:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.fill(val)
                human_delay(0.5, 1.2)
        except Exception:
            pass

    # 3. Sequential Step 2: Attach Resume
    try:
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            file_input.first.set_input_files(resume_path)
            human_delay(1.2, 2.0)
    except Exception as e:
        print(f"[{org}] Resume attach error: {e}", file=sys.stderr)

    # 4. Sequential Step 3: Native Selects & Comboboxes
    try:
        selects = page.locator("select")
        for i in range(selects.count()):
            sel = selects.nth(i)
            if not sel.is_visible():
                continue
            txt = sel.inner_text().lower()
            lbl = page.evaluate("(el) => el.closest('div,label')?.innerText || ''", sel.element_handle).lower()
            if "india" in txt:
                sel.select_option(label="India")
            elif "yes" in txt and "no" in txt:
                if "sponsorship" in lbl or "visa" in lbl:
                    sel.select_option(label="No")
                elif "authorized" in lbl or "relocate" in lbl or "agree" in lbl:
                    sel.select_option(label="Yes")
            human_delay(0.4, 0.8)
    except Exception:
        pass

    # Handle React-Select comboboxes (Country / Location / Degree)
    try:
        combos = page.locator("input[id*='react-select']")
        for i in range(combos.count()):
            cb = combos.nth(i)
            if cb.is_visible():
                lbl = page.evaluate("(el) => el.closest('div,label')?.innerText || ''", cb.element_handle).lower()
                if "location" in lbl or "country" in lbl or "state" in lbl:
                    cb.click()
                    cb.fill("India")
                    time.sleep(0.5)
                    page.keyboard.press("Enter")
                    human_delay(0.5, 1.0)
    except Exception:
        pass

    # 5. Sequential Step 4: Custom textareas & questions
    try:
        page.evaluate('''() => {
            document.querySelectorAll('input[type="text"], textarea').forEach(el => {
                const lbl = (el.closest('div,label')?.innerText || '').toLowerCase();
                const cur = el.value || '';
                if (cur.trim().length > 0) return;

                if (lbl.includes('most recent employer') || lbl.includes('current company') || lbl.includes('current organization')) {
                    window.setReactInput(el, 'Pibit AI (YC W21)');
                } else if (lbl.includes('most recent job title') || lbl.includes('current title') || lbl.includes('current role')) {
                    window.setReactInput(el, 'AI Intern (Research)');
                } else if (lbl.includes('salary expectation') || lbl.includes('expected compensation') || lbl.includes('expected ctc')) {
                    window.setReactInput(el, '22-26 LPA (negotiable)');
                } else if (lbl.includes('notice period')) {
                    window.setReactInput(el, 'Immediate');
                } else if (lbl.includes('years of experience') || lbl.includes('total experience')) {
                    window.setReactInput(el, '1.5');
                } else if (lbl.includes('why do you want') || lbl.includes('what interests you') || lbl.includes('cover letter')) {
                    window.setReactInput(el, 'I am excited by the challenging engineering work, modern tech stack, and rapid growth. My experience building production GenAI pipelines and agentic workflows directly aligns with this role.');
                }
            });
        }''')
        human_delay(0.6, 1.2)
    except Exception:
        pass

    # 6. Sequential Step 5: Checkboxes
    try:
        checkboxes = page.locator("input[type='checkbox']")
        for i in range(checkboxes.count()):
            cb = checkboxes.nth(i)
            lbl = page.evaluate("(el) => el.closest('div,label')?.innerText || ''", cb.element_handle).lower()
            if "agree" in lbl or "consent" in lbl or "acknowledge" in lbl or "privacy" in lbl or "terms" in lbl:
                if not cb.is_checked():
                    cb.check()
                    human_delay(0.2, 0.5)
    except Exception:
        pass

    # Scroll to bottom
    page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
    human_delay(0.8, 1.5)

    # 7. Submit
    submit_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Submit Application')")
    if submit_btn.count() == 0:
        return {"status": "FAILED", "reason": "No submit button found"}

    submit_btn.first.click()
    time.sleep(5)

    curr_url = page.url
    body_text = page.locator("body").inner_text()[:1500].lower()

    if "confirmation" in curr_url.lower() or "thank you for applying" in body_text or "application has been received" in body_text:
        return {"status": "SUCCESS", "confirmation_url": curr_url, "evidence": body_text[:200]}

    # Check OTP
    if "security code" in body_text or "verification code" in body_text or "one-time password" in body_text:
        print(f"[{org}] OTP challenged, querying Gmail listener...")
        try:
            from otp_listener import fetch_latest_otp
            otp = fetch_latest_otp(max_wait_seconds=45)
            if otp:
                print(f"[{org}] Entering OTP {otp}...")
                for idx, ch in enumerate(otp[:8]):
                    inp = page.locator(f'[id="security-input-{idx}"]')
                    if inp.count() > 0:
                        inp.click()
                        inp.fill(ch)
                        time.sleep(0.1)
                time.sleep(0.5)
                resub = page.locator("button[type='submit']")
                if resub.count() > 0:
                    resub.first.click()
                    time.sleep(5)
                if "/confirmation" in page.url or "thank you" in page.locator("body").inner_text().lower():
                    return {"status": "SUCCESS", "confirmation_url": page.url, "evidence": "OTP verified successfully"}
        except Exception as e:
            print(f"[{org}] OTP handling error: {e}", file=sys.stderr)
        return {"status": "OTP_REQUIRED", "reason": "Email verification code required"}

    if "captcha" in body_text:
        return {"status": "CAPTCHA_REQUIRED", "reason": "reCAPTCHA challenged"}

    return {"status": "VALIDATION_FAILED", "url": curr_url, "reason": "Form remained on page after submit"}

def fill_ashby_job(page, job, resume_path):
    url = job["url"]
    org = job.get("org", "company")
    print(f"[{org}] Navigating to {url}...")
    page.goto(url, timeout=40000, wait_until="domcontentloaded")
    human_delay(1.5, 2.5)

    # Reveal form if behind 'Apply' button
    try:
        apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply for this job')")
        if apply_btn.count() > 0 and apply_btn.first.is_visible():
            apply_btn.first.click()
            human_delay(1.0, 1.8)
    except Exception:
        pass

    # 1. 4x Scroll (Anti-bot telemetry for Ashby)
    human_scroll_4x(page)
    setup_react_helpers(page)
    human_delay(0.5, 1.0)

    # 2. Sequential Step 1: Personal Info
    ashby_fields = [
        ('input[name*="name" i]', PROFILE["full_name"]),
        ('input[name*="email" i]', PROFILE["email"]),
        ('input[name*="phone" i]', PROFILE["phone"]),
        ('input[aria-label*="LinkedIn" i]', PROFILE["linkedin"]),
        ('input[aria-label*="GitHub" i]', PROFILE["github"]),
    ]
    for sel, val in ashby_fields:
        try:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.fill(val)
                human_delay(0.5, 1.2)
        except Exception:
            pass

    # Location combobox
    try:
        loc_box = page.locator("div[role='combobox']:has-text('Start typing'), input[placeholder*='Start typing' i]")
        if loc_box.count() > 0 and loc_box.first.is_visible():
            loc_box.first.click()
            page.keyboard.type("India", delay=100)
            time.sleep(0.8)
            page.keyboard.press("Enter")
            human_delay(0.5, 1.0)
    except Exception:
        pass

    # 3. Sequential Step 2: Attach Resume
    try:
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            file_input.first.set_input_files(resume_path)
            human_delay(1.5, 2.2)
    except Exception as e:
        print(f"[{org}] Resume attach error: {e}", file=sys.stderr)

    # Scroll to bottom
    page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
    human_delay(0.8, 1.5)

    # 4. Submit
    submit_btn = page.locator("button:has-text('Submit Application'), button[type='submit']")
    if submit_btn.count() == 0:
        return {"status": "FAILED", "reason": "No submit button found"}

    submit_btn.first.click()
    time.sleep(5)

    curr_url = page.url
    body_text = page.locator("body").inner_text()[:1500].lower()

    if "/submitted" in curr_url.lower() or "thank you for your application" in body_text or "application submitted" in body_text:
        return {"status": "SUCCESS", "confirmation_url": curr_url, "evidence": body_text[:200]}

    if "flagged as possible spam" in body_text or "captcha" in body_text or "cloudflare" in body_text:
        return {"status": "CAPTCHA_REQUIRED", "reason": "Anti-bot flag / Captcha challenge"}

    return {"status": "VALIDATION_FAILED", "url": curr_url, "reason": "Form remained on page after submit"}

def run_single_job(job):
    platform = job.get("platform", "")
    url = job["url"]
    org = job.get("org", "company")
    role = job.get("title", "Software Engineer")
    resume_variant = job.get("resume_variant", "GenAI_DS")
    resume_path = RESUME_MAP.get(resume_variant, RESUME_MAP["GenAI_DS"])

    result = {"job": job, "status": "UNKNOWN"}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            if "greenhouse" in platform or "greenhouse.io" in url:
                res = fill_greenhouse_job(page, job, resume_path)
            elif "ashby" in platform or "ashbyhq.com" in url or "ashby.com" in url:
                res = fill_ashby_job(page, job, resume_path)
            else:
                res = {"status": "SKIPPED", "reason": f"Platform {platform} not supported in batch 5"}
            
            result.update(res)

            # Take snapshot if success
            if res.get("status") == "SUCCESS":
                snap_dir = ROOT / "src" / "accessability_snapshot"
                snap_dir.mkdir(parents=True, exist_ok=True)
                snap_file = snap_dir / f"{org}_success.png"
                page.screenshot(path=str(snap_file), full_page=True)

        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)[:150]
        finally:
            browser.close()

    return result

def main():
    # Target batch of 5 jobs
    batch = [
        {
            "platform": "greenhouse",
            "org": "cloudsek",
            "title": "SDE Intern - Backend",
            "location": "Bengaluru, Karnataka, India",
            "url": "https://job-boards.greenhouse.io/cloudsek/jobs/6222340004",
            "resume_variant": "GenAI_DS"
        },
        {
            "platform": "greenhouse",
            "org": "coherehealth",
            "title": "Associate SDET Engineer",
            "location": "Hyderabad, Telangana, India",
            "url": "https://job-boards.greenhouse.io/coherehealth/jobs/7693298003",
            "resume_variant": "GenAI_DS"
        },
        {
            "platform": "ashby",
            "org": "interview-kickstart",
            "title": "Intern - Software Development Engineer (Backend)",
            "location": "Remote - India",
            "url": "https://jobs.ashbyhq.com/interview-kickstart/bf2a4802-4180-440b-b5bf-5f8058e69846",
            "resume_variant": "GenAI_DS"
        },
        {
            "platform": "ashby",
            "org": "meraki-labs",
            "title": "Research Associate - SparX",
            "location": "Bangalore, India",
            "url": "https://jobs.ashbyhq.com/meraki-labs/38e05386-b0ac-4c63-9780-5ec391a116be",
            "resume_variant": "GenAI_DS"
        },
        {
            "platform": "greenhouse",
            "org": "anaplan",
            "title": "Engineer I",
            "location": "Gurugram, India",
            "url": "https://job-boards.greenhouse.io/anaplan/jobs/8571200002",
            "resume_variant": "GenAI_DS"
        }
    ]

    print(f"==================================================")
    print(f"STARTING 5-AGENT BATCH FILLING WITH ANTI-BOT RULES")
    print(f"Total jobs in batch: {len(batch)}")
    print(f"==================================================")

    results = []
    # Concurrency capped strictly at 5 agents
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(run_single_job, job): job for job in batch}
        for future in as_completed(futures):
            job = futures[future]
            try:
                res = future.result()
                results.append(res)
                print(f"[FINISHED] {job['org']} ({job['title']}): {res.get('status')} -> {res.get('confirmation_url', res.get('reason', ''))}")
            except Exception as e:
                print(f"[EXCEPTION] {job['org']}: {e}")

    # Record verified successes into jobs_applied.json
    applied_file = ROOT / "src" / "applied" / "jobs_applied.json"
    try:
        with open(applied_file, "r", encoding="utf-8") as f:
            app_data = json.load(f)
    except Exception:
        app_data = []

    success_count = 0
    for r in results:
        if r.get("status") == "SUCCESS":
            job = r["job"]
            entry = {
                "company": job["org"],
                "role": job["title"],
                "url": job["url"],
                "platform": job["platform"],
                "location": job["location"],
                "resume": f"{job['resume_variant']} ({RESUME_MAP[job['resume_variant']]})",
                "status": "applied",
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "verification": f"CONFIRMED: URL {r.get('confirmation_url')} + {r.get('evidence', 'Server confirmed')}"
            }
            app_data.append(entry)
            success_count += 1

    with open(applied_file, "w", encoding="utf-8") as f:
        json.dump(app_data, f, indent=2)

    print(f"==================================================")
    print(f"BATCH COMPLETE: {success_count}/{len(batch)} jobs successfully confirmed & logged.")
    print(f"==================================================")

if __name__ == "__main__":
    main()
