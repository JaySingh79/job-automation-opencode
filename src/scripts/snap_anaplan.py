from playwright.sync_api import sync_playwright
import time
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
URL = "https://job-boards.greenhouse.io/anaplan/jobs/8571200002"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    from test_smart_greenhouse import fill_greenhouse_smart
    fill_greenhouse_smart(page)
    time.sleep(3)
    page.screenshot(path=str(ROOT / "src" / "accessability_snapshot" / "anaplan_post_submit.png"), full_page=True)
    print("Screenshot saved to anaplan_post_submit.png")
    print("Final URL:", page.url)
    browser.close()
