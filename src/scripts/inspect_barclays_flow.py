import os
from playwright.sync_api import sync_playwright

url = "https://search.jobs.barclays/job/pune/software-engineer/13015/95536470528"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    )
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=25000)
    page.wait_for_timeout(3000)
    
    print("Page URL:", page.url)
    print("Page title:", page.title())
    
    # Check apply links/buttons
    apply_links = page.query_selector_all("a[href*='apply'], a.apply-button, button[class*='apply'], a:has-text('Apply')")
    print(f"Found {len(apply_links)} apply elements:")
    for al in apply_links:
        print("  Text:", al.inner_text().strip(), "Href:", al.get_attribute("href"), "Classes:", al.get_attribute("class"))
        
    # Check if there is an embedded Radancy/Phenom form already on the page or in a modal/drawer
    forms = page.query_selector_all("form")
    print(f"Forms on page: {len(forms)}")
    for f in forms:
        print("  Form action:", f.get_attribute("action"), "id:", f.get_attribute("id"), "class:", f.get_attribute("class"))
        inputs = f.query_selector_all("input")
        print(f"  Inputs in form ({len(inputs)}):")
        for inp in inputs:
            print("    name:", inp.get_attribute("name"), "type:", inp.get_attribute("type"), "id:", inp.get_attribute("id"), "visible:", inp.is_visible())

    browser.close()
