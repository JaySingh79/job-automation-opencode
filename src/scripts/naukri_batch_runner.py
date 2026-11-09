"""
Naukri Batch Apply Runner
Autonomous runner for native Naukri internal applications.
Follows human emulation rules, answers chatbot screeners and recruiter drawers,
and records checkpoints strictly in designated subfolders.
"""

import sys
import os
import json
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright

PROGRESS_FILE = "src/application_progress/naukri/naukri_progress.json"
APPLIED_FILE = "src/applied/naukri.json"
COOKIES_FILE = "src/application_progress/naukri/naukri_cookies.json"
AUTHORITY_FILE = "src/submit_permisssions/naukri_submit_authority.json"

def human_delay(min_ms=800, max_ms=1800):
    time.sleep(random.uniform(min_ms / 1000.0, max_ms / 1000.0))

def load_applied_ids():
    applied = set()
    if os.path.exists(APPLIED_FILE):
        try:
            with open(APPLIED_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    if "job_id" in item:
                        applied.add(str(item["job_id"]))
        except Exception:
            pass
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("jobs", []):
                    if item.get("status") in ["applied", "already_applied"]:
                        applied.add(str(item.get("job_id")))
        except Exception:
            pass
    return applied

def record_application(job_record):
    os.makedirs(os.path.dirname(APPLIED_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)

    # 1. Update applied/naukri.json
    applied_list = []
    if os.path.exists(APPLIED_FILE):
        try:
            with open(APPLIED_FILE, "r", encoding="utf-8") as f:
                applied_list = json.load(f)
        except Exception:
            applied_list = []
    
    # Avoid duplicate in list
    if not any(str(x.get("job_id")) == str(job_record.get("job_id")) for x in applied_list):
        applied_list.append(job_record)
        with open(APPLIED_FILE, "w", encoding="utf-8") as f:
            json.dump(applied_list, f, indent=2)

    # 2. Update progress file
    progress_data = {"last_updated": datetime.now().isoformat(), "jobs": []}
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                progress_data = json.load(f)
        except Exception:
            pass
    
    # Replace or append
    jobs = progress_data.get("jobs", [])
    found = False
    for i, j in enumerate(jobs):
        if str(j.get("job_id")) == str(job_record.get("job_id")):
            jobs[i] = job_record
            found = True
            break
    if not found:
        jobs.append(job_record)
    progress_data["jobs"] = jobs
    progress_data["last_updated"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, indent=2)

def handle_chatbot(page):
    """Answers Naukri interactive chatbot questions."""
    for step in range(12):
        time.sleep(1.5)
        # Check if chat is still visible
        chat_visible = page.evaluate("() => !!document.querySelector('.chatbot_MessageContainer')")
        if not chat_visible:
            break
        
        # Check if already redirecting to confirmation
        url = page.url
        if "saveApply" in url or "confirmation" in url:
            break

        # Check recent bot message text
        res = page.evaluate("""() => {
            const msgs = Array.from(document.querySelectorAll('.chatbot_ListItem, .botMsg')).map(m => m.innerText.trim());
            const text = msgs.slice(-4).join(' ');
            return {
                text,
                hasGrad: /graduation|grad|batch|year/i.test(text),
                hasLocation: /location|city/i.test(text),
                hasExp: /experience/i.test(text),
                hasNotice: /notice/i.test(text),
                hasCTC: /ctc|salary|lpa/i.test(text),
                hasThankYou: /thank you/i.test(text),
                hasEditable: !!document.querySelector('.textArea[contenteditable="true"]'),
                hasLabel2026: !!document.querySelector('label[for="2026"]'),
                hasMcc: !!document.querySelector('.multicheckboxes-container')
            };
        }""")

        if res.get("hasThankYou"):
            print("    [Chatbot] Thank you message received, waiting for confirmation...")
            time.sleep(2)
            break

        if res.get("hasGrad") and res.get("hasLabel2026"):
            print("    [Chatbot] Selecting Graduation Year: 2026")
            page.evaluate("""() => {
                const l = document.querySelector('label[for="2026"]');
                if (l) l.click();
            }""")
            human_delay(400, 800)
            page.evaluate("""() => {
                const btn = document.querySelector('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
                if (btn) btn.click();
            }""")
            continue

        if res.get("hasLocation") and res.get("hasEditable"):
            print("    [Chatbot] Typing Location: Gurgaon")
            page.evaluate("""() => {
                const ed = document.querySelector('.textArea[contenteditable="true"]');
                if (ed) {
                    ed.innerText = 'Gurgaon';
                    ed.dispatchEvent(new Event('input', { bubbles: true }));
                    ed.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""")
            human_delay(400, 800)
            page.evaluate("""() => {
                const btn = document.querySelector('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
                if (btn) btn.click();
            }""")
            continue

        if res.get("hasExp") and res.get("hasEditable"):
            print("    [Chatbot] Typing Experience: 1.5 Years")
            page.evaluate("""() => {
                const ed = document.querySelector('.textArea[contenteditable="true"]');
                if (ed) {
                    ed.innerText = '1.5 Years';
                    ed.dispatchEvent(new Event('input', { bubbles: true }));
                    ed.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""")
            human_delay(400, 800)
            page.evaluate("""() => {
                const btn = document.querySelector('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
                if (btn) btn.click();
            }""")
            continue

        if res.get("hasNotice") and res.get("hasEditable"):
            print("    [Chatbot] Typing Notice Period: Immediate")
            page.evaluate("""() => {
                const ed = document.querySelector('.textArea[contenteditable="true"]');
                if (ed) {
                    ed.innerText = 'Immediate';
                    ed.dispatchEvent(new Event('input', { bubbles: true }));
                    ed.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""")
            human_delay(400, 800)
            page.evaluate("""() => {
                const btn = document.querySelector('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
                if (btn) btn.click();
            }""")
            continue

        if res.get("hasCTC") and res.get("hasEditable"):
            print("    [Chatbot] Typing Current/Expected CTC (Current: 18 LPA, Expected: 22 LPA)")
            ctc_val = '18 LPA' if 'current' in res.get('text', '').lower() else '22 LPA'
            page.evaluate(f"""() => {{
                const ed = document.querySelector('.textArea[contenteditable="true"]');
                if (ed) {{
                    ed.innerText = '{ctc_val}';
                    ed.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    ed.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            }}""")
            human_delay(400, 800)
            page.evaluate("""() => {
                const btn = document.querySelector('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
                if (btn) btn.click();
            }""")
            continue

        # If any checkboxes or radio buttons are present
        if res.get("hasMcc"):
            print("    [Chatbot] Handling multicheckbox options...")
            page.evaluate("""() => {
                // Select first matching or appropriate checkbox
                const inputs = Array.from(document.querySelectorAll('.multicheckboxes-container input[type="checkbox"], .multicheckboxes-container input[type="radio"]'));
                for (const input of inputs) {
                    const label = document.querySelector(`label[for="${input.id}"]`)?.innerText || input.value || '';
                    if (/yes|python|ai|ml|agree|2026/i.test(label) || inputs.length === 1) {
                        input.click();
                        break;
                    }
                }
                if (inputs.length > 0 && !inputs.some(i => i.checked)) {
                    inputs[0].click();
                }
            }""")
            human_delay(400, 800)
            page.evaluate("""() => {
                const btn = document.querySelector('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
                if (btn) btn.click();
            }""")
            continue

        # Generic editable input fallback
        if res.get("hasEditable"):
            print("    [Chatbot] Answering generic prompt with 'Yes'...")
            page.evaluate("""() => {
                const ed = document.querySelector('.textArea[contenteditable="true"]');
                if (ed && !ed.innerText.trim()) {
                    ed.innerText = 'Yes';
                    ed.dispatchEvent(new Event('input', { bubbles: true }));
                    ed.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""")
            human_delay(400, 800)
            page.evaluate("""() => {
                const btn = document.querySelector('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
                if (btn) btn.click();
            }""")
            continue

def process_single_job(context, job):
    job_id = str(job.get("job_id"))
    title = job.get("title")
    company = job.get("company")
    url = job.get("url")

    print(f"\n---> Processing: [{job_id}] {title} @ {company}")
    page = context.new_page()

    result = {
        "job_id": job_id,
        "title": title,
        "company": company,
        "url": url,
        "applied_at": datetime.now().isoformat(),
        "status": "pending",
        "verification": None
    }

    try:
        page.goto(url, timeout=35000, wait_until="domcontentloaded")
        time.sleep(1.5)

        # 4 smooth viewport scrolls
        h = page.evaluate("() => document.body.scrollHeight")
        for frac in [0.25, 0.50, 0.75, 1.0]:
            page.evaluate(f"window.scrollTo({{ top: {h * frac}, behavior: 'smooth' }})")
            time.sleep(random.uniform(0.3, 0.6))
        page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        time.sleep(0.5)

        # Check if already applied
        state = page.evaluate("""() => {
            const body = document.body.innerText;
            const already = /already applied|application sent/i.test(body);
            const applyBtn = document.querySelector('#apply-button, .apply-button, button.apply-button');
            const btnText = applyBtn ? applyBtn.innerText.trim() : null;
            return {
                already,
                btnText,
                hasApplyBtn: !!applyBtn
            };
        }""")

        if state.get("already") or state.get("btnText") == "Applied":
            print(f"    [State] Job already applied previously.")
            result["status"] = "already_applied"
            result["verification"] = "Already applied marker present on page"
            record_application(result)
            page.close()
            return result

        if not state.get("hasApplyBtn"):
            print(f"    [Skip] No apply button found on page (likely closed or redirect).")
            result["status"] = "skipped"
            result["verification"] = "No native apply button found"
            record_application(result)
            page.close()
            return result

        # Check if external flow
        if "company site" in (state.get("btnText") or "").lower():
            print(f"    [Skip] External flow detected: '{state.get('btnText')}'")
            result["status"] = "skipped"
            result["verification"] = "External company site button"
            record_application(result)
            page.close()
            return result

        # Click Apply
        print(f"    [Action] Clicking Apply button...")
        page.evaluate("""() => {
            const btn = document.querySelector('#apply-button, .apply-button, button.apply-button');
            if (btn) btn.click();
        }""")
        time.sleep(2.5)

        # Check for immediate chatbot or drawer or confirmation
        current_url = page.url
        if "saveApply" in current_url or "confirmation" in current_url:
            print("    [Success] Immediate 1-click apply confirmation!")
            result["status"] = "applied"
            result["verification"] = f"Redirected to confirmation: {current_url}"
            record_application(result)
            page.close()
            return result

        # Check chatbot
        is_chat = page.evaluate("() => !!document.querySelector('.chatbot_MessageContainer')")
        if is_chat:
            print("    [Chatbot] Interactive chatbot detected, answering screening questions...")
            handle_chatbot(page)
            time.sleep(3)

        # Re-check confirmation
        conf_state = page.evaluate("""() => {
            const body = document.body.innerText;
            const url = window.location.href;
            const isConfirmed = /successfully applied|application sent|thank you for applying|apply confirmation/i.test(body) || /saveApply|confirmation/i.test(url);
            return {
                isConfirmed,
                url,
                title: document.title
            };
        }""")

        if conf_state.get("isConfirmed"):
            print(f"    [Success] Confirmed applied! URL: {conf_state.get('url')}")
            result["status"] = "applied"
            result["verification"] = f"Confirmed via {conf_state.get('title')} ({conf_state.get('url')})"
            record_application(result)
        else:
            print(f"    [Review] Form staged or awaiting review: {conf_state.get('url')}")
            result["status"] = "ready_for_human_submission"
            result["verification"] = f"Form completed; URL: {conf_state.get('url')}"
            record_application(result)

    except Exception as e:
        print(f"    [Error] Exception during job processing: {str(e)[:150]}")
        result["status"] = "error"
        result["verification"] = str(e)[:150]
        record_application(result)
    finally:
        try:
            page.close()
        except Exception:
            pass

    return result

def run_batch(batch_num):
    queue_path = f"src/job_search_results/naukri/naukri_internal_queue_batch{batch_num}.json"
    if not os.path.exists(queue_path):
        print(f"Queue file not found: {queue_path}")
        return

    with open(queue_path, "r", encoding="utf-8") as f:
        queue_data = json.load(f)

    jobs = queue_data.get("jobs", [])
    print(f"\n=======================================================")
    print(f"Starting Naukri Subagent Batch {batch_num} ({len(jobs)} jobs)")
    print(f"Queue: {queue_path}")
    print(f"=======================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )

        # Load session cookies
        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            # Filter valid cookie keys for playwright
            clean_cookies = []
            for c in cookies:
                clean_cookies.append({
                    "name": c["name"],
                    "value": c["value"],
                    "domain": c["domain"],
                    "path": c.get("path", "/")
                })
            context.add_cookies(clean_cookies)
            print(f"Loaded {len(clean_cookies)} session cookies into browser context.")

        for idx, job in enumerate(jobs, 1):
            print(f"\n[Batch {batch_num} - Job {idx}/{len(jobs)}]")
            process_single_job(context, job)
            human_delay(1000, 2500)

        browser.close()

    print(f"\n=======================================================")
    print(f"Completed Naukri Subagent Batch {batch_num}!")
    print(f"=======================================================\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        run_batch(int(sys.argv[1]))
    elif len(sys.argv) > 1 and sys.argv[1] == "all":
        for b in [1, 2, 3, 4]:
            run_batch(b)
    else:
        run_batch(1)
