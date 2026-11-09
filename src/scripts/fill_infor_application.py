import os
import time
from playwright.sync_api import sync_playwright

def fill_infor():
    url = "https://careers.infor.com/en/postings/0029cdab-7f9d-4a7c-b33a-c32a2fe77160/applications/new"
    resume_path = r"D:\Projects\PRACTICE\firecrawl_test\Resumes\Jay Resume GenAI+DS 5th Aug.pdf"
    screenshot_dir = r"src\accessability_snapshot\Infor"
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, "infor_staged_form.png")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        )
        page = ctx.new_page()
        
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        
        # Smooth scroll down to emulate human behavior and trigger lazy observers
        print("Emulating human scrolling...")
        for fraction in [0.25, 0.5, 0.75, 1.0]:
            page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {fraction})")
            time.sleep(1.0)
            
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1.0)
        
        # 1. Fill Personal Details
        print("Filling personal details...")
        first_name_input = page.locator("input[name='application_form[application][first_name]']")
        first_name_input.click()
        first_name_input.fill("Jay")
        time.sleep(1.0)
        
        last_name_input = page.locator("input[name='application_form[application][last_name]']")
        last_name_input.click()
        last_name_input.fill("Singh")
        time.sleep(1.0)
        
        email_input = page.locator("input[name='application_form[application][email]']")
        email_input.click()
        email_input.fill("singhjay7100@gmail.com")
        time.sleep(1.0)
        
        phone_input = page.locator("input[name='application_form[application][phone]']")
        phone_input.click()
        phone_input.fill("+918651274328")
        time.sleep(1.0)
        
        # Country
        country_input = page.locator("input[name='application_form[application][country]']:visible")
        if country_input.count() > 0:
            country_input.first.click()
            country_input.first.fill("India")
            time.sleep(1.0)
            
        # Address Line 1
        addr1_input = page.locator("input[name='application_form[application][address1]']")
        addr1_input.click()
        addr1_input.fill("H.No 12, Sector 4")
        time.sleep(1.0)
        
        # Town
        town_input = page.locator("input[name='application_form[application][town]']")
        town_input.click()
        town_input.fill("Bengaluru")
        time.sleep(1.0)
        
        # Postcode
        postcode_input = page.locator("input[name='application_form[application][postcode]']")
        postcode_input.click()
        postcode_input.fill("560001")
        time.sleep(1.2)
        
        # 2. Upload Resume
        print("Uploading resume...")
        file_input = page.locator("input[name='application_form[application][cv]']")
        file_input.set_input_files(resume_path)
        time.sleep(2.5)
        
        # 3. Questions
        print("Answering screening questions...")
        page.locator("label[for='application_form_application_answers_attributes_0_boolean_answer_true']").click()
        time.sleep(0.9)
        
        page.locator("label[for='application_form_application_answers_attributes_1_boolean_answer_true']").click()
        time.sleep(0.9)
        
        page.locator("label[for='application_form_application_answers_attributes_2_boolean_answer_false']").click()
        time.sleep(0.9)
        
        page.locator("label[for='application_form_application_answers_attributes_3_boolean_answer_false']").click()
        time.sleep(0.9)
        
        page.locator("label[for='application_form_application_answers_attributes_4_boolean_answer_false']").click()
        time.sleep(1.0)
        
        # 4. Consent Checkbox
        print("Checking consent checkbox...")
        page.locator("#application_process_information").click()
        time.sleep(1.0)
        
        # Verification check: inspect filled values
        print("\n--- Verifying Form Fields ---")
        fn_val = first_name_input.input_value()
        ln_val = last_name_input.input_value()
        em_val = email_input.input_value()
        ph_val = phone_input.input_value()
        ad_val = addr1_input.input_value()
        tw_val = town_input.input_value()
        pc_val = postcode_input.input_value()
        cb_val = page.locator("#application_process_information").is_checked()
        
        print(f"Name: {fn_val} {ln_val}")
        print(f"Email: {em_val} | Phone: {ph_val}")
        print(f"Address: {ad_val}, {tw_val} - {pc_val}")
        print(f"Consent checked: {cb_val}")
        
        # Take verification screenshot of the staged application
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Verification screenshot saved to: {screenshot_path}")
        
        print("\n>>> STAGED ON REVIEW / FORM COMPLETE: READY FOR HUMAN SUBMISSION <<<")
        print("Leaving submit unclicked per strict safety policy.")
        
        browser.close()

if __name__ == "__main__":
    fill_infor()
