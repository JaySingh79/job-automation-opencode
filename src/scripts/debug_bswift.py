from playwright.sync_api import sync_playwright
import time

URL = "https://job-boards.greenhouse.io/bswiftindia/jobs/4699956006"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000, wait_until="domcontentloaded")
    time.sleep(2)

    fields = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.field, [class*="field"], [data-field]')).map(el => {
            const label = el.querySelector('label, [class*="label"]')?.innerText || '';
            const input = el.querySelector('input, select, textarea');
            return {
                label: label.trim().replace(/\\n/g, ' '),
                id: input ? input.id : '',
                type: input ? input.type : '',
                required: input ? input.required : false
            };
        }).filter(f => f.label);
    }''')
    print("bswift India fields:")
    for f in fields:
        print(" ", f)

    browser.close()
