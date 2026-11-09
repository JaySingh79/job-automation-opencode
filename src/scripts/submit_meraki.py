from playwright.sync_api import sync_playwright
import time
import json
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
URL = "https://jobs.ashbyhq.com/meraki-labs/38e05386-b0ac-4c63-9780-5ec391a116be/application"
RESUME_PATH = str(ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    print("Navigating to Meraki Labs /application...")
    page.goto(URL, timeout=40000, wait_until="networkidle")
    time.sleep(1)

    # 4x Scroll
    for q in [0.25, 0.5, 0.75, 1.0]:
        page.evaluate(f"window.scrollTo({{ top: document.body.scrollHeight * {q}, behavior: 'smooth' }})")
        time.sleep(0.4)
    page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
    time.sleep(0.5)

    # Fill
    print("Filling Name & Email...")
    page.locator("input[name='_systemfield_name']").fill("Jay Singh")
    time.sleep(0.8)
    page.locator("input[name='_systemfield_email']").fill("jays.iitkgp@gmail.com")
    time.sleep(0.8)

    # Attach resume
    print("Attaching Resume...")
    page.locator("input[type='file']").last.set_input_files(RESUME_PATH)
    time.sleep(2.5)

    # Scroll
    page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
    time.sleep(1)

    # Submit
    print("Clicking Submit...")
    sub_btn = page.locator("button:has-text('Submit Application')")
    sub_btn.click()
    time.sleep(6)

    print("Post-submit URL:", page.url)
    body_text = page.locator("body").inner_text()
    print("Post-submit text snippet:", body_text[:300].replace("\n", " "))

    if "/submitted" in page.url or "thank you" in body_text.lower() or "success" in body_text.lower() or "submitted" in body_text.lower():
        print("SUCCESS! Meraki Labs received application!")
        page.screenshot(path=str(ROOT / "src" / "accessability_snapshot" / "meraki_success.png"), full_page=True)
        applied_file = ROOT / "src" / "applied" / "jobs_applied.json"
        try:
            with open(applied_file, "r", encoding="utf-8") as f:
                app_data = json.load(f)
            app_data.append({
                "company": "Meraki Labs",
                "role": "Research Associate - SparX",
                "url": URL,
                "platform": "ashby",
                "location": "Bangalore, India",
                "resume": f"GenAI_DS ({RESUME_PATH})",
                "status": "applied",
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "verification": f"CONFIRMED: URL {page.url} + Server confirmation text."
            })
            with open(applied_file, "w", encoding="utf-8") as f:
                json.dump(app_data, f, indent=2)
            print("Logged Meraki Labs to jobs_applied.json!")
        except Exception as e:
            print("Logging error:", e)

    browser.close()
