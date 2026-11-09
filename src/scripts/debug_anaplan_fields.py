from playwright.sync_api import sync_playwright
import time

URL = "https://job-boards.greenhouse.io/anaplan/jobs/8571200002"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000)
    time.sleep(2)

    combos = page.locator("[class*='control'], div[role='combobox'], [class*='container']")
    print(f"Total potential combobox containers: {combos.count()}")

    # Let's inspect all fields inside form
    fields = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.field, [class*="field"], [data-field]')).map(el => {
            const label = el.querySelector('label, [class*="label"]')?.innerText || '';
            const input = el.querySelector('input, select, textarea');
            return {
                label: label.trim().replace(/\\n/g, ' '),
                id: input ? input.id : '',
                name: input ? input.name : '',
                type: input ? input.type : '',
                hasReactSelect: el.innerHTML.includes('react-select')
            };
        });
    }''')
    for f in fields:
        if f['label']:
            print(f)

    browser.close()
