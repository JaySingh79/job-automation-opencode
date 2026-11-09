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
    
    field_specs = page.query_selector_all(".fieldSpec:visible")
    print(f"Visible fieldSpecs: {len(field_specs)}")
    for fs in field_specs:
        lbl = fs.query_selector("label")
        lbl_text = lbl.inner_text().strip() if lbl else ""
        inp = fs.query_selector("input:visible, select, textarea:visible")
        inp_id = inp.get_attribute("id") if inp else ""
        inp_val = inp.get_attribute("value") if inp else ""
        print(f"  Field: '{lbl_text}' | ID: {inp_id} | Val: {inp_val}")
        
    browser.close()
