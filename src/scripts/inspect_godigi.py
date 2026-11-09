import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.godigiinfotech.com/job-detail/ai-software-engineer/148", wait_until="domcontentloaded", timeout=20000)
    time.sleep(2)
    print("Page title:", page.title())
    apply_btns = page.locator("a:has-text('Apply'), button:has-text('Apply')")
    print("Apply buttons count:", apply_btns.count())
    for i in range(apply_btns.count()):
        btn = apply_btns.nth(i)
        print(f"[{i}] text='{btn.inner_text().strip()}' href='{btn.get_attribute('href')}'")
    page.close()
    browser.close()
