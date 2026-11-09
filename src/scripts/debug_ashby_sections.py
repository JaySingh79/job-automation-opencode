from playwright.sync_api import sync_playwright
import time

URL = "https://jobs.ashbyhq.com/interview-kickstart/bf2a4802-4180-440b-b5bf-5f8058e69846/application"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000, wait_until="networkidle")
    time.sleep(1)

    sections = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('form > div, div[class*="field"], div[class*="Question"]')).map(el => {
            const text = el.innerText || '';
            const inps = Array.from(el.querySelectorAll('input, textarea')).map(i => i.name || i.type);
            return { text: text.trim().replace(/\\n/g, ' -- '), inputs: inps };
        }).filter(x => x.inputs.length > 0);
    }''')
    for s in sections:
        print(s)

    browser.close()
