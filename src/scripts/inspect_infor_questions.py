from playwright.sync_api import sync_playwright

url = 'https://careers.infor.com/en/postings/0029cdab-7f9d-4a7c-b33a-c32a2fe77160/applications/new'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='domcontentloaded', timeout=25000)
    page.wait_for_timeout(2000)
    radios = page.query_selector_all("input[type='radio']")
    print(f"Total radios: {len(radios)}")
    for r in radios:
        name = r.get_attribute("name")
        val = r.get_attribute("value")
        # Find closest question container or legend
        text = r.evaluate("""el => {
            const fieldset = el.closest('fieldset');
            if (fieldset) return fieldset.innerText;
            const fg = el.closest('.form-group');
            if (fg) return fg.innerText;
            return el.parentElement.innerText;
        }""")
        print(f"--- Radio: {name} (val={val}) ---")
        print(text)
    browser.close()
