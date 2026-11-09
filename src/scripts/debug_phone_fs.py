from playwright.sync_api import sync_playwright
import time

URL = "https://job-boards.greenhouse.io/bswiftindia/jobs/4699956006"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000)
    time.sleep(2)

    phone_fieldset = page.locator("fieldset:has-text('Phone')")
    print("Phone fieldset HTML:")
    print(phone_fieldset.evaluate("el => el.outerHTML"))

    browser.close()
