import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

chrome_profile = Path(
    r"C:\Users\binit\AppData\Local\Google\Chrome\User Data\Profile 2"
)

playwright_profile = Path(
    r"C:\Users\binit\AppData\Local\PlaywrightChromeProfile"
)

# Copy Chrome Profile 2 → separate Playwright profile
if not playwright_profile.exists():
    shutil.copytree(chrome_profile, playwright_profile)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(playwright_profile),
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=False
    )

    print("Chrome launched!")

    context.storage_state(path="chrome_state.json")

    input("Press Enter to close...")

    context.close()