from playwright.sync_api import sync_playwright
import time
import json
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
URL = "https://job-boards.greenhouse.io/bswiftindia/jobs/4699956006"
RESUME_PATH = str(ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf")

def fill_bswift(page):
    print("Navigating to bswift India...")
    page.goto(URL, timeout=40000, wait_until="domcontentloaded")
    time.sleep(2)

    # 4x Scroll
    for q in [0.25, 0.5, 0.75, 1.0]:
        page.evaluate(f"window.scrollTo({{ top: document.body.scrollHeight * {q}, behavior: 'smooth' }})")
        time.sleep(0.3)
    page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
    time.sleep(0.5)

    # Basic fields
    page.locator("#first_name").fill("Jay")
    time.sleep(0.3)
    page.locator("#last_name").fill("Singh")
    time.sleep(0.3)
    page.locator("#email").fill("jays.iitkgp@gmail.com")
    time.sleep(0.3)

    # Country + phone
    country_inp = page.locator("#country")
    if country_inp.count() > 0:
        country_inp.click()
        time.sleep(0.3)
        page.keyboard.type("India", delay=80)
        time.sleep(0.8)
        opts = page.locator("[id*='option']")
        for i in range(opts.count()):
            txt = opts.nth(i).inner_text().strip()
            if "india" in txt.lower() and "+91" in txt:
                opts.nth(i).click()
                print(f"Selected country: {txt}")
                break
    page.locator("#phone").fill("8651274328")
    time.sleep(0.3)

    # Resume
    page.locator("input[type='file']").first.set_input_files(RESUME_PATH)
    time.sleep(2)

    # Smart Map custom questions
    containers = page.locator(".field, [class*='field']")
    print(f"Scanning {containers.count()} containers...")
    for i in range(containers.count()):
        c = containers.nth(i)
        lbl = c.locator("label, [class*='label']").first.inner_text().strip().lower() if c.locator("label, [class*='label']").count() > 0 else ""
        if not lbl:
            continue
        inp = c.locator("input[type='text'], textarea")
        if inp.count() == 0:
            continue

        val = None
        if "linkedin" in lbl:
            val = "https://linkedin.com/in/jay-singh-ds/"
        elif "website" in lbl:
            val = "https://jaysingh.vercel.app/"
        elif "current ctc" in lbl or "current salary" in lbl:
            val = "0"
        elif "ctc expectation" in lbl or "expected ctc" in lbl:
            val = "22-26 LPA (negotiable)"
        elif "notice period" in lbl:
            val = "Immediate"
        elif "current location" in lbl:
            val = "Gaya, Bihar"
        elif "bangalore" in lbl or "relocate" in lbl:
            val = "Currently in Gaya, Bihar. Willing to relocate to Bangalore immediately."
        elif "employer" in lbl or "company" in lbl:
            val = "Pibit AI (YC W21)"
        elif "preferred name" in lbl:
            val = "Jay"
        elif "license" in lbl or "certification" in lbl:
            val = "Deep Learning Specialization (deeplearning.ai), AWS Certified Cloud Practitioner"

        if val:
            print(f"  Setting '{lbl[:40]}' -> '{val[:30]}'")
            inp.first.fill(val)
            time.sleep(0.3)

    # Handle Bangalore relocation react-select dropdown
    bgl_inp = page.locator("#question_8585881006")
    if bgl_inp.count() > 0:
        bgl_inp.scroll_into_view_if_needed()
        time.sleep(0.4)
        control = bgl_inp.locator("xpath=ancestor::div[contains(@class, 'select__control')]")
        if control.count() > 0:
            control.first.click()
        else:
            bgl_inp.first.click()
        time.sleep(0.8)
        yes_opt = page.locator("#react-select-question_8585881006-option-0")
        if yes_opt.count() > 0:
            yes_opt.first.click()
            print("Selected 'Yes' for Bangalore relocation!")
        else:
            # Fallback search for option with text 'Yes'
            opts = page.locator("[id*='option']")
            for i in range(opts.count()):
                if opts.nth(i).inner_text().strip().lower() == "yes":
                    opts.nth(i).click()
                    print("Selected 'Yes' by option text!")
                    break
        time.sleep(0.5)

    # Check validity
    valid = page.evaluate("() => document.querySelector('form')?.checkValidity()")
    invalid_fields = page.evaluate('''() => {
        return Array.from(document.querySelectorAll(':invalid')).map(el => ({
            id: el.id,
            label: el.closest('.field, div, label')?.innerText?.slice(0, 50)
        }));
    }''')
    print(f"Form checkValidity: {valid}, Invalid elements: {invalid_fields}")

    # Submit
    sub_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Submit Application')")
    print(f"Submit button found: {sub_btn.count() > 0}")
    if valid and sub_btn.count() > 0:
        print("Submitting bswift India application...")
        sub_btn.first.click()
        time.sleep(6)
        print("Post-submit URL:", page.url)
        body_text = page.locator("body").inner_text()
        print("Post-submit text snippet:", body_text[:250].replace("\n", " "))

        if "/confirmation" in page.url or "thank you for applying" in body_text.lower() or "application has been received" in body_text.lower():
            print("SUCCESS! bswift India received application!")
            applied_file = ROOT / "src" / "applied" / "jobs_applied.json"
            try:
                with open(applied_file, "r", encoding="utf-8") as f:
                    app_data = json.load(f)
                app_data.append({
                    "company": "bswift India",
                    "role": "Software Engineer",
                    "url": URL,
                    "platform": "greenhouse",
                    "location": "Bangalore, India",
                    "resume": f"GenAI_DS ({RESUME_PATH})",
                    "status": "applied",
                    "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "verification": f"CONFIRMED: URL {page.url} + Server confirmation text."
                })
                with open(applied_file, "w", encoding="utf-8") as f:
                    json.dump(app_data, f, indent=2)
                print("Logged bswift India to jobs_applied.json!")
            except Exception as e:
                print("Logging error:", e)

        elif "security code" in body_text.lower() or "verification code" in body_text.lower():
            print("Greenhouse Email Verification Code challenged! Listening to Gmail...")
            try:
                from otp_listener import fetch_latest_otp
                otp = fetch_latest_otp(max_wait_seconds=45)
                if otp:
                    print(f"Retrieved OTP: {otp}. Entering into security inputs...")
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
                        time.sleep(5)
                    print("Post-OTP URL:", page.url)
                    if "/confirmation" in page.url or "thank you" in page.locator("body").inner_text().lower():
                        print("SUCCESS! bswift India confirmed with OTP!")
                        snap_path = ROOT / "src" / "accessability_snapshot" / "bswift_success.png"
                        page.screenshot(path=str(snap_path), full_page=True)
                        applied_file = ROOT / "src" / "applied" / "jobs_applied.json"
                        with open(applied_file, "r", encoding="utf-8") as f:
                            app_data = json.load(f)
                        app_data.append({
                            "company": "bswift India",
                            "role": "Software Engineer",
                            "url": URL,
                            "platform": "greenhouse",
                            "location": "Bangalore, India",
                            "resume": f"GenAI_DS ({RESUME_PATH})",
                            "status": "applied",
                            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "verification": f"CONFIRMED: Post-OTP URL {page.url} + Server confirmation text."
                        })
                        with open(applied_file, "w", encoding="utf-8") as f:
                            json.dump(app_data, f, indent=2)
                        print("Logged bswift India post-OTP to jobs_applied.json!")
            except Exception as e:
                print("OTP error:", e)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    fill_bswift(page)
    browser.close()
