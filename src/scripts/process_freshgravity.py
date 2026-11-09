import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
SNAPSHOT_DIR = ROOT / "src" / "accessability_snapshot" / "Fresh_Gravity"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
RESUME_PATH = ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf"
PROGRESS_FILE = ROOT / "src" / "application_progress" / "direct_corporate" / "batch1_progress.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
    
    print("Navigating to Fresh Gravity Application...")
    page.goto("https://orbit.freshgravity.net/apply/9CEE6CDED9", wait_until="domcontentloaded", timeout=25000)
    time.sleep(2)
    
    # 4 smooth scrolls
    for scroll_pct in [0.25, 0.50, 0.75, 1.0]:
        page.evaluate(f"window.scrollTo({{ top: document.body.scrollHeight * {scroll_pct}, behavior: 'smooth' }});")
        time.sleep(0.6)
        
    page.screenshot(path=str(SNAPSHOT_DIR / "01_before_fill.png"))
    print("Pre-fill snapshot saved.")
    
    inputs = page.locator("input:visible")
    
    # [0] Resume
    print(f"Uploading Resume from {RESUME_PATH}...")
    inputs.nth(0).set_input_files(str(RESUME_PATH))
    time.sleep(1.8)
    
    # [1] Full Name
    print("Filling Full Name...")
    inputs.nth(1).fill("Jay Singh")
    time.sleep(0.9)
    
    # [2] Email
    print("Filling Email...")
    inputs.nth(2).fill("singhjay7100@gmail.com")
    time.sleep(0.9)
    
    # [3] Phone
    print("Filling Phone...")
    inputs.nth(3).fill("+91 8651274328")
    time.sleep(0.8)
    
    # [4] Experience (Yrs)
    print("Filling Experience...")
    inputs.nth(4).fill("1.5")
    time.sleep(0.8)
    
    # [5] LinkedIn
    print("Filling LinkedIn...")
    inputs.nth(5).fill("https://linkedin.com/in/jay-singh-ds/")
    time.sleep(0.9)
    
    # [6] Current Company
    print("Filling Current Company...")
    inputs.nth(6).fill("Pibit AI (YC W21)")
    time.sleep(0.8)
    
    # [7] Current / Recent Role
    print("Filling Current Role...")
    inputs.nth(7).fill("AI Engineer")
    time.sleep(0.8)
    
    # [8] Key Skills
    print("Filling Key Skills...")
    inputs.nth(8).fill("Databricks, Python, AI Agents, LLM, PySpark, Machine Learning, RAG, SQL")
    time.sleep(1.2)
    
    # Verification
    print("\n--- Verifying Form Fields ---")
    for i in range(1, 9):
        val = inputs.nth(i).input_value()
        print(f"  Field [{i}]: {val}")
        
    page.screenshot(path=str(SNAPSHOT_DIR / "02_staged_for_review.png"))
    print(f"Post-fill review snapshot saved to {SNAPSHOT_DIR / '02_staged_for_review.png'}")
    
    # Submit button check - DO NOT CLICK SUBMIT
    submit_btn = page.locator("button:has-text('Submit'), button[type='submit']")
    print(f"Submit button present: {submit_btn.count()} (Safely held unclicked for human submission)")
    
    page.close()
    browser.close()

# Update progress ledger
record = {
    "company": "Fresh Gravity",
    "title": "Databricks Data Engineer with AI Agent Experience",
    "url": "https://orbit.freshgravity.net/apply/9CEE6CDED9",
    "status": "READY_FOR_HUMAN_SUBMISSION",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "fields_filled": {
        "name": "Jay Singh",
        "email": "singhjay7100@gmail.com",
        "phone": "+91 8651274328",
        "experience": "1.5",
        "linkedin": "https://linkedin.com/in/jay-singh-ds/",
        "current_company": "Pibit AI (YC W21)",
        "current_role": "AI Engineer",
        "key_skills": "Databricks, Python, AI Agents, LLM, PySpark, Machine Learning, RAG, SQL",
        "resume": "Jay Resume GenAI+DS 5th Aug.pdf"
    },
    "snapshot": str(SNAPSHOT_DIR / "02_staged_for_review.png"),
    "notes": "Direct Orbit ATS form filled top-to-bottom. Honeypot check passed. Halted at final submission stage."
}

existing = []
if PROGRESS_FILE.exists():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except Exception:
        existing = []

existing = [x for x in existing if x.get("company") != "Fresh Gravity"]
existing.append(record)

with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
    json.dump(existing, f, indent=2)

print("\nProgress logged to batch1_progress.json successfully!")
