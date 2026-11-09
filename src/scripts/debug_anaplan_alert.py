from playwright.sync_api import sync_playwright
import time

URL = "https://job-boards.greenhouse.io/anaplan/jobs/8571200002"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000)
    time.sleep(2)
    # Check if there are error banners or alerts
    alerts = page.locator("[role='alert'], .error, .alert, [class*='error'], [class*='flash']")
    print("Alerts found:", alerts.count())
    for i in range(alerts.count()):
        print("  -", alerts.nth(i).inner_text().strip())
    browser.close()
