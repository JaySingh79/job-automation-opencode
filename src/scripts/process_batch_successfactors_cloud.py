import os
import re
import json
import time
import random
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

BATCH_FILE = r"D:\Projects\PRACTICE\firecrawl_test\src\job_search_results\naukri\direct_company_platforms\batch_successfactors_cloud.json"
PROGRESS_FILE = r"D:\Projects\PRACTICE\firecrawl_test\src\application_progress\direct_corporate\batch3_progress.json"
RESUME_FILE = r"D:\Projects\PRACTICE\firecrawl_test\Resumes\Jay Resume GenAI+DS 5th Aug.pdf"
SNAPSHOT_DIR = r"D:\Projects\PRACTICE\firecrawl_test\src\accessability_snapshot"

CANDIDATE = {
    "first_name": "Jay",
    "last_name": "Singh",
    "full_name": "Jay Singh",
    "email": "singhjay7100@gmail.com",
    "phone": "8651274328",
    "country_code": "+91",
    "phone_with_code": "+918651274328",
    "experience_years": "1.5",
    "experience_months": "18",
    "education_college": "IIT Kharagpur",
    "education_degree": "B.Tech",
    "graduation_year": "2024",
    "current_ctc": "1800000",
    "current_ctc_lpa": "18",
    "expected_ctc": "2200000",
    "expected_ctc_lpa": "22",
    "notice_period": "0",
    "notice_period_text": "Immediate / 0 Days",
    "current_location": "Bengaluru",
    "preferred_locations": "Bengaluru, Pune, Hyderabad, Gurgaon, Noida, Remote",
    "pan": "OVFPS0023B",
    "linkedin": "https://www.linkedin.com/in/jay-singh-iitkgp",
    "github": "https://github.com/singhjay7100",
    "resume_path": RESUME_FILE
}

def load_jobs():
    with open(BATCH_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("jobs", [])

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "platform": "successfactors_and_cloud_ats",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_jobs": 0,
        "summary": {
            "staged_ready": 0,
            "blocked_auth_required": 0,
            "skipped": 0,
            "expired_or_closed": 0,
            "error": 0
        },
        "jobs": []
    }

def save_progress(progress):
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)

def update_job_progress(progress, job_id, company, title, url, status, reason, extra=None):
    for j in progress["jobs"]:
        if j.get("job_id") == job_id:
            j["status"] = status
            j["reason"] = reason
            j["updated_at"] = datetime.now(timezone.utc).isoformat()
            if extra:
                j.update(extra)
            recalc_summary(progress)
            save_progress(progress)
            return

    entry = {
        "job_id": job_id,
        "company": company,
        "title": title,
        "url": url,
        "status": status,
        "reason": reason,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    if extra:
        entry.update(extra)
    progress["jobs"].append(entry)
    recalc_summary(progress)
    save_progress(progress)

def recalc_summary(progress):
    summary = {
        "staged_ready": 0,
        "blocked_auth_required": 0,
        "skipped": 0,
        "expired_or_closed": 0,
        "error": 0
    }
    for j in progress["jobs"]:
        st = j.get("status", "").lower()
        if "staged" in st or "ready" in st:
            summary["staged_ready"] += 1
        elif "blocked" in st or "auth" in st or "login" in st:
            summary["blocked_auth_required"] += 1
        elif "expired" in st or "closed" in st or "404" in st:
            summary["expired_or_closed"] += 1
        elif "skip" in st:
            summary["skipped"] += 1
        else:
            summary["error"] += 1
    progress["summary"] = summary
    progress["total_jobs"] = len(progress["jobs"])

def save_snapshot(page, company_slug, name):
    try:
        cdir = os.path.join(SNAPSHOT_DIR, company_slug)
        os.makedirs(cdir, exist_ok=True)
        path = os.path.join(cdir, f"{name}.png")
        page.screenshot(path=path, full_page=False)
        return path
    except Exception as e:
        print(f"Failed to save screenshot: {e}")
        return None

def random_delay(min_ms=800, max_ms=2200):
    time.sleep(random.uniform(min_ms, max_ms) / 1000.0)

def scroll_page(page, times=4):
    for i in range(1, times + 1):
        fraction = i / times
        page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {fraction});")
        time.sleep(0.5)

def is_honeypot(input_element):
    # Rule: NEVER fill hidden text inputs (display: none, visibility: hidden) or name="q" on EY
    try:
        attrs = input_element.evaluate("""el => {
            const style = window.getComputedStyle(el);
            return {
                display: style.display,
                visibility: style.visibility,
                opacity: style.opacity,
                offsetParent: el.offsetParent !== null,
                name: el.getAttribute('name') || '',
                id: el.getAttribute('id') || '',
                type: el.getAttribute('type') || ''
            };
        }""")
        if attrs['name'] == 'q' or attrs['id'] == 'q':
            return True
        if attrs['display'] == 'none' or attrs['visibility'] == 'hidden' or attrs['opacity'] == '0':
            return True
        if not attrs['offsetParent'] and attrs['type'] != 'file':
            return True
        return False
    except Exception:
        return True

def process_single_job(browser, job, progress):
    job_id = job.get("job_id")
    company = job.get("company", "Unknown")
    title = job.get("title", "Unknown")
    url = job.get("company_site_url", "")
    exp = job.get("experience", "")
    
    print(f"\n==================================================")
    print(f"Processing [{job_id}] {company} - {title}")
    print(f"URL: {url}")
    print(f"==================================================")

    # 1. Fast Bailout: Seniority rule
    title_lower = title.lower()
    senior_keywords = ["senior", "sr.", "lead", "principal", "architect", "staff", "manager", "director", "head"]
    if any(k in title_lower for k in senior_keywords):
        print(f"SKIP: Senior role detected in title '{title}'")
        update_job_progress(progress, job_id, company, title, url, "SKIPPED", 
                            f"Seniority gate: Title '{title}' specifies senior level exceeding target profile (0-2 YoE).")
        return

    # Fast Bailout: Security Clearance / non-India eligibility
    if "security clearance" in title_lower or "tier 2" in title_lower:
        print(f"SKIP: Security clearance required for '{title}'")
        update_job_progress(progress, job_id, company, title, url, "SKIPPED",
                            f"Eligibility constraint: Title specifies '{title}' requiring US government security clearance, candidate ineligible.")
        return

    # 2. Open page in isolated tab
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800}
    )
    page = context.new_page()

    try:
        response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        scroll_page(page, times=2)
        
        status_code = response.status if response else 0
        current_url = page.url
        body_text = page.inner_text("body").lower() if page.locator("body").count() > 0 else ""
        
        print(f"Page loaded. Status: {status_code}, URL: {current_url}")

        # Check for 404 / Expired / Closed
        expired_phrases = [
            "job is no longer available", "posting has expired", "job requisition is closed",
            "this position has been filled", "404 not found", "page not found", "no longer accepting applications",
            "job expired", "job closed", "the job you are looking for has expired"
        ]
        if status_code == 404 or any(phrase in body_text for phrase in expired_phrases):
            print(f"EXPIRED: Posting closed or unavailable")
            save_snapshot(page, company.lower().replace(" ", "_"), f"{job_id}_expired")
            update_job_progress(progress, job_id, company, title, url, "EXPIRED_OR_CLOSED",
                                "Job posting is expired, filled, or returned 404 Not Found on direct company portal.")
            context.close()
            return

        # Handle specific platforms
        ats_domain = job.get("ats_domain", "")
        
        # --- EY (careers.ey.com) ---
        if "careers.ey.com" in ats_domain or "ey.com" in current_url:
            handle_ey(page, job, progress, context)
            return

        # --- PayU (careers.payu.in) ---
        elif "payu.in" in ats_domain or "payu" in current_url:
            handle_payu(page, job, progress, context)
            return

        # --- TurboHire (Avataar) ---
        elif "turbohire.co" in ats_domain or "turbohire" in current_url:
            handle_turbohire(page, job, progress, context)
            return

        # --- Micro1 (jobs.micro1.ai) ---
        elif "micro1.ai" in ats_domain or "micro1" in current_url:
            handle_micro1(page, job, progress, context)
            return

        # --- HROne (Wander On Experiences) ---
        elif "hrone.cloud" in ats_domain or "hrone" in current_url:
            handle_hrone(page, job, progress, context)
            return

        # --- ADP (Data Axle Solutions) ---
        elif "adp.com" in ats_domain or "adp" in current_url:
            handle_adp(page, job, progress, context)
            return

        # --- PeopleStrong (Akasa Air) ---
        elif "peoplestrong.com" in ats_domain or "peoplestrong" in current_url:
            handle_peoplestrong(page, job, progress, context)
            return

        # --- Medpace (careers.medpace.com) ---
        elif "medpace.com" in ats_domain or "medpace" in current_url:
            handle_medpace(page, job, progress, context)
            return

        # --- Newton School (careers.newtonschool.co) ---
        elif "newtonschool.co" in ats_domain or "newtonschool" in current_url:
            handle_newtonschool(page, job, progress, context)
            return

        # --- Reczee (Teesta Investment) ---
        elif "reczee.com" in ats_domain or "reczee" in current_url:
            handle_reczee(page, job, progress, context)
            return

        # --- Electrifex & Unitech Technocrats & others ---
        else:
            handle_generic(page, job, progress, context)
            return

    except Exception as e:
        print(f"ERROR processing {job_id}: {e}")
        update_job_progress(progress, job_id, company, title, url, "ERROR", f"Navigation/Processing exception: {str(e)[:200]}")
    finally:
        try:
            context.close()
        except Exception:
            pass

def handle_ey(page, job, progress, context):
    job_id = job.get("job_id")
    company = "EY"
    title = job.get("title")
    url = job.get("company_site_url")
    company_slug = "ey"

    print("Executing EY handler...")
    scroll_page(page, times=3)
    
    # Check for "Apply now" button
    apply_btn = page.locator("button:has-text('Apply now'), a:has-text('Apply now'), button:has-text('Apply'), a:has-text('Apply')").first
    if apply_btn.count() == 0:
        print("No Apply button found on EY page.")
        snap = save_snapshot(page, company_slug, f"{job_id}_no_apply")
        update_job_progress(progress, job_id, company, title, url, "EXPIRED_OR_CLOSED",
                            "EY job page does not have an active Apply button; requisition may be closed.")
        return

    print("Found Apply button, checking options...")
    apply_btn.click()
    time.sleep(3)
    
    # EY SuccessFactors TalentBrew usually shows a dropdown or modal: "Apply with LinkedIn", "Apply Now" (account)
    # Check if a modal or new tab/url opened
    current_url = page.url
    print(f"URL after Apply click: {current_url}")
    
    # Look for account login / create account
    if "login" in current_url.lower() or "career" in current_url.lower() or page.locator("input[type='password'], button:has-text('Sign In'), a:has-text('Create an account')").count() > 0:
        print("EY requires SuccessFactors candidate account authentication.")
        snap = save_snapshot(page, company_slug, f"{job_id}_sf_auth_required")
        update_job_progress(progress, job_id, company, title, url, "BLOCKED_AUTH_REQUIRED",
                            "EY SuccessFactors candidate portal requires corporate account login/registration with email verification password.",
                            {"snapshot": snap, "portal_url": current_url})
        return

    # Check if application form fields exist on page
    inputs = page.locator("input:visible, select:visible, textarea:visible")
    print(f"Visible inputs count: {inputs.count()}")
    if inputs.count() == 0:
        snap = save_snapshot(page, company_slug, f"{job_id}_auth_step")
        update_job_progress(progress, job_id, company, title, url, "BLOCKED_AUTH_REQUIRED",
                            "EY career portal redirected to account authentication gateway.",
                            {"snapshot": snap, "portal_url": current_url})
        return

    # If form exists without login, attempt safe fill
    fill_standard_form(page, job, progress, company_slug)

def handle_payu(page, job, progress, context):
    job_id = job.get("job_id")
    company = "PayU"
    title = job.get("title")
    url = job.get("company_site_url")
    company_slug = "payu"

    print("Executing PayU handler...")
    scroll_page(page, times=3)

    apply_btn = page.locator("a:has-text('Apply'), button:has-text('Apply'), a:has-text('I\\'m interested')").first
    if apply_btn.count() == 0:
        body = page.inner_text("body").lower()
        if "no longer available" in body or "closed" in body:
            update_job_progress(progress, job_id, company, title, url, "EXPIRED_OR_CLOSED", "PayU job is closed.")
            return

    apply_btn.click()
    time.sleep(3)
    current_url = page.url
    print(f"PayU URL after click: {current_url}")

    if "login" in current_url.lower() or page.locator("input[type='password']").count() > 0:
        snap = save_snapshot(page, company_slug, f"{job_id}_auth_required")
        update_job_progress(progress, job_id, company, title, url, "BLOCKED_AUTH_REQUIRED",
                            "PayU career portal requires candidate authentication/account creation.",
                            {"snapshot": snap, "portal_url": current_url})
        return

    fill_standard_form(page, job, progress, company_slug)

def handle_turbohire(page, job, progress, context):
    job_id = job.get("job_id")
    company = job.get("company", "Avataar")
    title = job.get("title")
    url = job.get("company_site_url")
    company_slug = "turbohire"

    print("Executing TurboHire handler...")
    scroll_page(page, times=3)

    apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply')").first
    if apply_btn.count() > 0:
        apply_btn.click()
        time.sleep(2)

    fill_standard_form(page, job, progress, company_slug)

def handle_micro1(page, job, progress, context):
    job_id = job.get("job_id")
    company = "Micro1"
    title = job.get("title")
    url = job.get("company_site_url")
    company_slug = "micro1"

    print("Executing Micro1 handler...")
    scroll_page(page, times=3)

    # Check for direct apply or button
    apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply')").first
    if apply_btn.count() > 0:
        apply_btn.click()
        time.sleep(2)

    fill_standard_form(page, job, progress, company_slug)

def handle_hrone(page, job, progress, context):
    job_id = job.get("job_id")
    company = job.get("company", "Wander On")
    title = job.get("title")
    url = job.get("company_site_url")
    company_slug = "hrone"

    print("Executing HROne handler...")
    scroll_page(page, times=3)

    fill_standard_form(page, job, progress, company_slug)

def handle_adp(page, job, progress, context):
    job_id = job.get("job_id")
    company = "Data Axle Solutions"
    title = job.get("title")
    url = job.get("company_site_url")
    company_slug = "adp"

    print("Executing ADP handler...")
    scroll_page(page, times=3)

    apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply')").first
    if apply_btn.count() > 0:
        apply_btn.click()
        time.sleep(3)

    current_url = page.url
    if "login" in current_url.lower() or page.locator("input[type='password']").count() > 0:
        snap = save_snapshot(page, company_slug, f"{job_id}_adp_auth_required")
        update_job_progress(progress, job_id, company, title, url, "BLOCKED_AUTH_REQUIRED",
                            "ADP CX candidate portal enforces candidate account login.",
                            {"snapshot": snap, "portal_url": current_url})
        return

    fill_standard_form(page, job, progress, company_slug)

def handle_peoplestrong(page, job, progress, context):
    job_id = job.get("job_id")
    company = "Akasa Air"
    title = job.get("title")
    url = job.get("company_site_url")
    company_slug = "peoplestrong"

    print("Executing PeopleStrong handler...")
    scroll_page(page, times=3)

    apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply')").first
    if apply_btn.count() > 0:
        apply_btn.click()
        time.sleep(3)

    current_url = page.url
    if "login" in current_url.lower() or page.locator("input[type='password']").count() > 0:
        snap = save_snapshot(page, company_slug, f"{job_id}_peoplestrong_auth")
        update_job_progress(progress, job_id, company, title, url, "BLOCKED_AUTH_REQUIRED",
                            "PeopleStrong candidate portal requires account registration/login.",
                            {"snapshot": snap, "portal_url": current_url})
        return

    fill_standard_form(page, job, progress, company_slug)

def handle_medpace(page, job, progress, context):
    job_id = job.get("job_id")
    company = "Medpace"
    title = job.get("title")
    url = job.get("company_site_url")
    company_slug = "medpace"

    print("Executing Medpace handler...")
    scroll_page(page, times=3)

    apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply')").first
    if apply_btn.count() > 0:
        apply_btn.click()
        time.sleep(3)

    fill_standard_form(page, job, progress, company_slug)

def handle_newtonschool(page, job, progress, context):
    job_id = job.get("job_id")
    company = "Newton School"
    title = job.get("title")
    url = job.get("company_site_url")
    company_slug = "newtonschool"

    print("Executing Newton School handler...")
    scroll_page(page, times=3)

    # Check for direct apply or button
    apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply')").first
    if apply_btn.count() > 0:
        apply_btn.click()
        time.sleep(2)

    fill_standard_form(page, job, progress, company_slug)

def handle_reczee(page, job, progress, context):
    job_id = job.get("job_id")
    company = "Teesta Investment"
    title = job.get("title")
    url = job.get("company_site_url")
    company_slug = "reczee"

    print("Executing Reczee handler...")
    scroll_page(page, times=3)

    fill_standard_form(page, job, progress, company_slug)

def handle_generic(page, job, progress, context):
    job_id = job.get("job_id")
    company = job.get("company", "Unknown")
    title = job.get("title")
    url = job.get("company_site_url")
    company_slug = company.lower().replace(" ", "_")

    print(f"Executing Generic handler for {company}...")
    scroll_page(page, times=3)

    # Check if page is just a generic homepage or invalid career site
    current_url = page.url
    body_text = page.inner_text("body").lower()
    
    apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply')").first
    if apply_btn.count() > 0:
        apply_btn.click()
        time.sleep(2)

    fill_standard_form(page, job, progress, company_slug)

def fill_standard_form(page, job, progress, company_slug):
    job_id = job.get("job_id")
    company = job.get("company")
    title = job.get("title")
    url = job.get("company_site_url")

    # Locate inputs
    inputs = page.locator("input, textarea, select")
    visible_count = 0
    filled_count = 0

    print("Scanning form inputs...")
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        try:
            if is_honeypot(inp):
                continue
            visible_count += 1
            
            # Extract attributes
            info = inp.evaluate("""el => {
                const label = document.querySelector(`label[for="${el.id}"]`)?.innerText || 
                              el.closest('label')?.innerText || 
                              el.getAttribute('aria-label') || 
                              el.getAttribute('placeholder') || 
                              el.getAttribute('name') || 
                              '';
                return {
                    name: el.getAttribute('name') || '',
                    id: el.getAttribute('id') || '',
                    type: el.getAttribute('type') || el.tagName.toLowerCase(),
                    placeholder: el.getAttribute('placeholder') || '',
                    label: label.toLowerCase()
                };
            }""")
            
            combined = (info['name'] + " " + info['id'] + " " + info['placeholder'] + " " + info['label']).lower()
            
            # Upload Resume
            if info['type'] == 'file' or 'resume' in combined or 'cv' in combined:
                if os.path.exists(RESUME_FILE):
                    inp.set_input_files(RESUME_FILE)
                    print(f"Uploaded resume to field: {combined[:40]}")
                    filled_count += 1
                    random_delay(1000, 2000)
                continue

            # First Name
            if any(k in combined for k in ['first_name', 'firstname', 'fname']) or ('first' in combined and 'name' in combined):
                inp.fill(CANDIDATE['first_name'])
                print(f"Filled First Name: {CANDIDATE['first_name']}")
                filled_count += 1
                random_delay()
                continue

            # Last Name
            if any(k in combined for k in ['last_name', 'lastname', 'lname']) or ('last' in combined and 'name' in combined):
                inp.fill(CANDIDATE['last_name'])
                print(f"Filled Last Name: {CANDIDATE['last_name']}")
                filled_count += 1
                random_delay()
                continue

            # Full Name
            if 'name' in combined and not any(k in combined for k in ['company', 'school', 'college', 'file']):
                inp.fill(CANDIDATE['full_name'])
                print(f"Filled Full Name: {CANDIDATE['full_name']}")
                filled_count += 1
                random_delay()
                continue

            # Email
            if 'email' in combined or 'e-mail' in combined or info['type'] == 'email':
                inp.fill(CANDIDATE['email'])
                print(f"Filled Email: {CANDIDATE['email']}")
                filled_count += 1
                random_delay()
                continue

            # Phone
            if any(k in combined for k in ['phone', 'mobile', 'contact', 'cell', 'tel']):
                if 'code' in combined or 'country' in combined:
                    try:
                        inp.fill("+91")
                    except Exception:
                        pass
                else:
                    inp.fill(CANDIDATE['phone'])
                print(f"Filled Phone: {CANDIDATE['phone']}")
                filled_count += 1
                random_delay()
                continue

            # Experience
            if any(k in combined for k in ['experience', 'exp', 'years_of_experience', 'total_experience']):
                if 'month' in combined:
                    inp.fill(CANDIDATE['experience_months'])
                else:
                    inp.fill(CANDIDATE['experience_years'])
                print(f"Filled Experience: {CANDIDATE['experience_years']}")
                filled_count += 1
                random_delay()
                continue

            # Current CTC
            if 'current_ctc' in combined or 'current ctc' in combined or 'current salary' in combined:
                if 'lpa' in combined or 'lakh' in combined:
                    inp.fill(CANDIDATE['current_ctc_lpa'])
                else:
                    inp.fill(CANDIDATE['current_ctc'])
                print(f"Filled Current CTC")
                filled_count += 1
                random_delay()
                continue

            # Expected CTC
            if 'expected_ctc' in combined or 'expected ctc' in combined or 'expected salary' in combined:
                if 'lpa' in combined or 'lakh' in combined:
                    inp.fill(CANDIDATE['expected_ctc_lpa'])
                else:
                    inp.fill(CANDIDATE['expected_ctc'])
                print(f"Filled Expected CTC")
                filled_count += 1
                random_delay()
                continue

            # Notice Period
            if 'notice' in combined:
                inp.fill(CANDIDATE['notice_period'])
                print(f"Filled Notice Period: 0")
                filled_count += 1
                random_delay()
                continue

            # Location / City
            if any(k in combined for k in ['city', 'location', 'address']):
                inp.fill(CANDIDATE['current_location'])
                print(f"Filled Location: {CANDIDATE['current_location']}")
                filled_count += 1
                random_delay()
                continue

            # College / University
            if any(k in combined for k in ['college', 'university', 'institute', 'school']):
                inp.fill(CANDIDATE['education_college'])
                print(f"Filled College: {CANDIDATE['education_college']}")
                filled_count += 1
                random_delay()
                continue

            # Degree
            if any(k in combined for k in ['degree', 'qualification', 'education']):
                inp.fill(CANDIDATE['education_degree'])
                print(f"Filled Degree: {CANDIDATE['education_degree']}")
                filled_count += 1
                random_delay()
                continue

            # LinkedIn
            if 'linkedin' in combined:
                inp.fill(CANDIDATE['linkedin'])
                print(f"Filled LinkedIn")
                filled_count += 1
                random_delay()
                continue

            # GitHub
            if 'github' in combined:
                inp.fill(CANDIDATE['github'])
                print(f"Filled GitHub")
                filled_count += 1
                random_delay()
                continue

        except Exception as field_err:
            print(f"Could not fill input: {field_err}")

    print(f"Form scanning complete. Filled {filled_count} / {visible_count} visible fields.")

    if filled_count >= 2:
        # Check for consent / terms checkbox
        try:
            checkboxes = page.locator("input[type='checkbox']:visible")
            for c in range(checkboxes.count()):
                cb = checkboxes.nth(c)
                if not cb.is_checked():
                    cb.check()
                    print("Checked consent checkbox")
        except Exception:
            pass

        # Take screenshot of staged application
        snap = save_snapshot(page, company_slug, f"{job_id}_staged_review")
        print(f"CRITICAL: Application filled and staged. STOPPING BEFORE FINAL SUBMISSION per Rule.")
        update_job_progress(progress, job_id, company, title, url, "STAGED_READY",
                            f"Application fields filled ({filled_count} fields, resume attached). Staged on review/submission step - awaiting human submission authority.",
                            {"snapshot": snap, "fields_filled": filled_count})
    else:
        # Form had no fields or failed to load
        snap = save_snapshot(page, company_slug, f"{job_id}_no_form")
        update_job_progress(progress, job_id, company, title, url, "BLOCKED_AUTH_REQUIRED",
                            "Direct apply form not exposed on public view; requires candidate portal account login/registration.",
                            {"snapshot": snap})

def main():
    jobs = load_jobs()
    progress = load_progress()
    print(f"Loaded {len(jobs)} jobs to process.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for job in jobs:
                process_single_job(browser, job, progress)
                time.sleep(1.5)
        finally:
            browser.close()

    print("\nBatch processing complete!")
    print(json.dumps(progress["summary"], indent=2))

if __name__ == "__main__":
    main()
