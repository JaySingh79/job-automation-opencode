from playwright.sync_api import sync_playwright
import time

URL = "https://job-boards.greenhouse.io/anaplan/jobs/8571200002"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000)
    time.sleep(2)

    containers = page.locator(".field, [class*='field']")
    for i in range(containers.count()):
        c = containers.nth(i)
        lbl = c.locator("label, [class*='label']").first.inner_text().strip().lower() if c.locator("label, [class*='label']").count() > 0 else ""
        if "authorized" in lbl or "sponsorship" in lbl:
            print(f"=== {lbl[:50]} ===")
            print("Outer HTML snippet:")
            print(c.evaluate("el => el.outerHTML")[:600])

    browser.close()
