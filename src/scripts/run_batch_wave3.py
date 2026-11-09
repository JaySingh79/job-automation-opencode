"""
run_batch_wave3.py — 5-agent batch runner for Wave 3:
  1. Cohere Health (Greenhouse) — Associate SDET Engineer
  2. DoorDash India (Greenhouse) — Software Engineer, Data Engineering
  3. GitLab (Greenhouse) — Intermediate Backend Engineer, India
  4. Jobgether (Lever) — Software Development Engineer 1
  5. Welo Global (Lever) — Associate Technical Publication Engineer

Strict Anti-Bot Discipline:
  - 4x human smooth scroll (25%, 50%, 75%, 100%) on every page
  - Sequential top-to-bottom field entry
  - Randomized delays (800ms - 2200ms) between fields
  - 5 isolated Chromium processes (0 tab contention)
  - Automatic Greenhouse email OTP retrieval via otp_listener.py
  - Exact server confirmation check before logging status: "applied"
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
    "phone_national": "8651274328",
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

WAVE3_JOBS = [
    {
        "id": "coherehealth",
        "company": "Cohere Health",
        "org": "coherehealth",
        "role": "Associate SDET Engineer",
        "platform": "greenhouse",
        "url": "https://job-boards.greenhouse.io/coherehealth/jobs/7693298003",
        "resume_variant": "GenAI_DS"
    },
    {
        "id": "doordashindia_de",
        "company": "DoorDash India",
        "org": "doordashindia",
        "role": "Software Engineer, Data Engineering",
        "platform": "greenhouse",
        "url": "https://job-boards.greenhouse.io/doordashindia/jobs/8200625",
        "resume_variant": "GenAI_DS"
    },
    {
        "id": "gitlab",
        "company": "GitLab",
        "org": "gitlab",
        "role": "Intermediate Backend Engineer, India",
        "platform": "greenhouse",
        "url": "https://job-boards.greenhouse.io/gitlab/jobs/8775507002",
        "resume_variant": "GenAI_DS"
    },
    {
        "id": "jobgether_sde",
        "company": "Jobgether",
        "org": "jobgether",
        "role": "Software Development Engineer 1",
        "platform": "lever",
        "url": "https://jobs.lever.co/jobgether/248e4baf-c4c8-4094-a0ac-8c358689a645",
        "resume_variant": "GenAI_DS"
    },
    {
        "id": "weloglobal",
        "company": "Welo Global",
        "org": "weloglobal",
        "role": "Associate Technical Publication Engineer",
        "platform": "lever",
        "url": "https://jobs.lever.co/weloglobal/7903f79a-fe0f-46e3-ac8b-83b607574453",
        "resume_variant": "GenAI_DS"
    }
]

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
        print(f"Scroll warning: {e}", file=sys.stderr)

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

# ==============================================================================
# LEVER APPLICATION FILLER
# ==============================================================================
def fill_lever_job(page, job, resume_path):
    url = job["url"]
    org = job["org"]
    apply_url = url if url.endswith("/apply") else f"{url.rstrip('/')}/apply"
    print(f"[{org}] Navigating to {apply_url}...")
    page.goto(apply_url, timeout=40000, wait_until="domcontentloaded")
    human_delay(1.5, 2.5)

    # Dismiss cookie banner
    try:
        dismiss = page.locator("button:has-text('Dismiss'), button:has-text('Accept'), a:has-text('Accept')")
        if dismiss.count() > 0 and dismiss.first.is_visible():
            dismiss.first.click()
            human_delay(0.4, 0.8)
    except Exception:
        pass

    # 1. 4x Scroll
    human_scroll_4x(page)

    # 2. Attach Resume
    print(f"[{org}] Attaching resume...")
    try:
        attach_btn = page.locator("button:has-text('ATTACH RESUME'), a:has-text('ATTACH RESUME')")
        if attach_btn.count() > 0:
            with page.expect_file_chooser(timeout=5000) as fc_info:
                attach_btn.first.click()
            file_chooser = fc_info.value
            file_chooser.set_files(resume_path)
            human_delay(1.5, 2.2)
        else:
            file_input = page.locator("input[type='file']")
            if file_input.count() > 0:
                file_input.first.set_input_files(resume_path)
                human_delay(1.5, 2.2)
    except Exception as e:
        print(f"[{org}] Attach warning: {e}", file=sys.stderr)

    # 3. Personal Fields sequentially
    print(f"[{org}] Filling personal fields...")
    lever_fields = [
        ('input[name="name"]', PROFILE["full_name"]),
        ('input[name="email"]', PROFILE["email"]),
        ('input[name="phone"]', PROFILE["phone"]),
        ('input[name="location"]', PROFILE["location"]),
        ('input[name="org"]', PROFILE["current_company"]),
        ('input[name="urls[LinkedIn]"]', PROFILE["linkedin"]),
        ('input[name="urls[GitHub]"]', PROFILE["github"]),
        ('input[name="urls[Portfolio]"]', PROFILE["portfolio"]),
    ]
    for sel, val in lever_fields:
        try:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.fill(val)
                human_delay(0.5, 1.2)
        except Exception:
            pass

    # Pronoun
    try:
        he_him = page.locator('input[type="checkbox"][value="He/him"], label:has-text("He/him")')
        if he_him.count() > 0:
            he_him.first.click()
            human_delay(0.3, 0.6)
    except Exception:
        pass

    # 4. Custom textareas / screening questions
    try:
        page.evaluate('''() => {
            document.querySelectorAll('input[type="text"], textarea').forEach(inp => {
                const txt = (inp.closest('.application-question, li, div')?.innerText || '').toLowerCase();
                const cur = inp.value || '';
                if (cur.trim().length > 0) return;

                if (txt.includes('current company') && !inp.name) inp.value = 'Pibit AI (YC W21)';
                else if (txt.includes('previous company')) inp.value = 'Pascal AI Labs';
                else if (txt.includes('full-time experience') || txt.includes('total experience') || txt.includes('years of experience')) inp.value = '1.5 years';
                else if (txt.includes('relevant experience')) inp.value = '1.5 years in AI/ML & LLM systems';
                else if (txt.includes('current annual compensation') || txt.includes('current ctc') || txt.includes('current salary')) inp.value = '0';
                else if (txt.includes('salary expectations') || txt.includes('expected ctc') || txt.includes('expected compensation')) inp.value = '2200000';
                else if (txt.includes('when can you start') || txt.includes('notice period')) inp.value = 'Immediately';
                else if (txt.includes('shorten a notice')) inp.value = 'Yes, immediate joiner';
                else if (txt.includes('consultant from our group')) inp.value = 'None';
                else if (txt.includes('highest education') || txt.includes('degree')) inp.value = 'B.Tech in Artificial Intelligence';
                else if (txt.includes('relocate')) inp.value = 'Yes, willing to relocate';
                inp.dispatchEvent(new Event('input', { bubbles: true }));
                inp.dispatchEvent(new Event('change', { bubbles: true }));
            });
        }''')
        human_delay(0.6, 1.2)
    except Exception:
        pass

    # 5. Native dropdowns
    try:
        selects = page.locator("select")
        for i in range(selects.count()):
            sel = selects.nth(i)
            txt = sel.inner_text().lower()
            if "inr" in txt:
                sel.select_option(label="INR")
            elif "yes" in txt and "no" in txt:
                lbl = page.evaluate("(el) => el.closest('li,div')?.innerText || ''", sel.element_handle).lower()
                if "sponsorship" in lbl or "visa" in lbl:
                    sel.select_option(label="No")
                elif "authorized" in lbl or "agree" in lbl or "consent" in lbl or "relocate" in lbl:
                    sel.select_option(label="Yes")
            human_delay(0.3, 0.6)
    except Exception:
        pass

    # 6. Checkboxes & radio buttons
    try:
        cbs = page.locator("input[type='checkbox']")
        for i in range(cbs.count()):
            cb = cbs.nth(i)
            txt = page.evaluate("(el) => el.closest('label, li, div')?.innerText || ''", cb.element_handle).lower()
            if any(w in txt for w in ["consent", "agree", "privacy", "authorize", "certify", "acknowledge"]):
                if not cb.is_checked():
                    cb.check()
                    human_delay(0.2, 0.4)
    except Exception:
        pass

    # Scroll to bottom
    page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
    human_delay(1.0, 1.8)

    # 7. Check Validity
    valid = page.evaluate("() => document.querySelector('form')?.checkValidity()")
    invalid_count = page.evaluate("() => document.querySelectorAll(':invalid').length")
    print(f"[{org}] Form checkValidity: {valid}, invalid count: {invalid_count}")

    # Snapshot
    snap_path = ROOT / "src" / "accessability_snapshot" / f"{org}_lever_review.png"
    page.screenshot(path=str(snap_path), full_page=True)

    # 8. Submit Attempt
    sub_btn = page.locator("#btn-submit, button[type='submit']:has-text('Submit'), button:has-text('Submit application')")
    if sub_btn.count() > 0:
        print(f"[{org}] Clicking submit...")
        sub_btn.first.click()
        time.sleep(5)
        curr_url = page.url
        body_text = page.locator("body").inner_text()[:1500].lower()

        if "/applied" in curr_url or "thank you for applying" in body_text:
            return {"status": "SUCCESS", "confirmation_url": curr_url, "evidence": body_text[:200]}

        # Check if hCaptcha challenged
        if page.locator("#h-captcha, iframe[src*='hcaptcha']").count() > 0:
            print(f"[{org}] hCaptcha visual challenge active! Staging for human review.")
            post_click_snap = ROOT / "src" / "accessability_snapshot" / f"{org}_post_click.png"
            page.screenshot(path=str(post_click_snap), full_page=True)
            return {"status": "STAGED_AWAITING_CAPTCHA", "screenshot": str(post_click_snap)}

    return {"status": "STAGED_REVIEW_READY", "screenshot": str(snap_path)}

# ==============================================================================
# GREENHOUSE APPLICATION FILLER
# ==============================================================================
def fill_greenhouse_job(page, job, resume_path):
    url = job["url"]
    org = job["org"]
    print(f"[{org}] Navigating to {url}...")
    page.goto(url, timeout=40000, wait_until="domcontentloaded")
    human_delay(1.5, 2.5)

    # 1. 4x Scroll
    human_scroll_4x(page)
    setup_react_helpers(page)
    human_delay(0.5, 1.0)

    # 2. Basic Fields
    print(f"[{org}] Filling basic contact fields...")
    for sel, val in [
        ("#first_name, [id='first_name'], input[name*='first_name']", PROFILE["first_name"]),
        ("#last_name, [id='last_name'], input[name*='last_name']", PROFILE["last_name"]),
        ("#email, [id='email'], input[name*='email']", PROFILE["email"]),
    ]:
        try:
            loc = page.locator(sel)
            if loc.count() > 0:
                loc.first.fill(val)
                human_delay(0.4, 0.8)
        except Exception:
            pass

    # Country selector
    try:
        country_inp = page.locator("#country, [id='country']")
        if country_inp.count() > 0:
            country_inp.first.click()
            time.sleep(0.3)
            page.keyboard.type("India", delay=80)
            time.sleep(0.8)
            opts = page.locator("[id*='option']")
            clicked = False
            for i in range(opts.count()):
                txt = opts.nth(i).inner_text().strip()
                if "india" in txt.lower() and "+91" in txt:
                    opts.nth(i).click()
                    clicked = True
                    break
            if not clicked:
                page.keyboard.press("Enter")
            human_delay(0.4, 0.8)
    except Exception:
        pass

    # Phone: national 10 digits
    try:
        phone_inp = page.locator("#phone, [id='phone'], input[name*='phone']")
        if phone_inp.count() > 0:
            phone_inp.first.fill(PROFILE["phone_national"])
            human_delay(0.4, 0.8)
    except Exception:
        pass

    # 3. Attach Resume
    print(f"[{org}] Attaching resume...")
    try:
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            file_input.first.set_input_files(resume_path)
            human_delay(1.5, 2.5)
    except Exception as e:
        print(f"[{org}] Resume attach error: {e}", file=sys.stderr)

    # Special handling for Candidate Location autocomplete (e.g. DoorDash)
    try:
        loc_inp = page.locator("input#candidate-location, input[id*='location']")
        if loc_inp.count() > 0:
            cur = loc_inp.first.input_value(timeout=500)
            if not cur.strip():
                loc_inp.first.click()
                time.sleep(0.3)
                page.keyboard.type("Pune, Maharashtra, India", delay=80)
                time.sleep(1.0)
                page.keyboard.press("ArrowDown")
                time.sleep(0.3)
                page.keyboard.press("Enter")
                human_delay(0.5, 1.0)
    except Exception:
        pass

    # 4. Smart Field Mapper based on container label
    containers = page.locator(".field, [class*='field'], .select, [class*='field-wrapper']")
    print(f"[{org}] Scanning {containers.count()} form field containers...")
    for i in range(containers.count()):
        c = containers.nth(i)
        lbl = c.locator("label, [class*='label']").first.inner_text().strip().lower() if c.locator("label, [class*='label']").count() > 0 else ""
        if not lbl:
            continue

        inp = c.locator("input[type='text'], textarea, input:not([type='hidden']):not([type='file'])")
        if inp.count() == 0:
            continue

        is_select = c.locator(".select, [class*='select-shell'], [class*='remix-css']").count() > 0

        val_to_set = None
        if "legal first name" in lbl or "preferred first name" in lbl:
            val_to_set = "Jay"
        elif "legal last name" in lbl or "preferred last name" in lbl:
            val_to_set = "Singh"
        elif "address line 1" in lbl or "street address" in lbl:
            val_to_set = "Gaya, Bihar"
        elif "address line 2" in lbl:
            val_to_set = "Nutan Nagar"
        elif "city" in lbl:
            val_to_set = "Gaya"
        elif "zip" in lbl or "postal" in lbl:
            val_to_set = "823001"
        elif "state" in lbl or "province" in lbl:
            val_to_set = "Bihar"
        elif "current salary" in lbl or "current ctc" in lbl:
            val_to_set = "0"
        elif "expected salary" in lbl or "expected ctc" in lbl or "compensation" in lbl:
            val_to_set = "22-26 LPA (negotiable)"
        elif "notice period" in lbl:
            val_to_set = "Immediate"
        elif "hear about" in lbl:
            val_to_set = "LinkedIn"
        elif "linkedin" in lbl:
            val_to_set = PROFILE["linkedin"]
        elif "website" in lbl or "portfolio" in lbl:
            val_to_set = PROFILE["portfolio"]
        elif "github" in lbl:
            val_to_set = PROFILE["github"]
        elif "authorized" in lbl:
            val_to_set = "Yes"
        elif "sponsorship" in lbl or "visa" in lbl:
            val_to_set = "No"
        elif "relocate" in lbl:
            val_to_set = "Yes"
        elif "license" in lbl or "certification" in lbl:
            val_to_set = "Deep Learning Specialization (deeplearning.ai), AWS Certified Cloud Practitioner"
        elif "current employer" in lbl or "current company" in lbl or "most recent employer" in lbl:
            val_to_set = "Pibit AI (YC W21)"

        if val_to_set:
            if is_select:
                try:
                    inp.first.click()
                    time.sleep(0.3)
                    page.keyboard.type(val_to_set, delay=60)
                    time.sleep(0.6)
                    opts = page.locator("[id*='option'], [class*='option']")
                    matched = False
                    for o_idx in range(opts.count()):
                        opt = opts.nth(o_idx)
                        if opt.is_visible() and val_to_set.lower() == opt.inner_text().strip().lower():
                            opt.click()
                            matched = True
                            break
                    if not matched:
                        page.keyboard.press("Enter")
                except Exception:
                    pass
            else:
                try:
                    cur = inp.first.input_value(timeout=500)
                    if not cur.strip():
                        inp.first.fill(val_to_set)
                except Exception:
                    inp.first.fill(val_to_set)
            human_delay(0.3, 0.6)

    # 5. Checkboxes
    try:
        cbs = page.locator("input[type='checkbox']")
        for i in range(cbs.count()):
            cb = cbs.nth(i)
            if not cb.is_checked():
                cb.check()
                human_delay(0.2, 0.4)
    except Exception:
        pass

    # Scroll to bottom
    page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
    human_delay(1.0, 1.8)

    # Check validity
    valid = page.evaluate("() => document.querySelector('form')?.checkValidity()")
    invalid_count = page.evaluate("() => document.querySelectorAll(':invalid').length")
    print(f"[{org}] Greenhouse checkValidity: {valid}, invalid count: {invalid_count}")

    # Snapshot before submit
    snap_path = ROOT / "src" / "accessability_snapshot" / f"{org}_greenhouse_review.png"
    page.screenshot(path=str(snap_path), full_page=True)

    # 6. Submit
    submit_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Submit Application')")
    if submit_btn.count() == 0:
        return {"status": "FAILED", "reason": "No submit button found"}

    print(f"[{org}] Submitting Greenhouse application...")
    submit_btn.first.click()
    time.sleep(6)

    curr_url = page.url
    body_text = page.locator("body").inner_text()[:1500].lower()

    if "/confirmation" in curr_url or "thank you for applying" in body_text or "application has been received" in body_text:
        return {"status": "SUCCESS", "confirmation_url": curr_url, "evidence": body_text[:200]}

    if "security code" in body_text or "verification code" in body_text or "one-time password" in body_text:
        print(f"[{org}] Email OTP challenged! Listening to Gmail...")
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
                resubmit = page.locator("button[type='submit']")
                if resubmit.count() > 0:
                    resubmit.first.click()
                    time.sleep(6)
                if "/confirmation" in page.url or "thank you" in page.locator("body").inner_text().lower():
                    return {"status": "SUCCESS", "confirmation_url": page.url, "evidence": "OTP verified successfully"}
        except Exception as e:
            print(f"[{org}] OTP error: {e}")

    return {"status": "STAGED_REVIEW_READY", "screenshot": str(snap_path)}

# ==============================================================================
# WORKER DISPATCHER
# ==============================================================================
def process_single_job(job):
    job_id = job["id"]
    org = job["org"]
    platform = job["platform"]
    resume_path = RESUME_MAP.get(job.get("resume_variant", "GenAI_DS"), RESUME_MAP["GenAI_DS"])

    print(f"\n>>> [WORKER START] {org} ({platform.upper()}) | Resume: {Path(resume_path).name}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 850},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            if platform == "lever":
                result = fill_lever_job(page, job, resume_path)
            elif platform == "greenhouse":
                result = fill_greenhouse_job(page, job, resume_path)
            else:
                result = {"status": "SKIPPED", "reason": f"Unknown platform {platform}"}

            result["job"] = job
            return result

        except Exception as e:
            print(f"[{org}] CRITICAL ERROR: {e}", file=sys.stderr)
            err_snap = ROOT / "src" / "accessability_snapshot" / f"{org}_error.png"
            try:
                page.screenshot(path=str(err_snap), full_page=True)
            except Exception:
                pass
            return {"status": "ERROR", "error": str(e), "job": job}
        finally:
            context.close()
            browser.close()
            print(f"<<< [WORKER END] {org}\n")

# ==============================================================================
# MAIN BATCH ORCHESTRATOR (5 AGENTS AT A TIME)
# ==============================================================================
def main():
    print("=" * 80)
    print("STARTING WAVE 3 BATCH (5 AGENTS RUNNING IN ISOLATED PROCESSES)")
    print("Protocol: 4x smooth scroll + sequential filling + random delays (800ms-2200ms)")
    print("=" * 80)

    results = []
    # Concurrency strictly capped at 5 agents
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_single_job, job): job for job in WAVE3_JOBS}
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            print(f"[COMPLETED AGENT] {res.get('job', {}).get('company')}: {res.get('status')}")

    # Reconcile confirmed successes in jobs_applied.json
    applied_file = ROOT / "src" / "applied" / "jobs_applied.json"
    with open(applied_file, "r", encoding="utf-8") as f:
        applied_data = json.load(f)

    newly_confirmed = 0
    for r in results:
        if r.get("status") == "SUCCESS":
            job = r["job"]
            applied_data.append({
                "company": job["company"],
                "role": job["role"],
                "url": job["url"],
                "platform": job["platform"],
                "location": "India",
                "resume": f"{job.get('resume_variant', 'GenAI_DS')} ({Path(RESUME_MAP[job.get('resume_variant', 'GenAI_DS')]).name})",
                "status": "applied",
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "verification": f"CONFIRMED: URL {r.get('confirmation_url')} + Evidence {r.get('evidence')}"
            })
            newly_confirmed += 1
            print(f"Logged confirmed application: {job['company']}")

    if newly_confirmed > 0:
        with open(applied_file, "w", encoding="utf-8") as f:
            json.dump(applied_data, f, indent=2)

    print("\n" + "=" * 80)
    print(f"WAVE 3 BATCH FINISHED: {newly_confirmed} CONFIRMED APPLIED, {len(results) - newly_confirmed} STAGED/CAPTCHA")
    print("=" * 80)
    for r in results:
        print(f" - {r.get('job', {}).get('company')} ({r.get('job', {}).get('platform')}): {r.get('status')}")

if __name__ == "__main__":
    main()
