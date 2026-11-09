from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://job-boards.greenhouse.io/bswiftindia/jobs/4699956006", timeout=30000)
    
    # Check invalid or select elements
    elements = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('select, [class*="select"], [role="combobox"], [role="listbox"], input[required]')).map(el => ({
            tagName: el.tagName,
            id: el.id,
            name: el.name,
            required: el.required,
            className: el.className,
            parentText: el.closest('.field, div, label')?.innerText?.slice(0, 150)
        }));
    }''')
    for el in elements:
        print("EL:", el)
        
    browser.close()
