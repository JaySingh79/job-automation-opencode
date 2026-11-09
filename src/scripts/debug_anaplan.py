from playwright.sync_api import sync_playwright
import time

URL = "https://job-boards.greenhouse.io/anaplan/jobs/8571200002"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000)
    time.sleep(2)

    invalid = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('input:required, select:required, textarea:required')).map(el => ({
            id: el.id,
            name: el.name,
            type: el.type,
            label: el.closest('div, label')?.innerText?.slice(0, 80)
        }));
    }''')
    print("Required fields on Anaplan:")
    for inv in invalid:
        print(" ", inv)

    browser.close()
