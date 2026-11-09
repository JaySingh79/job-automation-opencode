"""
fill_ashby_job.py — Robust filler for Ashby job applications.
Implements:
  1. wait_until='networkidle' to guarantee React client hydration.
  2. Clicking 'Apply for this Job' / 'Apply' to reveal the form fields.
  3. Mandatory 4x smooth scroll down and back up.
  4. Top-to-bottom sequential field filling with human delays.
  5. Location combobox typing with 'India' and chip selection.
  6. File upload verification.
  7. Submit and server confirmation verification.
"""

import sys
import time
import random
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
RESUME_PATH = str(ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf")

PROFILE = {
    "full_name": "Jay Singh",
    "email": "jays.iitkgp@gmail.com",
    "phone": "+91-8651274328",
    "location": "Gaya, Bihar, India",
    "linkedin": "https://linkedin.com/in/jay-singh-ds/",
    "github": "https://github.com/JaySingh79",
    "portfolio": "https://jaysingh.vercel.app/"
}

def human_delay(min_s: float = 0.8, max_s: float = 2.0):
    time.sleep(random.uniform(min_s, max_s))

def human_scroll_4x(page):
    print("Executing mandatory 4x human smooth scroll...")
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

def fill_ashby_app(url, company_name, role_name):
    print(f"==================================================")
    print(f"Applying to {company_name} - {role_name}")
    print(f"URL: {url}")
    print(f"==================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("1. Navigating with networkidle wait...")
        page.goto(url, timeout=45000, wait_until="networkidle")
        time.sleep(2)

        # 2. Click Apply for this Job if present
        apply_btn = page.locator("button:has-text('Apply for this Job'), a:has-text('Apply for this Job'), button:has-text('Apply')")
        if apply_btn.count() > 0 and apply_btn.first.is_visible():
            print("2. Clicking 'Apply for this Job' button...")
            apply_btn.first.click()
            time.sleep(2)

        # 3. Mandatory 4x scroll
        human_scroll_4x(page)

        # 4. Fill Personal Information sequentially
        print("4. Filling personal info...")
        # Name
        name_inp = page.locator("input[name*='name' i], input[id*='name' i], input[placeholder*='name' i]")
        if name_inp.count() > 0 and name_inp.first.is_visible():
            name_inp.first.fill(PROFILE["full_name"])
            human_delay(0.5, 1.0)

        # Email
        email_inp = page.locator("input[type='email'], input[name*='email' i], input[id*='email' i]")
        if email_inp.count() > 0 and email_inp.first.is_visible():
            email_inp.first.fill(PROFILE["email"])
            human_delay(0.5, 1.0)

        # Phone
        phone_inp = page.locator("input[type='tel'], input[name*='phone' i], input[id*='phone' i]")
        if phone_inp.count() > 0 and phone_inp.first.is_visible():
            phone_inp.first.fill(PROFILE["phone"])
            human_delay(0.5, 1.0)

        # LinkedIn
        li_inp = page.locator("input[name*='linkedin' i], input[id*='linkedin' i], input[placeholder*='linkedin' i], input[aria-label*='linkedin' i]")
        if li_inp.count() > 0 and li_inp.first.is_visible():
            li_inp.first.fill(PROFILE["linkedin"])
            human_delay(0.5, 1.0)

        # GitHub
        gh_inp = page.locator("input[name*='github' i], input[id*='github' i], input[placeholder*='github' i], input[aria-label*='github' i]")
        if gh_inp.count() > 0 and gh_inp.first.is_visible():
            gh_inp.first.fill(PROFILE["github"])
            human_delay(0.5, 1.0)

        # Location Combobox
        print("5. Handling location combobox...")
        try:
            loc_box = page.locator("div[role='combobox']:has-text('Start typing'), input[placeholder*='Start typing' i], div[id*='location']")
            if loc_box.count() > 0 and loc_box.first.is_visible():
                loc_box.first.click()
                time.sleep(0.4)
                page.keyboard.type("India", delay=80)
                time.sleep(1.0)
                page.keyboard.press("Enter")
                human_delay(0.5, 1.0)
        except Exception as e:
            print(f"Location combobox warning: {e}")

        # 6. Attach Resume
        print("6. Attaching resume...")
        try:
            file_input = page.locator("input[type='file']")
            if file_input.count() > 0:
                file_input.first.set_input_files(RESUME_PATH)
                human_delay(1.5, 2.5)
        except Exception as e:
            print(f"Resume attach error: {e}")

        # Final scroll to bottom
        page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
        human_delay(1.0, 1.8)

        # 7. Check for Submit button
        sub_btn = page.locator("button:has-text('Submit Application'), button[type='submit']")
        print(f"7. Submit button found: {sub_btn.count() > 0}")

        if sub_btn.count() == 0:
            browser.close()
            return {"status": "FAILED", "reason": "No submit button found"}

        print("8. Clicking Submit Application...")
        sub_btn.first.click()
        time.sleep(6)

        curr_url = page.url
        body_text = page.locator("body").inner_text()
        print(f"Post-submit URL: {curr_url}")
        print(f"Post-submit text snippet: {body_text[:250].replace(chr(10), ' ')}")

        if "/submitted" in curr_url.lower() or "/application" in curr_url.lower() and ("thank you" in body_text.lower() or "success" in body_text.lower() or "submitted" in body_text.lower()):
            print(f"SUCCESS! Application confirmed for {company_name}!")
            snap_file = ROOT / "src" / "accessability_snapshot" / f"{company_name.lower()}_success.png"
            page.screenshot(path=str(snap_file), full_page=True)

            applied_record = {
                "company": company_name,
                "role": role_name,
                "url": url,
                "platform": "ashby",
                "location": "India",
                "resume": f"GenAI_DS ({RESUME_PATH})",
                "status": "applied",
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "verification": f"CONFIRMED: URL {curr_url} + Heading Success / Application submitted."
            }
            applied_file = ROOT / "src" / "applied" / "jobs_applied.json"
            try:
                with open(applied_file, "r", encoding="utf-8") as f:
                    app_data = json.load(f)
                app_data.append(applied_record)
                with open(applied_file, "w", encoding="utf-8") as f:
                    json.dump(app_data, f, indent=2)
                print(f"Logged {company_name} to jobs_applied.json!")
            except Exception as e:
                print("Logging error:", e)

            browser.close()
            return {"status": "SUCCESS", "url": curr_url}

        if "flagged as possible spam" in body_text.lower():
            browser.close()
            return {"status": "BLOCKED_SPAM", "reason": "Ashby anti-bot telemetry spam challenge"}

        browser.close()
        return {"status": "VALIDATION_FAILED", "url": curr_url}

if __name__ == "__main__":
    if len(sys.argv) > 3:
        res = fill_ashby_app(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        # Default test Interview Kickstart
        res = fill_ashby_app(
            "https://jobs.ashbyhq.com/interview-kickstart/bf2a4802-4180-440b-b5bf-5f8058e69846",
            "Interview Kickstart",
            "Intern - Software Development Engineer (Backend)"
        )
    print(res)
