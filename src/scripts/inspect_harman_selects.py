from playwright.sync_api import sync_playwright

url = "https://jobsearch.harman.com/en_US/careers/ApplicationMethods?jobId=32726"
resume_path = r"D:\Projects\PRACTICE\firecrawl_test\Resumes\Jay Resume GenAI+DS 5th Aug.pdf"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(2000)
    
    with page.expect_file_chooser() as fc_info:
        page.locator("#methodButton--file").click()
    file_chooser = fc_info.value
    file_chooser.set_files(resume_path)
    page.wait_for_timeout(3000)
    page.locator("#uploadFileResume").click()
    page.wait_for_timeout(5000)
    
    selects = page.query_selector_all("select")
    for s in selects:
        name = s.get_attribute("name") or s.get_attribute("id")
        options = [o.inner_text().strip() for o in s.query_selector_all("option") if o.inner_text().strip()]
        print(f"Select '{name}': {options[:8]}")
        
    browser.close()
