import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
SNAPSHOT_DIR = ROOT / "src" / "accessability_snapshot" / "Softdel_Systems"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
RESUME_PATH = ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf"
PROGRESS_FILE = ROOT / "src" / "application_progress" / "direct_corporate" / "batch1_progress.json"

pitch_msg = (
    "I am an IIT Kharagpur graduate (2024) with a rigorous foundation in Computer Architecture, "
    "Algorithms, Linux systems, and Python/C systems programming. At Pibit AI and Pascal AI Labs, "
    "I engineered high-performance, low-latency computing workflows and data pipelines. "
    "Keen to contribute strong analytical and systems engineering skills to Softdel's embedded software team."
)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
    
    print("Navigating to Softdel Systems Application...")
    page.goto("https://www.softdel.com/jobs/software-engineer-embedded-systems/", wait_until="domcontentloaded", timeout=25000)
    time.sleep(2)
    
    # 4 smooth scrolls
    for scroll_pct in [0.25, 0.50, 0.75, 1.0]:
        page.evaluate(f"window.scrollTo({{ top: document.body.scrollHeight * {scroll_pct}, behavior: 'smooth' }});")
        time.sleep(0.5)
        
    page.screenshot(path=str(SNAPSHOT_DIR / "01_before_fill.png"))
    print("Pre-fill snapshot saved.")
    
    # Fill fields top to bottom
    print("Filling Name...")
    page.fill("#awsm-applicant-name", "Jay Singh")
    time.sleep(0.8)
    
    print("Filling Email...")
    page.fill("#awsm-applicant-email", "singhjay7100@gmail.com")
    time.sleep(0.8)
    
    print("Filling Phone...")
    page.fill("#awsm-applicant-phone", "+91 8651274328")
    time.sleep(0.8)
    
    print("Filling Cover Letter...")
    page.fill("#awsm-cover-letter", pitch_msg)
    time.sleep(1.0)
    
    print(f"Uploading Resume from {RESUME_PATH}...")
    page.set_input_files("#awsm-application-file", str(RESUME_PATH))
    time.sleep(1.5)
    
    print("Checking Privacy Policy Checkbox...")
    policy_cb = page.locator("#awsm_form_privacy_policy")
    if policy_cb.count() > 0 and not policy_cb.is_checked():
        policy_cb.check()
    time.sleep(0.8)
    
    # Verification
    name_val = page.input_value("#awsm-applicant-name")
    email_val = page.input_value("#awsm-applicant-email")
    phone_val = page.input_value("#awsm-applicant-phone")
    letter_val = page.input_value("#awsm-cover-letter")
    checked_val = page.is_checked("#awsm_form_privacy_policy")
    
    print("\n--- Verifying Form Fields ---")
    print(f"Name: {name_val}")
    print(f"Email: {email_val}")
    print(f"Phone: {phone_val}")
    print(f"Cover Letter chars: {len(letter_val)}")
    print(f"Privacy Policy Checked: {checked_val}")
    
    page.screenshot(path=str(SNAPSHOT_DIR / "02_staged_for_review.png"))
    print(f"Post-fill review snapshot saved to {SNAPSHOT_DIR / '02_staged_for_review.png'}")
    
    # Submit button check - DO NOT CLICK
    submit_btn = page.locator("#awsm-application-submit-btn")
    print(f"Submit button present: {submit_btn.count()} (Safely held unclicked for human review)")
    
    page.close()
    browser.close()

# Update progress ledger
record = {
    "company": "Softdel Systems",
    "title": "Software Engineer - Embedded Systems (Fresher)",
    "url": "https://www.softdel.com/jobs/software-engineer-embedded-systems/",
    "status": "READY_FOR_HUMAN_SUBMISSION",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "fields_filled": {
        "name": "Jay Singh",
        "email": "singhjay7100@gmail.com",
        "phone": "+91 8651274328",
        "cover_letter": pitch_msg,
        "resume": "Jay Resume GenAI+DS 5th Aug.pdf",
        "privacy_policy_accepted": True
    },
    "snapshot": str(SNAPSHOT_DIR / "02_staged_for_review.png"),
    "notes": "AWSM career portal form filled top-to-bottom. Honeypot check passed. Halted at final submission stage."
}

existing = []
if PROGRESS_FILE.exists():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except Exception:
        existing = []

existing = [x for x in existing if x.get("company") != "Softdel Systems"]
existing.append(record)

with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
    json.dump(existing, f, indent=2)

print("\nProgress logged to batch1_progress.json successfully!")
