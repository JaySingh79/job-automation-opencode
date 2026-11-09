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
    page.locator("input[type='file'][name*='resume']").set_input_files(RESUME_PATH)
    time.sleep(1.5)
    page.locator("input[name='20e78471-63af-4dc5-89bf-1af575c592f6']").fill("https://linkedin.com/in/jay-singh-ds/")
    time.sleep(0.5)

    # Click submit
    sub_btn = page.locator("button:has-text('Submit Application')")
    sub_btn.click()
    time.sleep(4)

    # Check for invalid elements or error alerts
    errors = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('[class*="error"], [class*="Error"], [role="alert"], :invalid')).map(el => ({
            tag: el.tagName,
            className: el.className,
            text: el.innerText
        }));
    }''')
    print("Post-click errors/alerts:", errors)
    page.screenshot(path=str(ROOT / "src" / "accessability_snapshot" / "ik_post_submit_debug.png"), full_page=True)
    browser.close()
