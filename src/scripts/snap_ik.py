from playwright.sync_api import sync_playwright
import time
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
URL = "https://jobs.ashbyhq.com/interview-kickstart/bf2a4802-4180-440b-b5bf-5f8058e69846/application"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000, wait_until="networkidle")
    time.sleep(2)
    page.screenshot(path=str(ROOT / "src" / "accessability_snapshot" / "interview_kickstart_form.png"), full_page=True)
    print("Screenshot saved to interview_kickstart_form.png")
    browser.close()
