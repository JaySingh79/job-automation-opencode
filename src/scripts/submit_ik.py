from playwright.sync_api import sync_playwright
import time
import random
import json
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
RESUME_PATH = str(ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf")
URL = "https://jobs.ashbyhq.com/interview-kickstart/bf2a4802-4180-440b-b5bf-5f8058e69846/application"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    print("1. Navigating to Ashby /application...")
    page.goto(URL, timeout=40000, wait_until="networkidle")
    time.sleep(2)

    # 4x Scroll
    print("2. 4x Scroll...")
    for q in [0.25, 0.5, 0.75, 1.0]:
        page.evaluate(f"window.scrollTo({{ top: document.body.scrollHeight * {q}, behavior: 'smooth' }})")
        time.sleep(0.4)
    page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
    time.sleep(0.5)

    # Fill fields
    print("3. Filling fields sequentially...")
    page.locator("input[name*='name']").first.fill("Jay Singh")
    time.sleep(0.8)
    page.locator("input[type='email'], input[name*='email']").first.fill("jays.iitkgp@gmail.com")
    time.sleep(0.8)
    page.locator("input[placeholder*='1234'], input[type='tel']").first.fill("+918651274328")
    time.sleep(0.8)

    # Resume upload
    print("4. Attaching resume...")
    file_input = page.locator("input[type='file'][name*='resume'], input[type='file']")
    if file_input.count() > 0:
        file_input.last.set_input_files(RESUME_PATH)
        time.sleep(2.5)

    # LinkedIn
    li_inp = page.locator("input[name='20e78471-63af-4dc5-89bf-1af575c592f6'], input[placeholder*='Type here']")
    if li_inp.count() > 0:
        li_inp.last.fill("https://linkedin.com/in/jay-singh-ds/")
        time.sleep(0.8)

    # Scroll to bottom
    page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
    time.sleep(1)

    # Screenshot before submit
    page.screenshot(path=str(ROOT / "src" / "accessability_snapshot" / "ik_review_ready.png"), full_page=True)

    # Submit
    print("5. Clicking Submit Application...")
    sub_btn = page.locator("button:has-text('Submit Application')")
    sub_btn.first.click()
    time.sleep(6)

    print("Post-submit URL:", page.url)
    body_text = page.locator("body").inner_text()
    print("Post-submit body snippet:", body_text[:300].replace("\n", " "))

    if "/submitted" in page.url or "thank you" in body_text.lower() or "success" in body_text.lower() or "submitted" in body_text.lower():
        print("SUCCESS! Interview Kickstart received application!")
        page.screenshot(path=str(ROOT / "src" / "accessability_snapshot" / "ik_success.png"), full_page=True)
        applied_file = ROOT / "src" / "applied" / "jobs_applied.json"
        try:
            with open(applied_file, "r", encoding="utf-8") as f:
                app_data = json.load(f)
            app_data.append({
                "company": "Interview Kickstart",
                "role": "Intern - Software Development Engineer ( Backend )",
                "url": URL,
                "platform": "ashby",
                "location": "Remote - India",
                "resume": f"GenAI_DS ({RESUME_PATH})",
                "status": "applied",
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "verification": f"CONFIRMED: URL {page.url} + Server confirmation text."
            })
            with open(applied_file, "w", encoding="utf-8") as f:
                json.dump(app_data, f, indent=2)
            print("Logged Interview Kickstart to jobs_applied.json!")
        except Exception as e:
            print("Logging error:", e)

    browser.close()
