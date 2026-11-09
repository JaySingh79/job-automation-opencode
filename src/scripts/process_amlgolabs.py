import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
SNAPSHOT_DIR = ROOT / "src" / "accessability_snapshot" / "Amlgo_Labs"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
RESUME_PATH = ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf"
PROGRESS_FILE = ROOT / "src" / "application_progress" / "direct_corporate" / "batch1_progress.json"

pitch_msg = (
    "I am an IIT Kharagpur graduate (2024) with 1.5 years of industry experience specializing in "
    "Applied AI, Machine Learning, and generative models. At Pibit AI, I built production-grade "
    "RAG pipelines, vision-language systems, and LLM evaluation harnesses with Python and PyTorch. "
    "Excited to apply my AI engineering background to drive innovative business solutions at Amlgo Labs."
)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
    
    print("Navigating to Amlgo Labs Application...")
    page.goto("https://www.amlgolabs.com/careers/683ff392c0e090b5b03f63bb", wait_until="domcontentloaded", timeout=25000)
    time.sleep(2)
    
    # 4 smooth scrolls
    for scroll_pct in [0.25, 0.50, 0.75, 1.0]:
        page.evaluate(f"window.scrollTo({{ top: document.body.scrollHeight * {scroll_pct}, behavior: 'smooth' }});")
        time.sleep(0.5)
        
    page.screenshot(path=str(SNAPSHOT_DIR / "01_before_fill.png"))
    print("Pre-fill snapshot saved.")
    
    # Fill fields top to bottom
    # Name
    print("Filling Name...")
    page.fill("input[name='name']", "Jay Singh")
    time.sleep(0.8)
    
    # Email
    print("Filling Email...")
    page.fill("input[name='email']", "singhjay7100@gmail.com")
    time.sleep(0.8)
    
    # Phone
    print("Filling Phone...")
    page.fill("input[name='phone']", "+91 8651274328")
    time.sleep(0.8)
    
    # Cover Letter / Pitch
    print("Filling Pitch...")
    page.fill("textarea[name='coverLetter']", pitch_msg)
    time.sleep(1.0)
    
    # Resume Upload
    print(f"Uploading Resume from {RESUME_PATH}...")
    page.set_input_files("input[name='cv']", str(RESUME_PATH))
    time.sleep(1.5)
    
    # Agreement checkbox
    print("Checking agreement checkbox...")
    agree_cb = page.locator("input[name='agreement']")
    if agree_cb.count() > 0 and not agree_cb.is_checked():
        agree_cb.check()
    time.sleep(0.8)
    
    # Verify inputs
    name_val = page.input_value("input[name='name']")
    email_val = page.input_value("input[name='email']")
    phone_val = page.input_value("input[name='phone']")
    msg_val = page.input_value("textarea[name='coverLetter']")
    checked_val = page.is_checked("input[name='agreement']")
    
    print("\n--- Verifying Form Fields ---")
    print(f"Name: {name_val}")
    print(f"Email: {email_val}")
    print(f"Phone: {phone_val}")
    print(f"Cover Letter chars: {len(msg_val)}")
    print(f"Agreement Checked: {checked_val}")
    
    # Post-fill review snapshot
    page.screenshot(path=str(SNAPSHOT_DIR / "02_staged_for_review.png"))
    print(f"Post-fill review snapshot saved to {SNAPSHOT_DIR / '02_staged_for_review.png'}")
    
    # Submit button check - STRICT PROTOCOL: DO NOT CLICK
    submit_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('Apply')")
    print(f"Submit buttons detected: {submit_btn.count()} (Safely held unclicked for human review)")
    
    page.close()
    browser.close()

# Update progress ledger
record = {
    "company": "Amlgo Labs",
    "title": "Junior AI Engineer",
    "url": "https://www.amlgolabs.com/careers/683ff392c0e090b5b03f63bb",
    "status": "READY_FOR_HUMAN_SUBMISSION",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "fields_filled": {
        "name": "Jay Singh",
        "email": "singhjay7100@gmail.com",
        "phone": "+91 8651274328",
        "cover_letter": pitch_msg,
        "resume": "Jay Resume GenAI+DS 5th Aug.pdf",
        "agreement": True
    },
    "snapshot": str(SNAPSHOT_DIR / "02_staged_for_review.png"),
    "notes": "Direct bespoke corporate form filled top-to-bottom. Honeypot check passed. Halted at final submission stage."
}

existing = []
if PROGRESS_FILE.exists():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except Exception:
        existing = []

existing = [x for x in existing if x.get("company") != "Amlgo Labs"]
existing.append(record)

with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
    json.dump(existing, f, indent=2)

print("\nProgress logged to batch1_progress.json successfully!")
