from playwright.sync_api import sync_playwright
import time

URL = "https://jobs.ashbyhq.com/interview-kickstart/bf2a4802-4180-440b-b5bf-5f8058e69846/application"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000, wait_until="networkidle")
    time.sleep(2)

    print("Title:", page.title())
    inputs = page.locator("input, textarea, select")
    print(f"Total inputs on /application: {inputs.count()}")
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        if inp.is_visible():
            name = inp.get_attribute("name") or inp.get_attribute("id") or inp.get_attribute("type")
            lbl = inp.evaluate("(el) => el.closest('div,label')?.innerText || ''").strip().replace("\n", " ")
            print(f"  Visible input {i+1}: name='{name}' label='{lbl[:50]}'")

    btns = page.locator("button")
    print("Buttons on /application:")
    for i in range(btns.count()):
        b = btns.nth(i)
        if b.is_visible():
            print(f"  Button: '{b.inner_text().strip()}'")

    browser.close()
