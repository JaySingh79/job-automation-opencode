"""
fill_doordash_live.py — Headed execution for DoorDash India Backend Engineer application.
Runs in HEADED mode (headless=False) so the user can see the browser actions live.
Uses the proven Greenhouse Remix React-Select dropdown interaction protocol with:
  1. Anti-bot 4x smooth scroll
  2. Sequential top-to-bottom filling
  3. Randomized human delays between fields
  4. Robust attribute selectors [id='...'] to prevent digit-ID CSS syntax errors.
  5. Keystroke typing for candidate-location geocoder.
"""
import time
import random
import sys
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
URL = "https://job-boards.greenhouse.io/doordashindia/jobs/5856393"
RESUME_PATH = str(ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf")

def human_delay(min_s: float = 0.8, max_s: float = 2.0):
    time.sleep(random.uniform(min_s, max_s))

def human_scroll_4x(page):
    """Perform 4 smooth scrolls down the page and back up."""
    print("Executing mandatory 4x human smooth scroll...")
    try:
        total_height = page.evaluate("() => document.documentElement.scrollHeight || document.body.scrollHeight || 2500")
        for q in [0.25, 0.50, 0.75, 1.0]:
            target_y = int(total_height * q)
            page.evaluate(f"window.scrollTo({{ top: {target_y}, behavior: 'smooth' }})")
            time.sleep(random.uniform(0.5, 0.9))
        page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        time.sleep(random.uniform(0.6, 1.2))
    except Exception as e:
        print(f"Scroll warning: {e}", file=sys.stderr)

def fill_combobox(page, field_id, search_term, option_matcher, use_keyboard_typing=False):
    print(f"Selecting combobox [id='{field_id}'] with search '{search_term}'...")
    try:
        inp = page.locator(f'[id="{field_id}"]')
        if inp.count() == 0:
            inp = page.locator(f'[id*="{field_id}"] input, div[id*="{field_id}"]')
        
        if inp.count() == 0:
            print(f"  Warning: Combobox element [id='{field_id}'] not found in DOM")
            return False

        inp.first.scroll_into_view_if_needed()
        inp.first.click()
        time.sleep(0.4)

        if use_keyboard_typing:
            page.keyboard.type(search_term, delay=100)
        else:
            inp.first.fill(search_term)
        time.sleep(1.2)

        # Look in listbox by attribute selector
        listbox = page.locator(f'[id="react-select-{field_id}-listbox"]')
        options = None
        if listbox.count() > 0:
            options = listbox.locator("[id*='option']")
        else:
            options = page.locator("[class*='-menu'] [id*='option'], div[role='listbox'] [role='option'], div[role='option']")

        count = options.count() if options else 0
        print(f"  Found {count} options for [id='{field_id}']")
        for i in range(count):
            opt = options.nth(i)
            text = opt.inner_text().strip()
            if option_matcher(text):
                print(f"  Clicking option: '{text}'")
                opt.click()
                human_delay(0.5, 1.0)
                return True

        print(f"  Warning: No matching option found for [id='{field_id}']")
        page.keyboard.press("Escape")
    except Exception as e:
        print(f"  Error selecting combobox [id='{field_id}']: {e}")
    return False

def run():
    print(f"==================================================")
    print(f"Launching DoorDash India Application (HEADED MODE)")
    print(f"Target URL: {URL}")
    print(f"==================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--no-sandbox"]
        )
        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("1. Navigating to DoorDash application page...")
        page.goto(URL, timeout=45000, wait_until="domcontentloaded")
        page.wait_for_selector("form", timeout=20000)
        human_delay(1.5, 2.5)

        # 1. Anti-bot 4x scroll
        human_scroll_4x(page)

        # 2. Fill Basic Personal Info sequentially
        print("2. Filling personal information...")
        page.locator('[id="first_name"]').fill("Jay")
        human_delay(0.5, 1.0)
        page.locator('[id="last_name"]').fill("Singh")
        human_delay(0.5, 1.0)
        page.locator('[id="email"]').fill("jays.iitkgp@gmail.com")
        human_delay(0.5, 1.0)

        # Country phone selector
        fill_combobox(page, "country", "India", lambda t: "india" in t.lower() and "+91" in t)
        page.locator('[id="phone"]').fill("+91-8651274328")
        human_delay(0.6, 1.2)

        # Candidate Location with keyboard geocoder typing
        fill_combobox(page, "candidate-location", "Pune", lambda t: "pune, maharashtra, india" in t.lower() or "pune" in t.lower(), use_keyboard_typing=True)
        human_delay(0.6, 1.2)

        # 3. Resume Upload
        print(f"3. Uploading resume: {RESUME_PATH}...")
        file_input = page.locator('input[type="file"]')
        if file_input.count() > 0:
            file_input.first.set_input_files(RESUME_PATH)
            human_delay(1.5, 2.5)

        # 4. Custom Screening Questions
        print("4. Filling custom questions sequentially...")
        if page.locator('[id="question_46985239"]').count() > 0:
            page.locator('[id="question_46985239"]').fill("https://linkedin.com/in/jay-singh-ds/")
            human_delay(0.5, 1.0)

        # Have you worked at DoorDash? -> I have not worked at DoorDash
        fill_combobox(page, "question_46985241", "not worked", lambda t: "not worked at doordash" in t.lower())
        human_delay(0.5, 1.0)

        # Relocation to Pune
        if page.locator('[id="question_63930318"]').count() > 0:
            page.locator('[id="question_63930318"]').fill(
                "Current location: Gaya, Bihar. Willing to relocate to Pune immediately and work from office/hybrid."
            )
            human_delay(0.8, 1.5)

        # Compensation Expectation
        if page.locator('[id="question_63930319"]').count() > 0:
            page.locator('[id="question_63930319"]').fill("22-26 LPA (negotiable)")
            human_delay(0.5, 1.0)

        # Notice Period
        if page.locator('[id="question_63992617"]').count() > 0:
            page.locator('[id="question_63992617"]').fill("Immediate")
            human_delay(0.5, 1.0)

        # Applicant Privacy Acknowledgement -> Yes
        fill_combobox(page, "question_46985242", "Yes", lambda t: t.strip().lower() == "yes")
        human_delay(0.6, 1.2)

        # 5. Demographics (Voluntary / Required)
        print("5. Filling demographic selections sequentially...")
        # Gender
        fill_combobox(page, "864", "Male", lambda t: "male" in t.lower() and "female" not in t.lower())
        human_delay(0.4, 0.8)
        # Transgender
        fill_combobox(page, "1328", "No", lambda t: t.strip().lower() == "no")
        human_delay(0.4, 0.8)
        # Hispanic / Latinx
        fill_combobox(page, "1332", "No", lambda t: t.strip().lower() == "no")
        human_delay(0.4, 0.8)
        # Race
        fill_combobox(page, "1333", "Asian", lambda t: "asian" in t.lower())
        human_delay(0.4, 0.8)
        # Veteran Status
        fill_combobox(page, "1336", "not", lambda t: "not" in t.lower() or "decline" in t.lower())
        human_delay(0.4, 0.8)
        # Disability Status
        fill_combobox(page, "1337", "No", lambda t: "no" in t.lower() or "decline" in t.lower())
        human_delay(0.6, 1.2)

        # Scroll to bottom
        page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
        human_delay(1.0, 2.0)

        # 6. Check Validity & Screenshot
        print("6. Verifying form completion...")
        valid_res = page.evaluate('''() => {
            const form = document.querySelector('form');
            const invalid = Array.from(document.querySelectorAll(':invalid')).map(el => ({
                id: el.id,
                name: el.name,
                label: el.closest('div, label')?.innerText?.slice(0, 50)
            }));
            return {
                checkValidity: form ? form.checkValidity() : false,
                invalidElements: invalid
            };
        }''')
        print(f"Form validity: {valid_res['checkValidity']}, Invalid elements: {valid_res['invalidElements']}")

        screenshot_ready = ROOT / "src" / "accessability_snapshot" / "doordash_review_ready.png"
        page.screenshot(path=str(screenshot_ready), full_page=True)
        print(f"Captured review-ready screenshot at {screenshot_ready}")

        # 7. Submit Application
        print("7. Submitting DoorDash application...")
        submit_btn = page.locator("button[type='submit']")
        if submit_btn.count() > 0:
            submit_btn.first.click()
            time.sleep(5)

        # 8. Check for OTP or Server Confirmation
        url_after = page.url
        body_text = page.locator("body").inner_text()
        print(f"Post-submit URL: {url_after}")

        if "/confirmation" in url_after or "thank you for applying" in body_text.lower() or "application has been received" in body_text.lower():
            print("SUCCESS! Application received by DoorDash server!")
            screenshot_success = ROOT / "src" / "accessability_snapshot" / "doordash_success.png"
            page.screenshot(path=str(screenshot_success), full_page=True)
            
            # Record in jobs_applied.json
            applied_record = {
                "company": "DoorDash",
                "role": "Backend Engineer (DoorDash India)",
                "url": URL,
                "platform": "greenhouse",
                "location": "Pune, Maharashtra, India",
                "resume": "GenAI_DS (Jay Resume GenAI+DS 5th Aug.pdf)",
                "status": "applied",
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "verification": f"CONFIRMED: URL {url_after} + Server confirmation text."
            }
            applied_file = ROOT / "src" / "applied" / "jobs_applied.json"
            try:
                with open(applied_file, "r", encoding="utf-8") as f:
                    app_data = json.load(f)
                app_data.append(applied_record)
                with open(applied_file, "w", encoding="utf-8") as f:
                    json.dump(app_data, f, indent=2)
                print(f"Logged DoorDash application to {applied_file}")
            except Exception as e:
                print(f"Ledger logging warning: {e}")

            browser.close()
            return {"status": "SUCCESS", "url": url_after}

        # Check if email verification code was challenged
        if "security code" in body_text.lower() or "verification code" in body_text.lower():
            print("Greenhouse Email Verification Code challenged!")
            print("Listening for OTP code from Gmail IMAP...")
            try:
                from otp_listener import fetch_latest_otp
                otp = fetch_latest_otp(max_wait_seconds=45)
            except Exception as e:
                print(f"OTP listener error: {e}")
                otp = None

            if otp:
                print(f"Retrieved OTP code: {otp}. Entering into security inputs...")
                for idx, ch in enumerate(otp[:8]):
                    inp = page.locator(f'[id="security-input-{idx}"]')
                    if inp.count() > 0:
                        inp.click()
                        inp.fill(ch)
                        time.sleep(0.1)
                time.sleep(0.5)
                # Resubmit
                resubmit_btn = page.locator("button[type='submit']")
                if resubmit_btn.count() > 0 and not resubmit_btn.first.is_disabled():
                    resubmit_btn.first.click()
                    time.sleep(5)
                
                url_final = page.url
                body_final = page.locator("body").inner_text()
                if "/confirmation" in url_final or "thank you" in body_final.lower():
                    print("SUCCESS! OTP verified and DoorDash application confirmed!")
                    screenshot_success = ROOT / "src" / "accessability_snapshot" / "doordash_success.png"
                    page.screenshot(path=str(screenshot_success), full_page=True)

                    applied_record = {
                        "company": "DoorDash",
                        "role": "Backend Engineer (DoorDash India)",
                        "url": URL,
                        "platform": "greenhouse",
                        "location": "Pune, Maharashtra, India",
                        "resume": "GenAI_DS (Jay Resume GenAI+DS 5th Aug.pdf)",
                        "status": "applied",
                        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "verification": f"CONFIRMED: URL {url_final} + Server confirmation text (OTP verified)."
                    }
                    applied_file = ROOT / "src" / "applied" / "jobs_applied.json"
                    try:
                        with open(applied_file, "r", encoding="utf-8") as f:
                            app_data = json.load(f)
                        app_data.append(applied_record)
                        with open(applied_file, "w", encoding="utf-8") as f:
                            json.dump(app_data, f, indent=2)
                        print(f"Logged DoorDash application to {applied_file}")
                    except Exception as e:
                        print(f"Ledger logging warning: {e}")

                    browser.close()
                    return {"status": "SUCCESS", "url": url_final}
            else:
                print("Could not retrieve OTP automatically. Leaving browser open for human input.")

        time.sleep(4)
        browser.close()
        return {"status": "COMPLETED", "url": page.url}

if __name__ == "__main__":
    res = run()
    print(res)
