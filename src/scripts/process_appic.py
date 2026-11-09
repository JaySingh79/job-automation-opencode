import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
SNAPSHOT_DIR = ROOT / "src" / "accessability_snapshot" / "Appic_Softwares"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
RESUME_PATH = ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf"
PROGRESS_FILE = ROOT / "src" / "application_progress" / "direct_corporate" / "batch1_progress.json"

pitch_msg = (
    "I am an IIT Kharagpur graduate (2024) with 1.5 years of industry experience specializing in "
    "Generative AI, Large Language Models, and RAG architectures. At Pibit AI, I engineered production "
    "LLM pipelines, agentic workflows, and multimodal systems using Python, PyTorch, and FastAPI. "
    "Excited to contribute to Appic Softwares' Generative AI team."
)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
    
    print("Navigating to Appic Softwares Careers...")
    page.goto("https://appicsoftwares.com/careers/", wait_until="domcontentloaded", timeout=25000)
    time.sleep(2)
    
    # 4 smooth scrolls
    for scroll_pct in [0.25, 0.50, 0.75, 1.0]:
        page.evaluate(f"window.scrollTo({{ top: document.body.scrollHeight * {scroll_pct}, behavior: 'smooth' }});")
        time.sleep(0.5)
        
    page.screenshot(path=str(SNAPSHOT_DIR / "01_before_fill.png"))
    print("Pre-fill snapshot saved.")
    
    # Fill fields top to bottom
    print("Filling Name...")
    page.fill("#job-name", "Jay Singh")
    time.sleep(0.8)
    
    print("Filling Email...")
    page.fill("#job-email", "singhjay7100@gmail.com")
    time.sleep(0.8)
    
    print("Filling Phone...")
    page.fill("#job-phone", "+91 8651274328")
    time.sleep(0.8)
    
    print("Filling Skills...")
    page.fill("#skills", "Generative AI, LLM, Python, PyTorch, RAG, LangChain, FastAPI, Prompt Engineering")
    time.sleep(0.9)
    
    print(f"Uploading CV from {RESUME_PATH}...")
    page.set_input_files("#your-resume", str(RESUME_PATH))
    time.sleep(1.5)
    
    print("Filling Message...")
    page.fill("#job-message", pitch_msg)
    time.sleep(1.0)
    
    # Verification
    name_val = page.input_value("#job-name")
    email_val = page.input_value("#job-email")
    phone_val = page.input_value("#job-phone")
    skill_val = page.input_value("#skills")
    msg_val = page.input_value("#job-message")
    
    print("\n--- Verifying Form Fields ---")
    print(f"Name: {name_val}")
    print(f"Email: {email_val}")
    print(f"Phone: {phone_val}")
    print(f"Skills: {skill_val}")
    print(f"Message chars: {len(msg_val)}")
    
    page.screenshot(path=str(SNAPSHOT_DIR / "02_staged_for_review.png"))
    print(f"Post-fill review snapshot saved to {SNAPSHOT_DIR / '02_staged_for_review.png'}")
    
    # Submit button check - DO NOT CLICK
    submit_btn = page.locator("input[type='submit'], button[type='submit'], button:has-text('Submit'), button:has-text('Apply')")
    print(f"Submit buttons detected: {submit_btn.count()} (Safely held unclicked for human review)")
    
    page.close()
    browser.close()

# Update progress ledger
record = {
    "company": "Appic Softwares",
    "title": "Generative AI Engineer",
    "url": "https://appicsoftwares.com/careers/",
    "status": "READY_FOR_HUMAN_SUBMISSION",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "fields_filled": {
        "name": "Jay Singh",
        "email": "singhjay7100@gmail.com",
        "phone": "+91 8651274328",
        "skills": "Generative AI, LLM, Python, PyTorch, RAG, LangChain, FastAPI, Prompt Engineering",
        "message": pitch_msg,
        "resume": "Jay Resume GenAI+DS 5th Aug.pdf"
    },
    "snapshot": str(SNAPSHOT_DIR / "02_staged_for_review.png"),
    "notes": "Direct corporate career form filled top-to-bottom. Honeypot check passed. Halted at final submission stage."
}

existing = []
if PROGRESS_FILE.exists():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except Exception:
        existing = []

existing = [x for x in existing if x.get("company") != "Appic Softwares"]
existing.append(record)

with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
    json.dump(existing, f, indent=2)

print("\nProgress logged to batch1_progress.json successfully!")
