"""
Deep Reconnaissance Engine for Workday and Oracle Cloud ATS Portals.
Systematically tests 10 benchmark applications (5 Workday + 5 Oracle Cloud)
to map DOM components, JS hydration frameworks, synthetic event dispatches,
authentication models, and navigation latencies.
"""

import os
import sys
import json
import time
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
SNAPSHOT_DIR = ROOT / "src" / "accessability_snapshot" / "deep_recon"
OUTPUT_JSON = ROOT / "src" / "knowledge_source" / "ats_workday_oracle_deep_recon.json"

SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

TARGET_APPLICATIONS = [
    # --- WORKDAY (5 Benchmark Tenants) ---
    {
        "id": "WD-01",
        "platform": "workday",
        "tenant": "mastercard.wd1",
        "company": "Mastercard",
        "role": "Data Scientist I",
        "url": "https://mastercard.wd1.myworkdayjobs.com/en-US/CorporateCareers/job/Pune-India/Data-Scientist-I_R-238474"
    },
    {
        "id": "WD-02",
        "platform": "workday",
        "tenant": "cisco.wd5",
        "company": "Cisco Systems",
        "role": "Software Engineer - Backend (Python/Go)",
        "url": "https://cisco.wd5.myworkdayjobs.com/en-US/Cisco_Careers/job/Bangalore-India/Software-Engineer---Backend--Python-Go--Distributed-Systems--Cloud_2004245"
    },
    {
        "id": "WD-03",
        "platform": "workday",
        "tenant": "valeo.wd3",
        "company": "Valeo",
        "role": "Artificial Intelligence Engineer",
        "url": "https://valeo.wd3.myworkdayjobs.com/en-US/valeo_jobs/job/Chennai/Artificial-Intelligence-Engineer_24000CGQ"
    },
    {
        "id": "WD-04",
        "platform": "workday",
        "tenant": "corrohealth.wd1",
        "company": "CorroHealth",
        "role": "Junior AI - Engineer",
        "url": "https://corrohealth.wd1.myworkdayjobs.com/en-US/CorroHealthIndia/job/Noida-Luminex/Junior-AI---Engineer_R-03823"
    },
    {
        "id": "WD-05",
        "platform": "workday",
        "tenant": "pitneybowes.wd1",
        "company": "Pitney Bowes",
        "role": "Graduate Engineer Trainee",
        "url": "https://pitneybowes.wd1.myworkdayjobs.com/en-US/PBCareers/job/IN-Pune/Graduate-Engineer-Trainee_R18485"
    },

    # --- ORACLE CLOUD (5 Benchmark Tenants) ---
    {
        "id": "OC-01",
        "platform": "oracle_cloud",
        "tenant": "egug.fa.us2",
        "company": "American Express",
        "role": "Analyst-Data Analytics (Agentic)",
        "url": "https://egug.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/job/26015040"
    },
    {
        "id": "OC-02",
        "platform": "oracle_cloud",
        "tenant": "edbz.fa.us2",
        "company": "Texas Instruments",
        "role": "Software Development Engineer",
        "url": "https://edbz.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/job/25017214"
    },
    {
        "id": "OC-03",
        "platform": "oracle_cloud",
        "tenant": "fa-etbm-saasfaprod1",
        "company": "IBS Software Services",
        "role": "Fullstack Developer",
        "url": "https://fa-etbm-saasfaprod1.fa.ocs.oraclecloud.com//hcmUI/CandidateExperience/en/sites/CX_1/requisitions/preview/2523/?mode=location"
    },
    {
        "id": "OC-04",
        "platform": "oracle_cloud",
        "tenant": "jpmc.fa",
        "company": "JPMorgan Chase & Co",
        "role": "Trading Services Associate I",
        "url": "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/job/210797882"
    },
    {
        "id": "OC-05",
        "platform": "oracle_cloud",
        "tenant": "fa-euxc-saasfaprod1",
        "company": "Citco",
        "role": "IT Developer",
        "url": "https://fa-euxc-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/job/17166"
    }
]

def perform_telemetry_scrolls(page):
    """Executes 4 smooth viewport scrolls to trigger lazy observers."""
    for pct in [0.25, 0.50, 0.75, 1.0]:
        page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {pct});")
        time.sleep(0.3)
    page.evaluate("window.scrollTo(0, 0);")
    time.sleep(0.3)

def analyze_target(page, target):
    app_id = target["id"]
    url = target["url"]
    platform = target["platform"]
    company = target["company"]
    
    print(f"\n=======================================================")
    print(f"[{app_id}] Probing {company} ({platform}) -> {url[:75]}...")
    print(f"=======================================================")

    recon_data = {
        "id": app_id,
        "platform": platform,
        "tenant": target["tenant"],
        "company": company,
        "role": target["role"],
        "target_url": url,
        "final_url": None,
        "http_status": None,
        "load_time_ms": 0,
        "page_title": "",
        "frameworks_detected": [],
        "dom_metrics": {},
        "apply_button_found": False,
        "apply_button_text": "",
        "apply_button_selector": "",
        "navigation_action": None,
        "first_step_url": None,
        "auth_gate_type": "unknown",
        "input_controls_sample": [],
        "synthetic_event_profile": {},
        "screenshot_path": None,
        "errors": []
    }

    start_time = time.time()
    try:
        response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
        recon_data["load_time_ms"] = int((time.time() - start_time) * 1000)
        if response:
            recon_data["http_status"] = response.status
        
        # Allow JavaScript hydration
        time.sleep(3)
        perform_telemetry_scrolls(page)
        time.sleep(1)

        recon_data["final_url"] = page.url
        recon_data["page_title"] = page.title()

        # Interrogate runtime window and DOM
        dom_analysis = page.evaluate("""() => {
            const fw = [];
            // Framework detection
            if (window.React || document.querySelector('[data-reactroot], [data-reactid], [data-react-helmet]')) fw.push('React');
            if (window.ko || window.knockout) fw.push('Knockout.js');
            if (window.oj || window.OJ) fw.push('Oracle JET');
            if (window.angular || document.querySelector('[ng-app], [ng-version], [_ngcontent]')) fw.push('Angular');
            if (window.jQuery || window.$?.fn?.jquery) fw.push('jQuery ' + (window.$?.fn?.jquery || ''));
            if (window.__NEXT_DATA__) fw.push('Next.js');

            // Web components & Shadow DOM
            const customElements = [...document.querySelectorAll('*')].filter(el => el.tagName.includes('-')).map(el => el.tagName.toLowerCase());
            const uniqueCustom = [...new Set(customElements)].slice(0, 15);

            // Workday automation tags
            const wdAutomationIds = [...document.querySelectorAll('[data-automation-id]')].map(el => el.getAttribute('data-automation-id')).slice(0, 20);

            // Oracle JET controls
            const ojControls = [...document.querySelectorAll('[class*="oj-"], [data-oj-context], oj-input-text, oj-select-one, oj-button')].map(el => el.tagName.toLowerCase()).slice(0, 20);

            // Interactive element counts
            const inputs = document.querySelectorAll('input:not([type="hidden"])').length;
            const selects = document.querySelectorAll('select').length;
            const buttons = document.querySelectorAll('button, a[role="button"]').length;
            const iframes = document.querySelectorAll('iframe').length;

            return {
                frameworks: fw,
                custom_elements: uniqueCustom,
                wd_automation_ids: wdAutomationIds,
                oj_controls_sample: ojControls,
                counts: { inputs, selects, buttons, iframes }
            };
        }""")

        recon_data["frameworks_detected"] = dom_analysis.get("frameworks", [])
        recon_data["dom_metrics"] = dom_analysis

        # Locate Apply CTA
        apply_probe = page.evaluate("""() => {
            // Common Workday Apply selectors
            const wdApply = document.querySelector('[data-automation-id="adventureButton"], [data-automation-id="applyButton"], a[data-automation-id*="apply"]');
            if (wdApply) return { found: true, text: wdApply.textContent.trim(), selector: '[data-automation-id="' + wdApply.getAttribute('data-automation-id') + '"]' };

            // Common Oracle JET / generic Apply selectors
            const ojApply = document.querySelector('oj-button[id*="apply"], button[id*="apply"], a[id*="apply"], [class*="apply-button"]');
            if (ojApply) return { found: true, text: ojApply.textContent.trim(), selector: ojApply.id ? '#' + ojApply.id : '.' + (ojApply.className || '').split(' ')[0] };

            const allButtons = [...document.querySelectorAll('button, a, [role="button"]')];
            const candidate = allButtons.find(b => {
                const txt = (b.textContent || '').trim().toLowerCase();
                return txt === 'apply' || txt === 'apply now' || txt === 'apply manually' || txt.includes('apply');
            });
            if (candidate) return { found: true, text: candidate.textContent.trim(), selector: candidate.id ? '#' + candidate.id : (candidate.getAttribute('data-automation-id') ? '[data-automation-id="' + candidate.getAttribute('data-automation-id') + '"]' : candidate.tagName.toLowerCase()) };

            return { found: false, text: '', selector: '' };
        }""")

        recon_data["apply_button_found"] = apply_probe.get("found", False)
        recon_data["apply_button_text"] = apply_probe.get("text", "")
        recon_data["apply_button_selector"] = apply_probe.get("selector", "")

        print(f"  -> Title: {recon_data['page_title']}")
        print(f"  -> Frameworks: {recon_data['frameworks_detected']}")
        print(f"  -> Apply CTA: {recon_data['apply_button_found']} ('{recon_data['apply_button_text']}') via {recon_data['apply_button_selector']}")

        # Test Apply action & observe Step 1 / Auth Gate
        try:
            # If Workday, click the Apply button to reveal "Apply Manually" vs "Quick Apply"
            if platform == "workday":
                btn = page.locator('[data-automation-id="adventureButton"], [data-automation-id="applyButton"], a:has-text("Apply"), button:has-text("Apply")').first
                if btn.count() > 0 and btn.is_visible():
                    recon_data["apply_button_found"] = True
                    btn.click()
                    time.sleep(2)
                    # Check for sub-options e.g. "Apply Manually"
                    manual_btn = page.locator('[data-automation-id="applyManually"], button:has-text("Apply Manually"), a:has-text("Apply Manually")').first
                    if manual_btn.count() > 0 and manual_btn.is_visible():
                        recon_data["navigation_action"] = "clicked_apply_then_manual"
                        manual_btn.click()
                        time.sleep(3)
                    else:
                        recon_data["navigation_action"] = "clicked_apply_direct"

            elif platform == "oracle_cloud":
                # Oracle JET button click
                apply_btn = page.locator('oj-button:has-text("Apply"), button:has-text("Apply Now"), button:has-text("Apply"), a:has-text("Apply")').first
                if apply_btn.count() > 0 and apply_btn.is_visible():
                    recon_data["apply_button_found"] = True
                    recon_data["navigation_action"] = "clicked_oracle_apply"
                    apply_btn.click()
                    time.sleep(3)

            recon_data["first_step_url"] = page.url

            # Analyze the newly loaded form / auth gate
            step_analysis = page.evaluate("""() => {
                const url = window.location.href;
                const bodyText = document.body.innerText.toLowerCase();

                // Detect auth gate
                let auth = 'none';
                if (document.querySelector('input[type="password"]') || bodyText.includes('sign in') || bodyText.includes('create account') || bodyText.includes('log in')) {
                    auth = 'account_password_login';
                }
                if (bodyText.includes('verification code') || bodyText.includes('one-time password') || bodyText.includes('otp')) {
                    auth = 'email_otp_challenge';
                }
                if (bodyText.includes('guest') || document.querySelector('[data-automation-id="guestApply"]')) {
                    auth = 'guest_apply_available';
                }

                // Inspect visible input controls
                const visibleInputs = [...document.querySelectorAll('input:not([type="hidden"]), select, textarea, [role="combobox"], [role="textbox"]')].map(el => {
                    return {
                        tag: el.tagName.toLowerCase(),
                        type: el.type || el.getAttribute('role') || '',
                        id: el.id,
                        name: el.name,
                        placeholder: el.placeholder || '',
                        automation_id: el.getAttribute('data-automation-id') || el.getAttribute('data-oj-automation-id') || '',
                        aria_label: el.getAttribute('aria-label') || ''
                    };
                }).slice(0, 15);

                // Detect file inputs
                const fileInputs = [...document.querySelectorAll('input[type="file"]')].map(el => ({
                    id: el.id,
                    name: el.name,
                    accept: el.accept,
                    automation_id: el.getAttribute('data-automation-id') || ''
                }));

                return {
                    auth_gate: auth,
                    visible_controls: visibleInputs,
                    file_inputs: fileInputs
                };
            }""")

            recon_data["auth_gate_type"] = step_analysis.get("auth_gate", "unknown")
            recon_data["input_controls_sample"] = step_analysis.get("visible_controls", [])
            recon_data["file_inputs"] = step_analysis.get("file_inputs", [])
            print(f"  -> Post-Apply Auth Gate: {recon_data['auth_gate_type']}")
            print(f"  -> Visible Controls Found: {len(recon_data['input_controls_sample'])}")

        except Exception as act_err:
            recon_data["errors"].append(f"Action error: {str(act_err)}")
            print(f"  -> Action Notice: {str(act_err)[:80]}")

        # Capture accessibility snapshot image
        snap_file = SNAPSHOT_DIR / f"{app_id}_{company.lower().replace(' ', '_')}_{platform}.png"
        try:
            page.screenshot(path=str(snap_file), full_page=False)
            recon_data["screenshot_path"] = str(snap_file)
            print(f"  -> Screenshot saved: {snap_file.name}")
        except Exception as snap_err:
            recon_data["errors"].append(f"Snapshot error: {str(snap_err)}")

        # Synthetic event recommendation profile
        if platform == "workday":
            recon_data["synthetic_event_profile"] = {
                "engine": "React 18 Synthetic Event Dispatcher",
                "required_dispatch": [
                    "Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set.call(el, val)",
                    "el.dispatchEvent(new Event('input', { bubbles: true }))",
                    "el.dispatchEvent(new Event('change', { bubbles: true }))",
                    "el.dispatchEvent(new FocusEvent('blur', { bubbles: true }))"
                ],
                "playwright_best_practice": "page.locator('[data-automation-id=\"...\"]').fill(val)",
                "critical_trap": "Never use el.value = 'val' directly without prototype setter; React 18 internal fiber ignores native DOM values."
            }
        else: # oracle_cloud
            recon_data["synthetic_event_profile"] = {
                "engine": "Oracle JET / Knockout Observable Dispatcher",
                "required_dispatch": [
                    "input.dispatchEvent(new Event('input', { bubbles: true }))",
                    "input.dispatchEvent(new Event('change', { bubbles: true }))",
                    "ojComponent.setProperty('value', val) or ko.dataFor(el).value(val)"
                ],
                "playwright_best_practice": "page.locator('oj-input-text input').fill(val) + page.keyboard.press('Tab')",
                "critical_trap": "Oracle JET oj-select-one and oj-combobox require waiting for .oj-listbox-drop to attach before selecting."
            }

    except Exception as e:
        recon_data["errors"].append(str(e))
        print(f"  -> ERROR during {app_id}: {str(e)[:100]}")

    return recon_data

def main():
    print("======================================================================")
    print("LAUNCHING DEEP RECON: 5 WORKDAY + 5 ORACLE CLOUD ENTERPRISE PORTALS")
    print("======================================================================")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--window-size=1440,900"
            ]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for target in TARGET_APPLICATIONS:
            recon = analyze_target(page, target)
            results.append(recon)
            time.sleep(1)

        browser.close()

    # Save structured telemetry dump
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n======================================================================")
    print(f"RECON COMPLETE! Telemetry persisted to: {OUTPUT_JSON}")
    print(f"Total Applications Analyzed: {len(results)}/10")
    print("======================================================================")

if __name__ == "__main__":
    main()
