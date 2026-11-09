from playwright.sync_api import sync_playwright
import time

URL = "https://jobs.ashbyhq.com/interview-kickstart/bf2a4802-4180-440b-b5bf-5f8058e69846"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000, wait_until="networkidle")
    time.sleep(3)

    print("Title:", page.title())
    body = page.locator("body").inner_text()
    print("Body length:", len(body))
    print("Body start:", body[:300].replace("\n", " "))

    btns = page.locator("button, a:has-text('Apply')")
    print("Buttons found:")
    for i in range(btns.count()):
        b = btns.nth(i)
        if b.is_visible():
            print(f"  - '{b.inner_text().strip()}'")

    browser.close()
