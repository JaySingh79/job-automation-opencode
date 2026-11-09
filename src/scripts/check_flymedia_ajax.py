import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://flymediatech.com/apply-for-job/", wait_until="networkidle", timeout=20000)
    time.sleep(4)
    opts = page.locator("select").first.locator("option").all_inner_texts()
    print("Flymedia options after wait:", opts)
    page.close()
    browser.close()
