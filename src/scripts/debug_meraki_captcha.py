from playwright.sync_api import sync_playwright
import time
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
URL = "https://jobs.ashbyhq.com/meraki-labs/38e05386-b0ac-4c63-9780-5ec391a116be/application"
RESUME_PATH = str(ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000, wait_until="networkidle")
    time.sleep(1)

    page.locator("input[name='_systemfield_name']").fill("Jay Singh")
    time.sleep(0.3)
    page.locator("input[name='_systemfield_email']").fill("jays.iitkgp@gmail.com")
    time.sleep(0.3)
    page.locator("input[type='file']").last.set_input_files(RESUME_PATH)
    time.sleep(2.5)

    sub_btn = page.locator("button:has-text('Submit Application')")
    sub_btn.click()
    time.sleep(5)

    snap = ROOT / "src" / "accessability_snapshot" / "meraki_post_submit.png"
    page.screenshot(path=str(snap), full_page=True)
    print("Screenshot saved to meraki_post_submit.png")

    frames = page.frames
    print(f"Total iframes: {len(frames)}")
    for f in frames:
        if "recaptcha" in f.url or "google.com/recaptcha" in f.url:
            print("  Found reCAPTCHA frame:", f.url[:60])

    browser.close()
