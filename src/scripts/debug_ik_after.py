from playwright.sync_api import sync_playwright
import time
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
URL = "https://jobs.ashbyhq.com/interview-kickstart/bf2a4802-4180-440b-b5bf-5f8058e69846/application"
RESUME_PATH = str(ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000, wait_until="networkidle")
    time.sleep(1)

    # Fill
    page.locator("input[name='_systemfield_name']").fill("Jay Singh")
    time.sleep(0.3)
    page.locator("input[name='_systemfield_email']").fill("jays.iitkgp@gmail.com")
    time.sleep(0.3)
    page.locator("input[name='82e7e933-38d5-4aba-810c-64d4d59071a2']").fill("+918651274328")
    time.sleep(0.3)
    page.locator("input[type='file']").last.set_input_files(RESUME_PATH)
    time.sleep(2.5)
    page.locator("input[name='20e78471-63af-4dc5-89bf-1af575c592f6']").fill("https://linkedin.com/in/jay-singh-ds/")
    time.sleep(0.5)

    # Click submit
    print("Clicking submit button...")
    sub_btn = page.locator("button:has-text('Submit Application')")
    sub_btn.click()
    time.sleep(8)

    print("Post-submit URL:", page.url)
    snap_path = ROOT / "src" / "accessability_snapshot" / "ik_post_submit_debug.png"
    page.screenshot(path=str(snap_path), full_page=True)
    print(f"Captured screenshot to {snap_path}")

    # Inspect text
    body = page.locator("body").inner_text()
    for line in body.split("\n"):
        if any(w in line.lower() for w in ["thank", "success", "error", "invalid", "required", "spam", "robot", "captcha"]):
            print("Line of interest:", line.strip())

    browser.close()
