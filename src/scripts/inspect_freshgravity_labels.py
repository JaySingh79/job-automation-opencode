import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://orbit.freshgravity.net/apply/9CEE6CDED9", wait_until="domcontentloaded", timeout=20000)
    time.sleep(2)
    inputs = page.locator("input:visible, textarea:visible, select:visible")
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        # get preceding label or text
        label_text = inp.evaluate("""el => {
            let label = el.closest('label');
            if (label) return label.innerText;
            let parent = el.parentElement;
            if (parent) {
                let prev = el.previousElementSibling;
                if (prev) return prev.innerText;
                return parent.innerText;
            }
            return '';
        }""")
        placeholder = inp.get_attribute("placeholder") or ""
        typ = inp.get_attribute("type") or ""
        print(f"[{i}] type={typ} placeholder='{placeholder}' label='{label_text.strip().replace(chr(10), ' ')}'")
    page.close()
    browser.close()
