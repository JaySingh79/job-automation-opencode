"""
Deep Reconnaissance Engine for Direct Corporate Career Portals.
Systematically probes 10 benchmark enterprise corporate career portals
(Google, Apple, Barclays, EY, Crisil, Synopsys, PayU, Tesco, Interactive Brokers, Findoc/Akasa)
to map DOM components, JS hydration frameworks, synthetic event dispatches,
authentication models, and anti-bot honeypots.
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
OUTPUT_JSON = ROOT / "src" / "knowledge_source" / "ats_direct_corporate_deep_recon.json"

SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

TARGET_APPLICATIONS = [
    {
        "id": "CORP-01",
        "company": "Google",
        "role": "Software Engineer (University Graduate 2026)",
        "domain": "www.google.com",
        "platform_type": "google_careers",
        "url": "https://www.google.com/about/careers/applications/jobs/results/111007517923779270-software-engineer-university-graduate-2026"
    },
    {
        "id": "CORP-02",
        "company": "Apple",
        "role": "Software Development Engineer - Automation Tools",
        "domain": "jobs.apple.com",
        "platform_type": "apple_jobs",
        "url": "https://jobs.apple.com/en-in/details/200675618-0321/software-development-engineer-automation-tools?team=HRDWR"
    },
    {
        "id": "CORP-03",
        "company": "Barclays",
        "role": "Software Engineer",
        "domain": "search.jobs.barclays",
        "platform_type": "phenom_people",
        "url": "https://search.jobs.barclays/job/pune/software-engineer/13015/95536470528"
    },
    {
        "id": "CORP-04",
        "company": "EY",
        "role": "Associate Consultant",
        "domain": "careers.ey.com",
        "platform_type": "sap_successfactors",
        "url": "https://careers.ey.com/ey/job/Mumbai-Associate-Consultant-Business-Consulting-Risk-FS-CNS-RISK-ACTUARIAL-Mumbai-Delhi-MH-400028/1444331333/"
    },
    {
        "id": "CORP-05",
        "company": "Crisil",
        "role": "Associate Engineer-Gen AI",
        "domain": "career.crisil.com",
        "platform_type": "custom_enterprise_taleo",
        "url": "https://career.crisil.com/crisil/jobview/associate-engineer-gen-ai-pune-maharashtra-india-2026083113512451"
    },
    {
        "id": "CORP-06",
        "company": "Synopsys",
        "role": "Intern",
        "domain": "careers.synopsys.com",
        "platform_type": "phenom_people",
        "url": "https://careers.synopsys.com/job/bengaluru/intern/44408/95298114432"
    },
    {
        "id": "CORP-07",
        "company": "PayU",
        "role": "Data Scientist",
        "domain": "careers.payu.in",
        "platform_type": "sap_successfactors",
        "url": "https://careers.payu.in/PayU/job/Gurgaon-Data-Scientist/53331580/"
    },
    {
        "id": "CORP-08",
        "company": "Tesco",
        "role": "Data Scientist",
        "domain": "careers.tesco.com",
        "platform_type": "bespoke_tesco",
        "url": "https://careers.tesco.com/en_GB/careers/JobDetail/Data-Scientist/140615"
    },
    {
        "id": "CORP-09",
        "company": "Interactive Brokers",
        "role": "Jr Engineer - Software (iOS)",
        "domain": "jobs.dayforcehcm.com",
        "platform_type": "dayforce_hcm",
        "url": "https://jobs.dayforcehcm.com/en-US/ibgllc/CANDIDATEPORTAL/jobs/1495"
    },
    {
        "id": "CORP-10",
        "company": "Findoc Investmart",
        "role": "Quant Researcher Machine Learning",
        "domain": "www.findoc.com",
        "platform_type": "custom_startup_portal",
        "url": "https://www.findoc.com/career/671573000008854035"
    }
]

def perform_telemetry_scrolls(page):
    """Executes 4 smooth viewport scrolls to trigger lazy observers."""
    try:
        for pct in [0.25, 0.50, 0.75, 1.0]:
            page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {pct});")
            time.sleep(0.3)
        page.evaluate("window.scrollTo(0, 0);")
        time.sleep(0.3)
    except Exception:
        pass

def analyze_target(page, target):
    app_id = target["id"]
    url = target["url"]
    company = target["company"]
    platform_type = target["platform_type"]
    
    print(f"\n=======================================================")
    print(f"[{app_id}] Probing {company} ({platform_type}) -> {url[:75]}...")
    print(f"=======================================================")

    recon_data = {
        "id": app_id,
        "company": company,
        "role": target["role"],
        "platform_type": platform_type,
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
        "honeypot_detected": False,
        "honeypot_selectors": [],
        "input_controls_sample": [],
        "synthetic_event_profile": {},
        "screenshot_path": None,
        "errors": []
    }

    start_time = time.time()
    try:
        response = page.goto(url, wait_until="domcontentloaded", timeout=40000)
        recon_data["load_time_ms"] = int((time.time() - start_time) * 1000)
        if response:
            recon_data["http_status"] = response.status
        
        # Hydration pause
        time.sleep(3)
        recon_data["final_url"] = page.url
        recon_data["page_title"] = page.title().strip()

        # Check and dismiss generic cookie consent banners
        try:
            cookie_btn = page.locator('button:has-text("Accept"), button:has-text("I Agree"), button:has-text("Agree"), .cookie-consent__button.accept, #onetrust-accept-btn-handler, [data-automation-id="legalNoticeAcceptButton"]').first
            if cookie_btn.count() > 0 and cookie_btn.is_visible():
                cookie_btn.click()
                time.sleep(1)
                print("  -> Dismissed cookie consent banner")
        except Exception:
            pass

        # Perform 4 telemetry scrolls
        perform_telemetry_scrolls(page)

        # Inspect DOM & detect frameworks
        dom_analysis = page.evaluate("""() => {
            const fw = [];
            if (window.React || document.querySelector('[data-reactroot], [data-reactid], #root, #app')) fw.push('React');
            if (window.angular || document.querySelector('[ng-app], [ng-controller], [ng-version]')) fw.push('Angular');
            if (window.Vue || document.querySelector('[data-v-]')) fw.push('Vue');
            if (window.Polymer) fw.push('Polymer');
            if (window.jQuery || window.$) fw.push('jQuery');
            if (document.querySelector('oj-dialog, [class*="oj-"]')) fw.push('Oracle JET');
            if (window.phenom || document.querySelector('[class*="phenom"], [data-ph-id]')) fw.push('Phenom People');

            // Unique custom elements
            const customElements = [...document.querySelectorAll('*')]
                .map(el => el.tagName.toLowerCase())
                .filter(tag => tag.includes('-'))
                .slice(0, 15);

            // Stale job signals
            const bodyText = document.body.innerText.toLowerCase();
            const isStale = bodyText.includes("no longer available") || 
                            bodyText.includes("job has expired") || 
                            bodyText.includes("job is closed") || 
                            bodyText.includes("page doesn't exist") ||
                            bodyText.includes("not found");

            // Honeypot fields inspection (hidden text inputs or traps)
            const honeypots = [];
            document.querySelectorAll('input[type="text"]').forEach(el => {
                const name = (el.name || '').toLowerCase();
                const id = (el.id || '').toLowerCase();
                const autoId = (el.getAttribute('data-automation-id') || '').toLowerCase();
                const style = window.getComputedStyle(el);
                const isHidden = style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0' || el.offsetWidth === 0;

                if (name.includes('honey') || id.includes('honey') || name.includes('beecatcher') || autoId.includes('beecatcher') || isHidden) {
                    honeypots.push({ name: el.name, id: el.id, auto_id: autoId, isHidden });
                }
            });

            // Count interactive controls
            const inputs = document.querySelectorAll('input:not([type="hidden"])').length;
            const selects = document.querySelectorAll('select').length;
            const buttons = document.querySelectorAll('button, a[role="button"]').length;

            return {
                frameworks: fw,
                custom_elements: [...new Set(customElements)],
                is_stale: isStale,
                honeypots: honeypots,
                counts: { inputs, selects, buttons }
            };
        }""")

        recon_data["frameworks_detected"] = dom_analysis.get("frameworks", [])
        recon_data["dom_metrics"] = dom_analysis
        if dom_analysis.get("honeypots"):
            recon_data["honeypot_detected"] = True
            recon_data["honeypot_selectors"] = dom_analysis.get("honeypots")

        # Locate Apply CTA
        apply_probe = page.evaluate("""() => {
            const allElements = [...document.querySelectorAll('a, button, [role="button"]')];
            const candidate = allElements.find(el => {
                const txt = (el.textContent || '').trim().toLowerCase();
                const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                return txt === 'apply' || txt === 'apply now' || txt === 'apply for this job' || 
                       txt === 'start application' || aria.includes('apply now') || aria === 'apply';
            });

            if (candidate) {
                return {
                    found: true,
                    text: (candidate.textContent || '').trim(),
                    tag: candidate.tagName.toLowerCase(),
                    id: candidate.id || '',
                    className: (candidate.className || '').toString().slice(0, 50),
                    href: candidate.getAttribute('href') || ''
                };
            }
            return { found: false, text: '', tag: '', id: '', className: '', href: '' };
        }""")

        recon_data["apply_button_found"] = apply_probe.get("found", False)
        recon_data["apply_button_text"] = apply_probe.get("text", "")
        recon_data["apply_button_selector"] = apply_probe.get("id") or apply_probe.get("className") or apply_probe.get("tag")

        print(f"  -> Title: {recon_data['page_title']}")
        print(f"  -> Frameworks: {recon_data['frameworks_detected']}")
        print(f"  -> Stale Signal: {dom_analysis.get('is_stale')}")
        print(f"  -> Apply CTA Found: {recon_data['apply_button_found']} ('{recon_data['apply_button_text']}')")
        if recon_data["honeypot_detected"]:
            print(f"  -> [HONEYPOT DETECTED]: {recon_data['honeypot_selectors']}")

        # Test Apply action & observe Step 1 / Auth Gate
        if recon_data["apply_button_found"] and not dom_analysis.get("is_stale"):
            try:
                apply_locator = page.locator('a:has-text("Apply Now"), button:has-text("Apply Now"), a:has-text("Apply"), button:has-text("Apply"), a:has-text("Apply for this job"), button:has-text("Apply for this job")').first
                if apply_locator.count() > 0 and apply_locator.is_visible():
                    recon_data["navigation_action"] = "clicked_apply"
                    apply_locator.click()
                    time.sleep(4)

                    recon_data["first_step_url"] = page.url

                    # Inspect the transition for Auth Gates and Steppers
                    step_analysis = page.evaluate("""() => {
                        const url = window.location.href;
                        const bodyText = document.body.innerText.toLowerCase();

                        let auth = 'none_or_guest';
                        if (url.includes('accounts.google.com') || bodyText.includes('sign in with google')) {
                            auth = 'google_oauth_gate';
                        } else if (url.includes('appleid.apple.com') || bodyText.includes('sign in with apple')) {
                            auth = 'apple_id_gate';
                        } else if (document.querySelector('input[type="password"]') || bodyText.includes('create account') || bodyText.includes('sign in to apply')) {
                            auth = 'account_password_gate';
                        } else if (bodyText.includes('verification code') || bodyText.includes('one-time password') || bodyText.includes('enter otp')) {
                            auth = 'email_otp_challenge';
                        } else if (document.querySelector('input[type="file"]') || document.querySelector('input[name*="name"], input[name*="email"]')) {
                            auth = 'direct_form_no_gate';
                        }

                        // Inspect visible input controls
                        const visibleInputs = [...document.querySelectorAll('input:not([type="hidden"]), select, textarea')].map(el => {
                            return {
                                tag: el.tagName.toLowerCase(),
                                type: el.type || '',
                                id: el.id || '',
                                name: el.name || '',
                                placeholder: el.placeholder || '',
                                aria_label: el.getAttribute('aria-label') || ''
                            };
                        }).slice(0, 15);

                        return {
                            auth_gate: auth,
                            visible_controls: visibleInputs
                        };
                    }""")

                    recon_data["auth_gate_type"] = step_analysis.get("auth_gate", "unknown")
                    recon_data["input_controls_sample"] = step_analysis.get("visible_controls", [])
                    print(f"  -> Post-Apply Auth Gate: {recon_data['auth_gate_type']}")
                    print(f"  -> Visible Controls Count: {len(recon_data['input_controls_sample'])}")

            except Exception as act_err:
                recon_data["errors"].append(f"Action error: {str(act_err)}")
                print(f"  -> Action Notice: {str(act_err)[:80]}")

        # Capture snapshot
        snap_file = SNAPSHOT_DIR / f"{app_id}_{company.lower().replace(' ', '_')}_{platform_type}.png"
        try:
            page.screenshot(path=str(snap_file), full_page=False)
            recon_data["screenshot_path"] = str(snap_file)
            print(f"  -> Screenshot saved: {snap_file.name}")
        except Exception as snap_err:
            recon_data["errors"].append(f"Snapshot error: {str(snap_err)}")

        # Synthetic event recommendation
        if "React" in recon_data["frameworks_detected"]:
            recon_data["synthetic_event_profile"] = {
                "engine": "React Prototype Setter",
                "recommendation": "Use page.locator().fill() or React prototype setter with input, change, and blur event dispatch."
            }
        elif "Angular" in recon_data["frameworks_detected"]:
            recon_data["synthetic_event_profile"] = {
                "engine": "Angular ngModel",
                "recommendation": "Use page.locator().fill() followed by page.keyboard.press('Tab') to trigger ngModelChange."
            }
        elif "Phenom People" in recon_data["frameworks_detected"]:
            recon_data["synthetic_event_profile"] = {
                "engine": "Phenom People Experience Platform",
                "recommendation": "Native Playwright fill on standard form elements; verify resume auto-parser status."
            }
        elif "Oracle JET" in recon_data["frameworks_detected"]:
            recon_data["synthetic_event_profile"] = {
                "engine": "Oracle JET Knockout Observables",
                "recommendation": "Native Playwright fill followed by Tab press, skipping any input with name='honey-pot'."
            }
        else:
            recon_data["synthetic_event_profile"] = {
                "engine": "Standard HTML5 / DOM Events",
                "recommendation": "Native Playwright page.locator().fill() with human delay."
            }

    except Exception as e:
        recon_data["errors"].append(str(e))
        print(f"  -> ERROR during {app_id}: {str(e)[:100]}")

    return recon_data

def main():
    print("======================================================================")
    print("LAUNCHING DEEP RECON: 10 DIRECT CORPORATE ENTERPRISE PORTALS")
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
    print(f"Total Corporate Portals Analyzed: {len(results)}/10")
    print("======================================================================")

if __name__ == "__main__":
    main()
