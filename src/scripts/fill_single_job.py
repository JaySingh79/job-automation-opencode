"""
fill_single_job.py — Robust single-job application filler for Greenhouse, Lever, and Ashby.
Runs an isolated Playwright Chromium session to guarantee ZERO tab contention between parallel agents.
Properly handles React synthetic events, file attachments, and server confirmation verification.
Enforces strict anti-bot detection mitigations:
  1. Scroll 4 times on each page (25%, 50%, 75%, 100% smooth scroll).
  2. Sequential top-to-bottom field entry.
  3. Randomized human delays between fields (800ms - 2200ms) and natural typing.
"""

import argparse
import json
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
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

def human_delay(min_s: float = 0.8, max_s: float = 2.2):
    """Randomized human delay between form interactions."""
    delay = random.uniform(min_s, max_s)
    time.sleep(delay)

def human_scroll_4x(page):
    """
    Mandatory Anti-Bot Mitigation:
    Perform at least 4 natural smooth scrolls down the page (25%, 50%, 75%, 100% of viewport)
    to trigger viewport observers, lazy components, and human behavior telemetry.
    Then scroll smoothly back up to the top.
    """
    try:
        total_height = page.evaluate("() => document.documentElement.scrollHeight || document.body.scrollHeight || 2000")
        quarters = [0.25, 0.50, 0.75, 1.0]
        for q in quarters:
            target_y = int(total_height * q)
            page.evaluate(f"window.scrollTo({{ top: {target_y}, behavior: 'smooth' }})")
            time.sleep(random.uniform(0.4, 0.9))
        
        # Scroll smoothly back to top for sequential form filling
        page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        time.sleep(random.uniform(0.5, 1.0))
    except Exception as e:
        print(f"[human_scroll_4x] scroll warning: {e}", file=sys.stderr)

def setup_react_helpers(page):
    """Inject safe React synthetic event dispatchers that never fail on digit IDs."""
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

def fill_greenhouse(page, resume_path):
    # 1. Anti-bot 4x scroll
    human_scroll_4x(page)
    setup_react_helpers(page)
    human_delay(0.5, 1.2)

    # 2. Sequential Step 1: Personal Contact Information
    contact_fields = [
        ('input[aria-label*="First Name" i], input[name*="first_name"], #first_name', PROFILE["first_name"]),
        ('input[aria-label*="Last Name" i], input[name*="last_name"], #last_name', PROFILE["last_name"]),
        ('input[aria-label*="Email" i], input[name*="email"], #email', PROFILE["email"]),
        ('input[aria-label*="Phone" i], input[name*="phone"], #phone', PROFILE["phone"]),
        ('input[autocomplete*="linkedin"], input[id*="linkedin" i], input[name*="linkedin" i]', PROFILE["linkedin"]),
        ('input[id*="website" i], input[id*="portfolio" i], input[name*="website" i]', PROFILE["portfolio"]),
    ]

    for sel, val in contact_fields:
        try:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.fill(val)
                human_delay(0.6, 1.5)
        except Exception:
            pass

    # 3. Sequential Step 2: Attach Resume
    try:
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            file_input.first.set_input_files(resume_path)
            human_delay(1.2, 2.0)
    except Exception as e:
        print(f"[Greenhouse] Resume attach warning: {e}", file=sys.stderr)

    # 4. Sequential Step 3: Handle Dropdowns / Selects & Comboboxes
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
                human_delay(0.5, 1.0)
            elif "yes" in txt and "no" in txt:
                if "sponsorship" in lbl or "visa" in lbl:
                    sel.select_option(label="No")
                elif "authorized" in lbl or "relocate" in lbl or "agree" in lbl:
                    sel.select_option(label="Yes")
                human_delay(0.5, 1.0)
    except Exception:
        pass

    # Handle React-Select comboboxes (e.g. DoorDash, Cognite custom location/degree)
    try:
        combos = page.locator("input[id*='react-select']")
        for i in range(combos.count()):
            cb = combos.nth(i)
            if cb.is_visible():
                lbl = page.evaluate("(el) => el.closest('div,label')?.innerText || ''", cb.element_handle).lower()
                if "location" in lbl or "country" in lbl:
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
                if (cur.trim().length > 0) return; // don't overwrite

                if (lbl.includes('most recent employer') || lbl.includes('current company') || lbl.includes('current organization')) {
                    window.setReactInput(el, 'Pibit AI (YC W21)');
                } else if (lbl.includes('most recent job title') || lbl.includes('current title') || lbl.includes('current role')) {
                    window.setReactInput(el, 'AI Intern (Research)');
                } else if (lbl.includes('salary expectation') || lbl.includes('expected compensation')) {
                    window.setReactInput(el, '22-26 LPA (negotiable)');
                } else if (lbl.includes('notice period')) {
                    window.setReactInput(el, 'Immediate');
                } else if (lbl.includes('years of experience') || lbl.includes('total experience')) {
                    window.setReactInput(el, '1.5');
                } else if (lbl.includes('why do you want') || lbl.includes('what interests you')) {
                    window.setReactInput(el, 'I am excited by your engineering challenges, modern tech stack, and rapid growth. My experience building production GenAI pipelines and agentic workflows directly aligns with this role.');
                }
            });
        }''')
        human_delay(0.8, 1.5)
    except Exception:
        pass

    # 6. Sequential Step 5: Mandatory Consent Checkboxes
    try:
        checkboxes = page.locator("input[type='checkbox']")
        for i in range(checkboxes.count()):
            cb = checkboxes.nth(i)
            lbl = page.evaluate("(el) => el.closest('div,label')?.innerText || ''", cb.element_handle).lower()
            if "agree" in lbl or "consent" in lbl or "acknowledge" in lbl or "privacy" in lbl or "terms" in lbl:
                if not cb.is_checked():
                    cb.check()
                    human_delay(0.3, 0.7)
    except Exception:
        pass

    # Final scroll to bottom before submission
    page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
    human_delay(1.0, 2.0)

    # 7. Submit Application
    submit_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Submit Application')")
    if submit_btn.count() == 0:
        return {"status": "FAILED", "reason": "No submit button found"}

    submit_btn.first.click()
    time.sleep(5)

    # 8. Server-side Confirmation Verification
    curr_url = page.url
    body_text = page.locator("body").inner_text()[:1500].lower()

    if "confirmation" in curr_url.lower() or "thank you for applying" in body_text or "application has been received" in body_text:
        return {"status": "SUCCESS", "confirmation_url": curr_url, "evidence": body_text[:200]}
    
    if "security code" in body_text or "verification code" in body_text or "one-time password" in body_text:
        return {"status": "OTP_REQUIRED", "reason": "Email verification code requested by Greenhouse"}

    if "captcha" in body_text or "recaptcha" in body_text:
        return {"status": "CAPTCHA_REQUIRED", "reason": "reCAPTCHA challenged"}

    return {"status": "VALIDATION_FAILED", "url": curr_url, "reason": "Form remained on page after submit (check unfilled required fields)"}

def fill_lever(page, resume_path):
    apply_url = page.url if page.url.endswith("/apply") else f"{page.url.rstrip('/')}/apply"
    page.goto(apply_url, timeout=30000, wait_until="domcontentloaded")
    human_delay(1.5, 2.5)

    # 1. Anti-bot 4x scroll
    human_scroll_4x(page)

    # Dismiss cookie banner
    try:
        dismiss = page.locator("button:has-text('Dismiss'), button:has-text('Accept')")
        if dismiss.count() > 0 and dismiss.first.is_visible():
            dismiss.first.click()
            human_delay(0.4, 0.8)
    except Exception:
        pass

    # 2. Sequential Step 1: Attach Resume
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
        print(f"[Lever] Attach error: {e}", file=sys.stderr)

    # 3. Sequential Step 2: Personal Contact Fields
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
                human_delay(0.6, 1.4)
        except Exception:
            pass

    # Pronoun checkbox
    try:
        he_him = page.locator('input[type="checkbox"][value="He/him"], label:has-text("He/him")')
        if he_him.count() > 0:
            he_him.first.click()
            human_delay(0.3, 0.6)
    except Exception:
        pass

    # 4. Sequential Step 3: Custom Questions
    try:
        page.evaluate('''() => {
            document.querySelectorAll('input[type="text"], textarea').forEach(inp => {
                const txt = (inp.closest('.application-question, li, div')?.innerText || '').toLowerCase();
                const cur = inp.value || '';
                if (cur.trim().length > 0) return;

                if (txt.includes('current company') && !inp.name) inp.value = 'Pibit AI (YC W21)';
                else if (txt.includes('previous company')) inp.value = 'Pascal AI Labs';
                else if (txt.includes('full-time experience') || txt.includes('total experience')) inp.value = '1.5 years';
                else if (txt.includes('relevant experience')) inp.value = '1.5 years in AI/ML & LLM systems';
                else if (txt.includes('current annual compensation') || txt.includes('current ctc')) inp.value = '0';
                else if (txt.includes('salary expectations') || txt.includes('expected ctc')) inp.value = '2200000';
                else if (txt.includes('when can you start') || txt.includes('notice period')) inp.value = 'Immediately';
                else if (txt.includes('shorten a notice')) inp.value = 'Yes, immediate joiner';
                else if (txt.includes('consultant from our group')) inp.value = 'None';
                inp.dispatchEvent(new Event('input', { bubbles: true }));
                inp.dispatchEvent(new Event('change', { bubbles: true }));
            });
        }''')
        human_delay(0.8, 1.5)
    except Exception:
        pass

    # Native dropdowns
    try:
        selects = page.locator("select")
        for i in range(selects.count()):
            sel = selects.nth(i)
            txt = sel.inner_text().lower()
            if "inr" in txt:
                sel.select_option(label="INR")
            elif "annual" in txt:
                sel.select_option(label="Annual")
            elif "gross" in txt:
                sel.select_option(label="gross")
            elif "linkedin job post" in txt:
                sel.select_option(label="LinkedIn job post")
            elif "india" in txt:
                sel.select_option(label="India")
            human_delay(0.4, 0.8)
    except Exception:
        pass

    # 5. Check if hCaptcha is present on Lever
    body_text_pre = page.locator("body").inner_text()[:2000].lower()
    if "hcaptcha" in body_text_pre or page.locator("#h-captcha, iframe[src*='hcaptcha']").count() > 0:
        # Lever hCaptcha is present: stage cleanly without triggering visual puzzle
        return {
            "status": "CAPTCHA_REQUIRED",
            "reason": "hCaptcha detected on Lever form; staged ready for human submission"
        }

    # 6. Submit Application
    submit_btn = page.locator("button[type='submit'], #btn-submit, button:has-text('Submit application')")
    if submit_btn.count() == 0:
        return {"status": "FAILED", "reason": "No submit button found"}

    submit_btn.first.click()
    time.sleep(5)

    curr_url = page.url
    body_text = page.locator("body").inner_text()[:1500].lower()

    if "/applied" in curr_url.lower() or "thank you for applying" in body_text:
        return {"status": "SUCCESS", "confirmation_url": curr_url, "evidence": body_text[:200]}

    if "hcaptcha" in body_text or "captcha" in body_text:
        return {"status": "CAPTCHA_REQUIRED", "reason": "hCaptcha challenged on Lever post-click"}

    return {"status": "VALIDATION_FAILED", "url": curr_url, "reason": "Form remained on page after submit"}

def fill_ashby(page, resume_path):
    human_delay(1.5, 2.5)

    # Check if there's an Apply tab/button to reveal form
    try:
        apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply for this job')")
        if apply_btn.count() > 0 and apply_btn.first.is_visible():
            apply_btn.first.click()
            human_delay(1.0, 1.8)
    except Exception:
        pass

    # 1. Anti-bot 4x scroll (Crucial for Ashby to prevent reCAPTCHA spam flag)
    human_scroll_4x(page)
    setup_react_helpers(page)
    human_delay(0.5, 1.2)

    # 2. Sequential Step 1: Personal Contact Information
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
                human_delay(0.6, 1.4)
        except Exception:
            pass

    # 3. Location Combobox
    try:
        loc_box = page.locator("div[role='combobox']:has-text('Start typing'), input[placeholder*='Start typing' i]")
        if loc_box.count() > 0 and loc_box.first.is_visible():
            loc_box.first.click()
            page.keyboard.type("India")
            time.sleep(0.8)
            page.keyboard.press("Enter")
            human_delay(0.6, 1.2)
    except Exception:
        pass

    # 4. Sequential Step 2: Attach Resume
    try:
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            file_input.first.set_input_files(resume_path)
            human_delay(1.5, 2.5)
    except Exception as e:
        print(f"[Ashby] Resume attach warning: {e}", file=sys.stderr)

    # Final scroll to bottom before submit
    page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
    human_delay(1.0, 2.0)

    # 5. Submit Application
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
        return {"status": "CAPTCHA_REQUIRED", "reason": "Submission flagged by anti-bot spam/captcha telemetry"}

    return {"status": "VALIDATION_FAILED", "url": curr_url, "reason": "Form remained on page after submit"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--platform", default="")
    parser.add_argument("--resume", default="GenAI_DS")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode")
    args = parser.parse_args()

    url = args.url
    platform = args.platform
    if not platform:
        if "greenhouse.io" in url:
            platform = "greenhouse"
        elif "lever.co" in url:
            platform = "lever"
        elif "ashbyhq.com" in url or "ashby.com" in url:
            platform = "ashby"

    resume_path = RESUME_MAP.get(args.resume, RESUME_MAP["GenAI_DS"])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto(url, timeout=35000, wait_until="domcontentloaded")
            if platform == "greenhouse":
                res = fill_greenhouse(page, resume_path)
            elif platform == "lever":
                res = fill_lever(page, resume_path)
            elif platform == "ashby":
                res = fill_ashby(page, resume_path)
            else:
                res = {"status": "FAILED", "reason": f"Unknown platform: {platform}"}
        except Exception as e:
            res = {"status": "ERROR", "error": f"{type(e).__name__}: {str(e)[:150]}"}
        finally:
            browser.close()

    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
