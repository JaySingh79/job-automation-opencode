from playwright.sync_api import sync_playwright
import time

URL = "https://jobs.ashbyhq.com/interview-kickstart/bf2a4802-4180-440b-b5bf-5f8058e69846/application"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000, wait_until="networkidle")
    time.sleep(1)

    inp6 = page.locator("input[name='20e78471-63af-4dc5-89bf-1af575c592f6']")
    if inp6.count() > 0:
        print("Input 6 type:", inp6.get_attribute("type"))
        print("Input 6 placeholder:", inp6.get_attribute("placeholder"))
        print("Input 6 label:", inp6.evaluate("el => el.closest('div,label')?.innerText"))

    browser.close()
