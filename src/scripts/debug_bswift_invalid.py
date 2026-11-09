from playwright.sync_api import sync_playwright
import time

URL = "https://job-boards.greenhouse.io/bswiftindia/jobs/4699956006"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000)
    time.sleep(2)

    invalids = page.evaluate('''() => {
        return Array.from(document.querySelectorAll(':invalid')).map(el => ({
            tag: el.tagName,
            id: el.id,
            name: el.name,
            label: el.closest('.field, div, label')?.innerText?.slice(0, 100)
        }));
    }''')
    print("Invalid elements on bswift India:")
    for inv in invalids:
        print(" ", inv)

    browser.close()
