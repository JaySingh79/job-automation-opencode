from playwright.sync_api import sync_playwright
import time

URL = "https://job-boards.greenhouse.io/coherehealth/jobs/7693298003"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000)
    time.sleep(3)

    invalid = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('input:required, select:required, textarea:required')).map(el => ({
            id: el.id,
            name: el.name,
            type: el.type,
            label: el.closest('div, label')?.innerText?.slice(0, 70)
        }));
    }''')
    print("Required fields on Cohere Health:")
    for inv in invalid:
        print(" ", inv)

    browser.close()
