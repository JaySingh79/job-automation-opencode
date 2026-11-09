"""
Universal ATS Filler Engine (v2.0) — Ashby, Greenhouse, Lever, SmartRecruiters.
Powered by Patchright (CDP Runtime.enable leak patched) + Deep Shadow DOM Traversal.
Implements all 10 Plans & Iteration 1 Root-Cause Fixes:
  - Verified Resume Path (`Resumes/Jay Resume GenAI+DS 5th Aug.pdf`)
  - Greenhouse React-Select strict `.select__option` scoping (ignoring 244 hidden `li.iti__country` nodes)
  - Greenhouse `Apply` tab/button auto-expander (`button:has-text("Apply")`)
  - Ashby `input[type="file"]` custom dropzone validation check + secondary file input upload
  - Lever `input#location-input` custom validity reset & autocomplete handler
  - SmartRecruiters Patchright `channel="chrome"` DataDome bypass + Deep Shadow DOM (`spl-*`, `oc-*`) Step 1 -> Step 2 Screening + `spl-checkbox[data-test="consent-box"]` handler
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import json
import os
import random
import re
import sys
import time
import traceback
from pathlib import Path
from typing import Any

from patchright.sync_api import sync_playwright, Page, Frame, Locator

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
RESUME_DEFAULT = ROOT / "Resumes" / "Resume ML_Vision_RL_PPO 7th Aug.pdf"
SNAP_DIR = ROOT / "src" / "accessability_snapshot" / "universal_eval"
PROGRESS_DIR = ROOT / "src" / "application_progress"
LOG_MD_PATH = ROOT / "src" / "knowledge_source" / "ats_mastery_log.md"

SNAP_DIR.mkdir(parents=True, exist_ok=True)
PROGRESS_DIR.mkdir(parents=True, exist_ok=True)

CANDIDATE = {
    "first_name": "Jay",
    "last_name": "Singh",
    "full_name": "Jay Singh",
    "preferred_name": "Jay",
    "email": "jays.iitkgp@gmail.com",
    "phone_national": "8651274328",
    "phone_intl": "+918651274328",
    "phone_hyphen": "+91-8651274328",
    "city": "Bengaluru",
    "state": "Karnataka",
    "country": "India",
    "postal_code": "560001",
    "address": "Bengaluru, Karnataka, India",
    "location_full": "Bengaluru, Karnataka, India",
    "linkedin": "https://www.linkedin.com/in/jay-singh-adc/",
    "github": "https://github.com/jaysingh-ai",
    "portfolio": "https://github.com/jaysingh-ai",
    "website": "https://github.com/jaysingh-ai",
    "university": "Indian Institute of Technology (IIT) Kharagpur",
    "university_short": "IIT Kharagpur",
    "degree": "Bachelor's Degree",
    "discipline": "Computer Science",
    "gpa": "8.4",
    "grad_year": "2024",
    "start_year": "2020",
    "current_company": "AI-First Product Studio",
    "current_title": "Software & Machine Learning Engineer",
    "yoe_numeric": "2",
    "ctc_current_lpa": "18",
    "ctc_expected_lpa": "22",
    "ctc_expected_usd": "85000",
    "notice_days": "7",
    "notice_text": "Immediate / 7 days",
    "start_date_iso": (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
    "start_date_us": (datetime.date.today() + datetime.timedelta(days=7)).strftime("%m/%d/%Y"),
    "pronouns": "He/him",
    "gender": "Male",
    "ethnicity": "Asian",
    "veteran": "I am not a protected veteran",
    "disability": "No, I do not have a disability",
    "pitch": (
        "IIT Kharagpur graduate and Software/AI Engineer with hands-on experience architecting "
        "multi-agent LLM systems (DFR-Tracer on LangGraph with 94% precision), distributed Python/FastAPI "
        "microservices, and sub-second RAG & computer vision pipelines in production. Excited to bring "
        "high-velocity engineering and deep system reliability to your team."
    ),
}


def human_delay(min_s: float = 0.35, max_s: float = 0.85):
    time.sleep(random.uniform(min_s, max_s))


def human_scroll_4x(page: Page):
    """Mandatory 4x smooth scroll across page height (25% -> 50% -> 75% -> 100% -> top) with mouse movement."""
    try:
        total_height = page.evaluate(
            "() => Math.max(document.body ? document.body.scrollHeight : 0, document.documentElement ? document.documentElement.scrollHeight : 0, 1200)"
        )
        for frac in (0.25, 0.50, 0.75, 1.0):
            target_y = int(total_height * frac)
            page.mouse.move(random.randint(250, 850), random.randint(180, 620), steps=4)
            page.evaluate(f"window.scrollTo({{ top: {target_y}, behavior: 'smooth' }})")
            time.sleep(random.uniform(0.30, 0.55))
        page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        time.sleep(random.uniform(0.30, 0.50))
    except Exception:
        pass


# ============================================================================
# PLAN 2: 120-PATTERN SEMANTIC QUESTION & OPTION SCORING BRAIN
# ============================================================================

class SemanticQuestionEngine:
    """Maps arbitrary question labels, placeholders, field types, and option lists to accurate candidate answers."""

    @staticmethod
    def answer_text(label: str, placeholder: str = "", name: str = "", input_type: str = "text") -> str:
        ctx = f"{label} {placeholder} {name}".lower().strip()

        if input_type == "date" or "yyyy-mm-dd" in ctx:
            return CANDIDATE["start_date_iso"]
        if "pick date" in ctx or "mm/dd/yyyy" in ctx or "start date" in ctx or "available to start" in ctx or "date available" in ctx:
            return CANDIDATE["start_date_us"]
        if input_type == "number":
            if any(k in ctx for k in ["gpa", "cgpa", "grade"]):
                return "8.4"
            if any(k in ctx for k in ["notice", "days"]):
                return "7"
            if any(k in ctx for k in ["current ctc", "current salary", "present ctc"]):
                return "18"
            if any(k in ctx for k in ["expected ctc", "expected salary", "desired salary", "compensation", "pay"]):
                return "22" if ("lpa" in ctx or "inr" in ctx or "lakh" in ctx) else "80000"
            if any(k in ctx for k in ["graduation", "year of passing", "batch", "end year"]):
                return "2024"
            if any(k in ctx for k in ["start year"]):
                return "2020"
            if any(k in ctx for k in ["age"]):
                return "23"
            return "2"

        if "confirm" in ctx and "email" in ctx:
            return CANDIDATE["email"]
        if "email" in ctx or input_type == "email":
            return CANDIDATE["email"]
        if "first name" in ctx or "given name" in ctx or name in ("first_name", "firstName", "first-name-input"):
            return CANDIDATE["first_name"]
        if "last name" in ctx or "surname" in ctx or "family name" in ctx or name in ("last_name", "lastName", "last-name-input"):
            return CANDIDATE["last_name"]
        if "preferred name" in ctx or "nickname" in ctx:
            return CANDIDATE["preferred_name"]
        if ("full name" in ctx or "your name" in ctx or "legal name" in ctx or name in ("name", "_systemfield_name")) and "company" not in ctx and "refer" not in ctx and "school" not in ctx:
            return CANDIDATE["full_name"]
        if "phone" in ctx or "mobile" in ctx or "contact number" in ctx or input_type == "tel":
            return CANDIDATE["phone_national"]

        if "linkedin" in ctx:
            return CANDIDATE["linkedin"]
        if "github" in ctx or "git" in ctx:
            return CANDIDATE["github"]
        if any(k in ctx for k in ["portfolio", "website", "personal site", "blog", "other url", "urls[", "url", "http", "link"]):
            return CANDIDATE["portfolio"]

        if "postal" in ctx or "zip" in ctx or "pincode" in ctx or "pin code" in ctx:
            return CANDIDATE["postal_code"]
        if "street" in ctx or "address line" in ctx:
            return CANDIDATE["address"]
        if "state" in ctx or "province" in ctx:
            return CANDIDATE["state"]
        if "country" in ctx:
            return CANDIDATE["country"]
        if "city" in ctx or "current location" in ctx or "location" in ctx or "residence" in ctx or "where are you based" in ctx:
            return CANDIDATE["location_full"]

        if any(k in ctx for k in ["university", "college", "school", "institution", "alma mater"]):
            return CANDIDATE["university"]
        if any(k in ctx for k in ["degree", "qualification", "education level"]):
            return CANDIDATE["degree"]
        if any(k in ctx for k in ["major", "discipline", "field of study", "specialization", "branch"]):
            return CANDIDATE["discipline"]
        if any(k in ctx for k in ["gpa", "cgpa", "percentage", "grade"]):
            return CANDIDATE["gpa"]
        if any(k in ctx for k in ["current company", "current employer", "organization", "recent employer"]) or name == "org":
            return CANDIDATE["current_company"]
        if any(k in ctx for k in ["current title", "job title", "current role", "designation", "position"]):
            return CANDIDATE["current_title"]

        if any(k in ctx for k in ["notice period", "how soon can you join", "when can you start", "availability", "earliest start"]):
            return CANDIDATE["notice_text"]
        if any(k in ctx for k in ["current ctc", "current salary", "present salary", "current compensation"]):
            return "18 LPA"
        if any(k in ctx for k in ["expected ctc", "expected salary", "desired salary", "compensation expectation", "salary expectation", "target compensation", "desired pay", "rate"]):
            return "22 LPA"
        if any(k in ctx for k in ["how many years", "years of experience", "total experience", "relevant experience"]):
            return "2"

        if any(k in ctx for k in ["refer", "who referred", "employee name"]):
            return "N/A"
        if any(k in ctx for k in ["how did you hear", "where did you hear", "source"]):
            return "LinkedIn"
        if any(k in ctx for k in ["pronoun"]):
            return "He/Him"
        if any(k in ctx for k in ["visa", "sponsorship", "require sponsorship"]):
            return "No"
        if any(k in ctx for k in ["authorized", "legally eligible", "right to work", "relocat", "hybrid", "onsite", "on-site", "in-office", "background check", "18 years"]):
            return "Yes"

        if any(k in ctx for k in ["why", "interest", "motivat", "tell us", "about yourself", "cover letter", "note", "additional", "anything else", "project", "experience", "accomplish", "challenge", "message to"]):
            return CANDIDATE["pitch"]

        return "Yes" if "?" in label else CANDIDATE["full_name"] if "name" in ctx else "2"

    @staticmethod
    def choose_yes_no(label: str) -> str:
        ctx = label.lower()
        negative_triggers = [
            "require sponsorship", "need sponsorship", "require visa", "need a visa",
            "require future sponsorship", "need work visa", "previously worked",
            "ever worked for", "formerly employed", "previously been employed",
            "previously employed", "non-compete", "non compete", "restrictive covenant",
            "conflict of interest", "relatives", "family member", "government official",
            "export control", "criminal", "convicted", "felony", "debarred", "sanctioned",
            "hispanic", "latino", "disability", "disabled", "veteran", "armed forces",
            "currently a student", "enrolled in", "require accommodation",
        ]
        for neg in negative_triggers:
            if neg in ctx:
                return "No"
        return "Yes"

    @staticmethod
    def pick_best_option(label: str, options: list[str]) -> str | None:
        valid_opts = [
            o.strip() for o in options
            if o and o.strip() and o.strip().lower() not in (
                "select...", "select", "select one", "choose...", "choose one",
                "--", "-- select --", "please select", "none", ""
            )
        ]
        if not valid_opts:
            return None

        ctx = label.lower()
        lower_map = [(o, o.lower()) for o in valid_opts]

        # 1. Pure Yes/No option set
        opt_lowers = {lo for _, lo in lower_map}
        if opt_lowers <= {"yes", "no", "y", "n", "true", "false"} or any(lo in ("yes", "no") for _, lo in lower_map):
            target_yn = SemanticQuestionEngine.choose_yes_no(label).lower()
            for orig, lo in lower_map:
                if lo == target_yn or lo.startswith(target_yn + " ") or lo.startswith(target_yn + ","):
                    return orig

        # 2. Country / Location
        if "country" in ctx or "location" in ctx or "where are you" in ctx or "based" in ctx or "live" in ctx:
            for kw in ["bengaluru", "bangalore", "hyderabad", "india +91", "india+91", "india", "remote", "asia", "united states", "other"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig

        # 3. Gender
        if "gender" in ctx or "sex" in ctx:
            for kw in ["male", "man", "decline", "prefer not", "not wish"]:
                for orig, lo in lower_map:
                    if lo == kw or lo.startswith(kw):
                        return orig

        # 4. Pronouns
        if "pronoun" in ctx:
            for kw in ["he/him", "he / him", "prefer not", "decline"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig

        # 5. Hispanic / Latino
        if "hispanic" in ctx or "latino" in ctx:
            for kw in ["no", "not hispanic", "decline", "prefer not"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig

        # 6. Race / Ethnicity
        if "race" in ctx or "ethnic" in ctx:
            for kw in ["asian", "south asian", "indian", "decline", "prefer not"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig

        # 7. Veteran status
        if "veteran" in ctx or "military" in ctx:
            for kw in ["not a protected veteran", "not a veteran", "no", "decline", "prefer not"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig

        # 8. Disability status
        if "disab" in ctx or "handicap" in ctx:
            for kw in ["do not have a disability", "no, i don't", "no", "decline", "prefer not"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig

        # 9. Education Degree
        if "degree" in ctx or "education" in ctx or "qualification" in ctx:
            for kw in ["bachelor", "b.tech", "b.s", "bs", "undergraduate", "master", "graduate", "university", "college"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig

        # 10. Discipline / Major
        if "discipline" in ctx or "major" in ctx or "field of study" in ctx:
            for kw in ["computer science", "engineering", "information technology", "artificial intelligence", "data science", "mathematics", "other"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig

        # 11. School / University
        if "school" in ctx or "university" in ctx or "college" in ctx:
            for kw in ["indian institute of technology", "iit", "kharagpur", "other"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig

        # 12. Months & Years
        if "month" in ctx:
            for kw in ["may", "june", "july", "august", "january", "05", "06", "1"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig
        if "year" in ctx and ("start" in ctx or "end" in ctx or "grad" in ctx):
            target_yr = "2020" if "start" in ctx else "2024"
            for orig, lo in lower_map:
                if target_yr in lo:
                    return orig

        # 13. How did you hear / Source
        if "hear" in ctx or "source" in ctx or "learn about" in ctx:
            for kw in ["linkedin", "job board", "company website", "career", "search engine", "google", "online", "other"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig

        # 14. Notice period / Availability
        if "notice" in ctx or "join" in ctx or "start" in ctx or "availab" in ctx:
            for kw in ["immediate", "0-15", "less than 15", "15 days", "2 weeks", "0 - 30", "30 days", "1 month", "yes"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig

        # 15. Experience Years bucket
        if "experience" in ctx or "years" in ctx:
            for kw in ["1-3", "1 - 3", "0-2", "0 - 2", "1-2", "2-4", "2+", "1+", "entry", "junior", "2"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig

        # 16. Authorization / Sponsorship / Policy Consent
        if any(k in ctx for k in ["sponsorship", "visa"]):
            for kw in ["no", "do not require", "will not require", "not require"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig
        if any(k in ctx for k in ["authoriz", "eligible", "right to work", "relocat", "consent", "agree", "privacy", "acknowledge", "confirm", "hybrid", "onsite", "office", "background check"]):
            for kw in ["yes", "i agree", "i consent", "accept", "authorized", "confirm", "understand"]:
                for orig, lo in lower_map:
                    if kw in lo:
                        return orig

        for kw in ["yes", "i agree", "confirm"]:
            for orig, lo in lower_map:
                if lo == kw or lo.startswith(kw + " "):
                    return orig

        return valid_opts[0]


# ============================================================================
# PLAN 5: TWO-PHASE REACT 18 / STENCIL NATIVE VALUE SETTER
# ============================================================================

def safe_fill_input(locator: Locator, value: str, is_long_prose: bool = False):
    try:
        locator.scroll_into_view_if_needed(timeout=2000)
    except Exception:
        pass

    try:
        cur = locator.input_value(timeout=1200)
        if cur and cur.strip() == value.strip():
            return True
    except Exception:
        pass

    if not is_long_prose and len(value) < 85:
        try:
            locator.click(timeout=1800)
            locator.fill(value, timeout=2000)
            locator.dispatch_event("change")
            locator.dispatch_event("blur")
            cur = locator.input_value(timeout=1000)
            if cur and cur.strip() == value.strip():
                return True
        except Exception:
            pass

    try:
        locator.evaluate(
            """(el, val) => {
                const proto = el.tagName === 'TEXTAREA'
                    ? window.HTMLTextAreaElement.prototype
                    : window.HTMLInputElement.prototype;
                const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
                if (setter) {
                    setter.call(el, 'x');
                    el.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
                    setter.call(el, val);
                } else {
                    el.value = val;
                }
                if (el.setCustomValidity) el.setCustomValidity('');
                el.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
                el.dispatchEvent(new Event('change', { bubbles: true, composed: true }));
                el.dispatchEvent(new FocusEvent('blur', { bubbles: true, composed: true }));
            }""",
            value,
        )
        return True
    except Exception:
        return False


# ============================================================================
# PLATFORM 1: ASHBY ENGINE (`jobs.ashbyhq.com`)
# ============================================================================

def fill_ashby_application(page: Page, url: str) -> dict[str, Any]:
    app_url = url.rstrip("/")
    if not app_url.endswith("/application"):
        app_url = app_url + "/application"

    page.goto(app_url, wait_until="domcontentloaded", timeout=35000)

    # Wait up to 10s for Ashby React 18 SPA to hydrate (`input#_systemfield_name` or `input[type='file']`)
    for _ in range(20):
        time.sleep(0.5)
        if page.locator("input#_systemfield_name, input#_systemfield_email, input[type='file']").count() > 0:
            break

    body_txt = page.locator("body").inner_text(timeout=5000).lower()
    if "job not found" in body_txt or "job posting not found" in body_txt or "no longer open" in body_txt or "job you are looking for is unavailable" in body_txt:
        return {"status": "SKIPPED_DEAD", "reason": "Ashby job closed"}

    if page.locator("input#_systemfield_name, input#_systemfield_email, input[type='file']").count() == 0:
        app_tab = page.locator("a:has-text('Application'), button:has-text('Application'), a:has-text('Apply')").first
        if app_tab.count() > 0:
            app_tab.click()
            for _ in range(12):
                time.sleep(0.5)
                if page.locator("input#_systemfield_name, input#_systemfield_email, input[type='file']").count() > 0:
                    break

    if page.locator("input#_systemfield_name, input#_systemfield_email, input[type='file']").count() == 0:
        return {"status": "SKIPPED_DEAD", "reason": "No Ashby application form"}

    human_scroll_4x(page)

    # STEP 1 (Plan 3): Upload Resume to `input#_systemfield_resume` AND any additional required file inputs (e.g. Cover Letter / Transcript)
    try:
        file_inputs = page.locator("input[type='file']")
        f_cnt = file_inputs.count()
        for fi in range(f_cnt):
            f_inp = file_inputs.nth(fi)
            fid = f_inp.get_attribute("id") or ""
            # Skip top "Autofill from resume" input if there are multiple file inputs and this one has no id
            if f_cnt > 1 and not fid:
                continue
            f_inp.set_input_files(str(RESUME_DEFAULT))
        time.sleep(3.0)
    except Exception:
        pass

    # STEP 2: Fill canonical system fields
    sys_name = page.locator("input#_systemfield_name, input[name='_systemfield_name']").first
    if sys_name.count() > 0:
        safe_fill_input(sys_name, CANDIDATE["full_name"])
        human_delay(0.3, 0.6)

    sys_email = page.locator("input#_systemfield_email, input[name='_systemfield_email'], input[type='email']").first
    if sys_email.count() > 0:
        safe_fill_input(sys_email, CANDIDATE["email"])
        try:
            sys_email.press("Tab")
        except Exception:
            pass
        human_delay(0.3, 0.6)

    # STEP 3: Handle Ashby Comboboxes (`input[placeholder="Start typing..."]` / `[role="combobox"]`)
    comboboxes = page.locator("input[placeholder*='Start typing'], input[role='combobox']")
    for i in range(comboboxes.count()):
        cb = comboboxes.nth(i)
        try:
            if not cb.is_visible():
                continue
            label = cb.evaluate(
                """el => {
                    const c = el.closest('[class*="fieldEntry"], [class*="formField"], fieldset, div');
                    const l = c ? c.querySelector('label') : null;
                    return l ? l.innerText : (el.getAttribute('aria-label') || '');
                }"""
            ) or ""
            cb.scroll_into_view_if_needed(timeout=2000)
            cb.click(timeout=2000)
            time.sleep(0.3)
            search_terms = ["India", "Bengaluru", "Remote", "United States"]
            if "school" in label.lower() or "university" in label.lower():
                search_terms = ["Indian Institute of Technology", "IIT", "Other"]
            selected = False
            for term in search_terms:
                cb.fill("")
                cb.type(term, delay=60)
                time.sleep(0.85)
                opts = page.locator("[role='listbox'] [role='option'], [class*='option']")
                if opts.count() > 0 and opts.first.is_visible():
                    opts.first.click(force=True)
                    selected = True
                    break
            if not selected:
                cb.press("ArrowDown")
                cb.press("Enter")
            human_delay(0.3, 0.6)
        except Exception:
            pass

    # STEP 4: Handle Ashby Yes/No Button Pairs (`<button>Yes</button>` / `<button>No</button>`)
    yn_groups = page.evaluate(
        """() => {
            const buttons = Array.from(document.querySelectorAll('button[type="button"], button:not([type="submit"])'));
            const yesButtons = buttons.filter(b => b.innerText.trim().toLowerCase() === 'yes');
            const results = [];
            yesButtons.forEach((yb, idx) => {
                const parent = yb.parentElement;
                if (!parent) return;
                const sibs = Array.from(parent.querySelectorAll('button'));
                const nb = sibs.find(b => b.innerText.trim().toLowerCase() === 'no');
                if (nb) {
                    const container = parent.closest('[class*="fieldEntry"], [class*="question"], fieldset') || parent.parentElement;
                    const labelEl = container ? container.querySelector('label, h3, h4, p') : null;
                    const label = labelEl ? labelEl.innerText : (container ? container.innerText.split('\\n')[0] : '');
                    yb.setAttribute('data-agy-yn-yes', String(idx));
                    nb.setAttribute('data-agy-yn-no', String(idx));
                    results.push({ idx, label });
                }
            });
            return results;
        }"""
    )
    for grp in yn_groups:
        idx = grp["idx"]
        lbl = grp["label"]
        choice = SemanticQuestionEngine.choose_yes_no(lbl)
        target_sel = f"button[data-agy-yn-yes='{idx}']" if choice == "Yes" else f"button[data-agy-yn-no='{idx}']"
        btn = page.locator(target_sel).first
        try:
            if btn.is_visible():
                btn.scroll_into_view_if_needed(timeout=2000)
                btn.click(timeout=2000)
                human_delay(0.25, 0.5)
        except Exception:
            pass

    # STEP 5 & 6: Handle Radio Groups & Checkboxes
    fill_grouped_radios_and_checkboxes(page)

    # STEP 7: Fill all remaining visible text, tel, number, date, url inputs & textareas
    inputs_meta = page.evaluate(
        """() => {
            const els = Array.from(document.querySelectorAll('input:not([type="hidden"]):not([type="file"]):not([type="radio"]):not([type="checkbox"]):not([type="submit"]):not([type="button"]), textarea, select'));
            return els.map((el, idx) => {
                el.setAttribute('data-agy-inp-idx', String(idx));
                const rect = el.getBoundingClientRect();
                const visible = rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden';
                const container = el.closest('[class*="fieldEntry"], [class*="formField"], fieldset') || el.parentElement?.parentElement;
                let label = '';
                if (el.id) {
                    const l = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
                    if (l) label = l.innerText;
                }
                if (!label && container) {
                    const l = container.querySelector('label, legend');
                    if (l) label = l.innerText;
                }
                const isCombobox = el.getAttribute('role') === 'combobox' || (el.placeholder && el.placeholder.includes('Start typing'));
                return {
                    idx,
                    tag: el.tagName.toLowerCase(),
                    type: (el.type || 'text').toLowerCase(),
                    name: el.name || '',
                    id: el.id || '',
                    placeholder: el.placeholder || '',
                    label: (label || '').trim(),
                    value: el.value || '',
                    required: el.required || el.getAttribute('aria-required') === 'true' || (label && label.includes('*')),
                    visible,
                    isCombobox
                };
            });
        }"""
    )

    for meta in inputs_meta:
        if not meta["visible"] or meta["isCombobox"]:
            continue
        if meta["value"].strip():
            continue
        loc = page.locator(f"[data-agy-inp-idx='{meta['idx']}']").first
        if meta["tag"] == "select":
            try:
                opts = loc.locator("option").all_inner_texts()
                best = SemanticQuestionEngine.pick_best_option(meta["label"], opts)
                if best:
                    loc.select_option(label=best)
            except Exception:
                pass
            continue

        ans = SemanticQuestionEngine.answer_text(
            meta["label"], meta["placeholder"], meta["name"], meta["type"]
        )
        safe_fill_input(loc, ans, is_long_prose=(meta["tag"] == "textarea"))
        human_delay(0.25, 0.5)

    if sys_email.count() > 0:
        safe_fill_input(sys_email, CANDIDATE["email"])

    return audit_form_completeness(page, "ashby")


# ============================================================================
# PLATFORM 2: GREENHOUSE ENGINE (`job-boards.greenhouse.io` & `boards.greenhouse.io`)
# ============================================================================

def fill_greenhouse_application(page: Page, url: str) -> dict[str, Any]:
    page.goto(url, wait_until="domcontentloaded", timeout=35000)
    time.sleep(2.2)

    cur_url = page.url
    body_txt = page.locator("body").inner_text(timeout=5000)
    if "error=true" in cur_url or "no longer open" in body_txt.lower() or "page not found" in body_txt.lower():
        return {"status": "SKIPPED_DEAD", "reason": "Greenhouse job closed or redirected"}

    target: Page | Frame = page
    for fr in page.frames:
        if "greenhouse.io" in fr.url and fr != page.main_frame:
            target = fr
            break

    human_scroll_4x(page)

    # Check if `#first_name` exists; if not visible, click the "Apply" tab/button to reveal or scroll to the form
    first_name_loc = target.locator("#first_name, input[name='job_application[first_name]']").first
    if first_name_loc.count() == 0 or not first_name_loc.is_visible():
        apply_btn = target.locator("button:has-text('Apply'), a:has-text('Apply')").first
        if apply_btn.count() > 0 and apply_btn.is_visible():
            try:
                apply_btn.click(timeout=3000)
                time.sleep(2.0)
            except Exception:
                pass

    if target.locator("#first_name, input[name='job_application[first_name]'], input#email").count() == 0:
        return {"status": "SKIPPED_DEAD", "reason": "No Greenhouse form present"}

    # STEP 1 (Plan 3): Upload Resume FIRST (and any required Cover Letter file input)
    try:
        res_file = target.locator("input#resume, input[type='file']").first
        if res_file.count() > 0:
            res_file.set_input_files(str(RESUME_DEFAULT))
            time.sleep(1.8)
        cl_file = target.locator("input#cover_letter")
        if cl_file.count() > 0:
            cl_file.first.set_input_files(str(RESUME_DEFAULT))
            time.sleep(1.0)
    except Exception:
        pass

    # STEP 2: Select Phone Country (`#country`) BEFORE filling `#phone`
    country_rs = target.locator("input#country[role='combobox']")
    if country_rs.count() > 0 and country_rs.first.is_visible():
        select_greenhouse_react_select(target, country_rs.first, "Country", preferred_query="India")
        human_delay(0.3, 0.55)

    # STEP 3: Fill Standard Identity Fields
    std_map = [
        ("#first_name, input[name='job_application[first_name]']", CANDIDATE["first_name"]),
        ("#last_name, input[name='job_application[last_name]']", CANDIDATE["last_name"]),
        ("#preferred_name, input[name='job_application[preferred_name]']", CANDIDATE["preferred_name"]),
        ("#email, input[name='job_application[email]']", CANDIDATE["email"]),
        ("#phone, input[name='job_application[phone]']", CANDIDATE["phone_national"]),
    ]
    for sel, val in std_map:
        loc = target.locator(sel).first
        if loc.count() > 0 and loc.is_visible():
            safe_fill_input(loc, val)
            human_delay(0.3, 0.55)

    # STEP 4: Handle ALL React-Select v5 Comboboxes (`input.select__input`, `.select__control input[role='combobox']`)
    for _pass in range(2):
        rs_inputs = target.locator("input.select__input, .select__control input[role='combobox']")
        rs_count = rs_inputs.count()
        for i in range(rs_count):
            inp = rs_inputs.nth(i)
            try:
                if not inp.is_visible():
                    continue
                state = inp.evaluate(
                    """el => {
                        const ctrl = el.closest('.select__control');
                        const container = el.closest('.select__container, .field, [class*="select-shell"]') || (ctrl ? ctrl.parentElement : el.parentElement);
                        const hasSingle = ctrl ? !!ctrl.querySelector('.select__single-value, [class*="singleValue"]') : false;
                        const hasMulti = ctrl ? !!ctrl.querySelector('.select__multi-value, [class*="multiValue"]') : false;
                        let label = '';
                        const lblId = el.getAttribute('aria-labelledby');
                        if (lblId) {
                            lblId.split(/\\s+/).forEach(id => {
                                const l = document.getElementById(id);
                                if (l) label += ' ' + l.innerText;
                            });
                        }
                        if (!label && el.id) {
                            const l = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
                            if (l) label = l.innerText;
                        }
                        if (!label && container) {
                            const l = container.querySelector('label, .label');
                            if (l) label = l.innerText;
                        }
                        return {
                            hasValue: hasSingle || hasMulti,
                            label: (label || el.getAttribute('aria-label') || '').trim(),
                            id: el.id || ''
                        };
                    }"""
                )
                if state["hasValue"]:
                    continue
                select_greenhouse_react_select(target, inp, state["label"], inp_id=state["id"])
                human_delay(0.3, 0.55)
            except Exception:
                pass

    # STEP 5: Handle Classic Greenhouse `<select>` & Select2 dropdowns
    selects = target.locator("select")
    for i in range(selects.count()):
        s = selects.nth(i)
        try:
            meta = s.evaluate(
                """el => {
                    const container = el.closest('.field, div') || el.parentElement;
                    const l = container ? container.querySelector('label') : null;
                    const opts = Array.from(el.options).map(o => ({ text: o.text.trim(), val: o.value }));
                    return {
                        label: l ? l.innerText.trim() : (el.name || el.id || ''),
                        value: el.value,
                        opts
                    };
                }"""
            )
            if meta["value"] and meta["value"] not in ("", "null"):
                continue
            opt_texts = [o["text"] for o in meta["opts"] if o["val"] != ""]
            best_txt = SemanticQuestionEngine.pick_best_option(meta["label"], opt_texts)
            if not best_txt and opt_texts:
                best_txt = opt_texts[0]
            if best_txt:
                s.evaluate(
                    """(el, targetTxt) => {
                        const opt = Array.from(el.options).find(o => o.text.trim() === targetTxt) || el.options[1];
                        if (opt) {
                            el.value = opt.value;
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                            if (window.jQuery) {
                                try { window.jQuery(el).val(opt.value).trigger('change'); } catch(e) {}
                            }
                        }
                    }""",
                    best_txt,
                )
        except Exception:
            pass

    # STEP 6: Handle Group-Scoped Checkboxes & Radios
    fill_grouped_radios_and_checkboxes(target)

    # STEP 7: Fill all remaining visible text inputs, number inputs, and textareas
    rem_inputs = target.evaluate(
        """() => {
            const els = Array.from(document.querySelectorAll('input:not([type="hidden"]):not([type="file"]):not([type="radio"]):not([type="checkbox"]):not([type="submit"]):not([type="button"]), textarea'));
            return els.map((el, idx) => {
                el.setAttribute('data-agy-gh-idx', String(idx));
                const rect = el.getBoundingClientRect();
                const visible = rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden';
                const isRS = el.classList.contains('select__input') || el.getAttribute('role') === 'combobox' || el.classList.contains('select2-input') || el.classList.contains('select2-offscreen') || el.className.includes('requiredInput');
                const container = el.closest('.field, .text-input-wrapper, div') || el.parentElement;
                let label = '';
                if (el.id) {
                    const l = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
                    if (l) label = l.innerText;
                }
                if (!label && container) {
                    const l = container.querySelector('label');
                    if (l) label = l.innerText;
                }
                return {
                    idx,
                    tag: el.tagName.toLowerCase(),
                    type: (el.type || 'text').toLowerCase(),
                    name: el.name || '',
                    id: el.id || '',
                    placeholder: el.placeholder || '',
                    label: (label || '').trim(),
                    value: el.value || '',
                    visible,
                    isRS
                };
            });
        }"""
    )
    for meta in rem_inputs:
        if not meta["visible"] or meta["isRS"] or meta["value"].strip():
            continue
        if meta["id"] == "cover_letter_text" and "*" not in meta["label"]:
            continue
        loc = target.locator(f"[data-agy-gh-idx='{meta['idx']}']").first
        ans = SemanticQuestionEngine.answer_text(
            meta["label"], meta["placeholder"], meta["name"], meta["type"]
        )
        safe_fill_input(loc, ans, is_long_prose=(meta["tag"] == "textarea"))
        human_delay(0.25, 0.5)

    phone_loc = target.locator("#phone, input[name='job_application[phone]']").first
    if phone_loc.count() > 0 and phone_loc.is_visible():
        cur_p = phone_loc.input_value()
        if not cur_p or len(re.sub(r"\D", "", cur_p)) < 10:
            safe_fill_input(phone_loc, CANDIDATE["phone_national"])

    # STEP 8: Self-Healing Validation Pass on any remaining `:invalid` React-Select or Input
    heal_greenhouse_invalids(target)

    return audit_form_completeness(target, "greenhouse")


def select_greenhouse_react_select(target: Page | Frame, inp_locator: Locator, label: str, inp_id: str = "", preferred_query: str = ""):
    """Strictly scopes to `.select__option` (ignoring hidden `li.iti__country` nodes!) and selects the best option."""
    try:
        inp_locator.scroll_into_view_if_needed(timeout=2000)
        ctrl = inp_locator.locator("xpath=ancestor::div[contains(@class, 'select__control')][1]")
        if ctrl.count() > 0:
            ctrl.first.click(timeout=2000)
        else:
            inp_locator.click(force=True, timeout=2000)
        time.sleep(0.4)

        ctx = f"{label} {inp_id}".lower()
        # CRITICAL FIX: Only match `.select__option` or `[id^='react-select-'][id*='-option-']`, NEVER generic `[role='option']` (which matches 244 hidden `li.iti__country` elements!)
        option_sel = ".select__option, [id^='react-select-'][id*='-option-']"
        opts = target.locator(option_sel)

        if opts.count() == 0:
            if preferred_query:
                search_tokens = [preferred_query]
            elif "school" in ctx or "university" in ctx or "college" in ctx:
                search_tokens = ["Indian Institute of Technology", "IIT", "University", "Other"]
            elif "degree" in ctx:
                search_tokens = ["Bachelor", "B.Tech", "Master", "Other"]
            elif "discipline" in ctx or "major" in ctx:
                search_tokens = ["Computer Science", "Engineering", "Other"]
            elif "location" in ctx or "city" in ctx or "country" in ctx:
                search_tokens = ["Bengaluru", "India", "Remote", "United States", "New York"]
            else:
                search_tokens = ["Yes", "India", "a"]

            for tok in search_tokens:
                inp_locator.fill("")
                inp_locator.type(tok, delay=50)
                time.sleep(0.8)
                opts = target.locator(option_sel)
                if opts.count() > 0:
                    txt0 = opts.first.inner_text().strip().lower()
                    if "no options" not in txt0 and "loading" not in txt0:
                        break

        opts = target.locator(option_sel)
        count = opts.count()
        if count > 0:
            opt_texts = []
            for idx in range(min(count, 40)):
                try:
                    t = opts.nth(idx).inner_text().strip()
                    if t and "no options" not in t.lower():
                        opt_texts.append((idx, t))
                except Exception:
                    pass
            if opt_texts:
                best_str = SemanticQuestionEngine.pick_best_option(label, [t for _, t in opt_texts])
                chosen_idx = opt_texts[0][0]
                if best_str:
                    for idx, t in opt_texts:
                        if t == best_str:
                            chosen_idx = idx
                            break
                opts.nth(chosen_idx).click(force=True, timeout=2000)
                time.sleep(0.25)
                return True

        inp_locator.press("ArrowDown")
        inp_locator.press("Enter")
        return True
    except Exception:
        return False


def heal_greenhouse_invalids(target: Page | Frame):
    invalids = target.evaluate(
        """() => {
            const inv = Array.from(document.querySelectorAll(':invalid')).filter(el => el.tagName !== 'FORM' && el.tagName !== 'FIELDSET');
            return inv.map((el, i) => {
                el.setAttribute('data-agy-inv-idx', String(i));
                const container = el.closest('.select__container, .field, div')?.parentElement || el.parentElement;
                const rsInput = container ? container.querySelector('input.select__input, input[role="combobox"]') : null;
                if (rsInput) rsInput.setAttribute('data-agy-inv-rs', String(i));
                const l = container ? container.querySelector('label') : null;
                return {
                    i,
                    tag: el.tagName.toLowerCase(),
                    type: el.type || '',
                    id: el.id || '',
                    name: el.name || '',
                    isRequiredInput: el.className.includes('requiredInput') || !!rsInput,
                    label: l ? l.innerText.trim() : ''
                };
            });
        }"""
    )
    for item in invalids:
        i = item["i"]
        if item["isRequiredInput"]:
            rs_loc = target.locator(f"input[data-agy-inv-rs='{i}']").first
            if rs_loc.count() > 0:
                select_greenhouse_react_select(target, rs_loc, item["label"], item["id"])
        elif item["type"] == "checkbox":
            cb = target.locator(f"[data-agy-inv-idx='{i}']").first
            try:
                cb.check(force=True, timeout=1500)
            except Exception:
                pass
        elif item["type"] == "file":
            f_loc = target.locator(f"[data-agy-inv-idx='{i}']").first
            try:
                f_loc.set_input_files(str(RESUME_DEFAULT))
                time.sleep(1.5)
            except Exception:
                pass
        else:
            loc = target.locator(f"[data-agy-inv-idx='{i}']").first
            ans = SemanticQuestionEngine.answer_text(item["label"], "", item["name"], item["type"])
            safe_fill_input(loc, ans, is_long_prose=(item["tag"] == "textarea"))


# ============================================================================
# PLATFORM 3: LEVER ENGINE (`jobs.lever.co/<org>/<uuid>/apply`)
# ============================================================================

def fill_lever_application(page: Page, url: str) -> dict[str, Any]:
    apply_url = url.rstrip("/")
    if not apply_url.endswith("/apply"):
        apply_url = apply_url + "/apply"

    page.goto(apply_url, wait_until="domcontentloaded", timeout=35000)
    time.sleep(2.2)

    body_txt = page.locator("body").inner_text(timeout=5000)
    if "This job does not exist" in body_txt or "job posting you're looking for might have closed" in body_txt:
        return {"status": "SKIPPED_DEAD", "reason": "Lever job closed"}

    if page.locator("#application-form, form").count() == 0:
        return {"status": "SKIPPED_DEAD", "reason": "No Lever form on page"}

    human_scroll_4x(page)

    # STEP 1 (Plan 3): Upload Resume FIRST and wait for `/parseResume` XHR to finish!
    try:
        res_inp = page.locator("input#resume-upload-input, input[name='resume'], input[type='file']").first
        if res_inp.count() > 0:
            res_inp.set_input_files(str(RESUME_DEFAULT))
            for _ in range(9):
                time.sleep(0.5)
                succ = page.locator(".resume-upload-success").is_visible()
                working = page.locator(".resume-upload-working").is_visible()
                if succ and not working:
                    break
            time.sleep(0.6)
    except Exception:
        pass

    # STEP 2: Fill Canonical Personal & Link Fields
    lever_std = [
        ("input[name='name']", CANDIDATE["full_name"]),
        ("input[name='email']", CANDIDATE["email"]),
        ("input[name='phone']", CANDIDATE["phone_intl"]),
        ("input[name='org']", CANDIDATE["current_company"]),
        ("input[name='urls[LinkedIn]'], input[name*='LinkedIn' i]", CANDIDATE["linkedin"]),
        ("input[name='urls[GitHub]'], input[name*='GitHub' i], input[name='urls[Github]']", CANDIDATE["github"]),
        ("input[name='urls[Portfolio]'], input[name*='Portfolio' i], input[name='urls[Website]']", CANDIDATE["portfolio"]),
        ("input[name='urls[Other]']", CANDIDATE["portfolio"]),
    ]
    for sel, val in lever_std:
        loc = page.locator(sel).first
        if loc.count() > 0 and loc.is_visible():
            safe_fill_input(loc, val)
            human_delay(0.3, 0.55)

    # STEP 3: Handle Lever Location (`input[name='location']`) with Autocomplete Dropdown Support & CustomValidity Reset
    loc_inp = page.locator("input[name='location'], input#location-input").first
    if loc_inp.count() > 0 and loc_inp.is_visible():
        fill_lever_location(page, loc_inp)
        human_delay(0.3, 0.55)

    # STEP 4: Handle Custom Screening Question Cards (`cards[...][fieldN]`), EEO Selects, Radios, and Checkboxes
    for _pass in range(2):
        selects = page.locator("select")
        for i in range(selects.count()):
            s = selects.nth(i)
            try:
                if not s.is_visible():
                    continue
                cur_val = s.input_value()
                if cur_val and cur_val.strip():
                    continue
                lbl = s.evaluate(
                    """el => {
                        const c = el.closest('li.application-question, .application-question, .eeo-question, label, div');
                        const t = c ? c.querySelector('.text, label') : null;
                        return t ? t.innerText.trim() : (c ? c.innerText.split('\\n')[0] : el.name);
                    }"""
                )
                opts = s.locator("option").all_inner_texts()
                best = SemanticQuestionEngine.pick_best_option(lbl, opts)
                if best:
                    s.select_option(label=best)
                elif len(opts) > 1:
                    s.select_option(index=1)
                human_delay(0.2, 0.45)
            except Exception:
                pass

        fill_grouped_radios_and_checkboxes(page)

        rem_lever = page.evaluate(
            """() => {
                const els = Array.from(document.querySelectorAll('input:not([type="hidden"]):not([type="file"]):not([type="radio"]):not([type="checkbox"]):not([type="submit"]):not([type="button"]), textarea'));
                return els.map((el, idx) => {
                    el.setAttribute('data-agy-lv-idx', String(idx));
                    const rect = el.getBoundingClientRect();
                    const visible = rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden';
                    const isTrap = el.name === 'trap' || el.getAttribute('hp') === 'true' || el.classList.contains('lever-trap') || !!el.closest('.lever-trap');
                    const card = el.closest('li.application-question, .application-question, label, div');
                    const txtEl = card ? card.querySelector('.text, .application-label, label') : null;
                    const label = txtEl ? txtEl.innerText.trim() : (card ? card.innerText.split('\\n')[0] : el.name);
                    return {
                        idx,
                        tag: el.tagName.toLowerCase(),
                        type: (el.type || 'text').toLowerCase(),
                        name: el.name || '',
                        placeholder: el.placeholder || '',
                        label: (label || '').trim(),
                        value: el.value || '',
                        visible,
                        isTrap
                    };
                });
            }"""
        )
        for meta in rem_lever:
            if not meta["visible"] or meta["isTrap"] or meta["value"].strip():
                continue
            loc = page.locator(f"[data-agy-lv-idx='{meta['idx']}']").first
            ans = SemanticQuestionEngine.answer_text(
                meta["label"], meta["placeholder"], meta["name"], meta["type"]
            )
            safe_fill_input(loc, ans, is_long_prose=(meta["tag"] == "textarea"))
            human_delay(0.25, 0.5)

        extra_files = page.locator("input[type='file']:not(#resume-upload-input):not([name='resume'])")
        for fi in range(extra_files.count()):
            ef = extra_files.nth(fi)
            try:
                is_req = ef.evaluate(
                    "el => el.required || !!(el.closest('.application-question') && el.closest('.application-question').querySelector('.required'))"
                )
                if is_req:
                    ef.set_input_files(str(RESUME_DEFAULT))
                    time.sleep(1.5)
            except Exception:
                pass

    # STEP 5: Final Guard on `input[name="location"]` (re-check if wiped or invalid)
    if loc_inp.count() > 0 and loc_inp.is_visible():
        is_val = loc_inp.evaluate("el => el.checkValidity() && el.value.trim().length > 0")
        if not is_val:
            fill_lever_location(page, loc_inp)

    return audit_form_completeness(page, "lever")


def fill_lever_location(page: Page, loc_inp: Locator):
    try:
        loc_inp.scroll_into_view_if_needed(timeout=2000)
        loc_inp.click(timeout=2000)
        loc_inp.fill("")
        loc_inp.type("Bengaluru, India", delay=55)
        time.sleep(1.0)
        dd_opt = page.locator(".dropdown-container .uru-result, .dropdown-container div[id*='location'], .location-results div").first
        if dd_opt.count() > 0 and dd_opt.is_visible():
            dd_opt.click(force=True, timeout=1500)
        else:
            safe_fill_input(loc_inp, CANDIDATE["location_full"])
            # Also populate hidden `#selected-location` and clear custom validity if Lever's location script flagged it
            page.evaluate(
                """() => {
                    const inp = document.querySelector('input[name="location"], input#location-input');
                    if (inp) {
                        if (!inp.value.trim()) inp.value = 'Bengaluru, Karnataka, India';
                        if (inp.setCustomValidity) inp.setCustomValidity('');
                    }
                    const sel = document.querySelector('input#selected-location, input[name="selectedLocation"]');
                    if (sel && (!sel.value || sel.value === '{"name":""}')) {
                        sel.value = JSON.stringify({ name: 'Bengaluru, Karnataka, India', country: 'IN' });
                    }
                }"""
            )
    except Exception:
        pass


# ============================================================================
# PLATFORM 4: SMARTRECRUITERS ENGINE (`jobs.smartrecruiters.com` & `/oneclick-ui/`)
# ============================================================================

def fill_smartrecruiters_application(page: Page, url: str) -> dict[str, Any]:
    page.goto(url, wait_until="domcontentloaded", timeout=35000)
    time.sleep(2.2)

    body_txt = page.locator("body").inner_text(timeout=5000)
    if "no longer available" in body_txt.lower() or "job is not available" in body_txt.lower():
        return {"status": "SKIPPED_DEAD", "reason": "SmartRecruiters job closed"}

    # STEP 1: Click "I'm interested" CTA to enter `/oneclick-ui/`
    if "/oneclick-ui/" not in page.url:
        cta = page.locator("a#st-apply, a:has-text(\"I'm interested\"), button:has-text(\"I'm interested\")").first
        if cta.count() > 0 and cta.is_visible():
            cta.click()
            try:
                page.wait_for_url("**/oneclick-ui/**", timeout=15000)
            except Exception:
                pass
            time.sleep(3.5)

    # Wait up to 6s for Step 1 components (`spl-input`, `input#first-name-input`, or `spl-dropzone`) to mount
    for _ in range(12):
        if page.locator("input#first-name-input, spl-input, spl-dropzone").count() > 0:
            break
        time.sleep(0.5)

    if page.locator("input#first-name-input, spl-input, spl-dropzone").count() == 0:
        return {"status": "SKIPPED_DEAD", "reason": "SmartRecruiters form did not mount"}

    human_scroll_4x(page)

    # STEP 2: Fill SmartRecruiters Step 1
    fill_smartrecruiters_step(page, step_num=1)

    # STEP 3: If there is a "Next" button (`oc-button[data-test='footer-next']`), advance to Step 2 (`/screening`)!
    next_btn = page.locator("oc-button[data-test='footer-next'], spl-button[data-test='footer-next'], button[data-test='footer-next'], spl-button:has-text('Next')").first
    if next_btn.count() > 0 and next_btn.is_visible():
        heal_smartrecruiters_step(page)
        try:
            next_btn.scroll_into_view_if_needed(timeout=2000)
            next_btn.click(timeout=3000)
            time.sleep(3.5)
        except Exception:
            pass

        # Fill Step 2 (Preliminary questions + Privacy Consent box)
        human_scroll_4x(page)
        fill_smartrecruiters_step(page, step_num=2)
        heal_smartrecruiters_step(page)

    return audit_form_completeness(page, "smartrecruiters")


def fill_smartrecruiters_step(page: Page, step_num: int):
    # 1. Upload Resume ONLY to `spl-dropzone[data-test='resume-upload'] input[type='file']` or `#spl-dropzone-file-input-1`
    res_dropzone = page.locator("spl-dropzone[data-test='resume-upload'] input[type='file'], input#spl-dropzone-file-input-1").first
    if res_dropzone.count() > 0:
        try:
            res_dropzone.set_input_files(str(RESUME_DEFAULT))
            time.sleep(2.2)
        except Exception:
            pass

    # 2. Fill Step 1 Canonical Personal Inputs directly
    sr_std = [
        ("input#first-name-input", CANDIDATE["first_name"]),
        ("input#last-name-input", CANDIDATE["last_name"]),
        ("input#email-input", CANDIDATE["email"]),
        ("input#confirm-email-input", CANDIDATE["email"]),
        ("spl-phone-field input[type='tel']", CANDIDATE["phone_national"]),
        ("input#linkedin-input", CANDIDATE["linkedin"]),
        ("input#website-input", CANDIDATE["portfolio"]),
        ("textarea#hiring-manager-message-input", CANDIDATE["pitch"]),
    ]
    for sel, val in sr_std:
        loc = page.locator(sel).first
        if loc.count() > 0 and loc.is_visible():
            safe_fill_input(loc, val, is_long_prose=("textarea" in sel))
            human_delay(0.25, 0.5)

    # 3. Fill Location Autocomplete (`spl-autocomplete[data-test='location-autocomplete'] input[role='combobox']`)
    loc_cb = page.locator("spl-autocomplete input[role='combobox']").first
    if loc_cb.count() > 0 and loc_cb.is_visible():
        try:
            if not loc_cb.input_value().strip():
                loc_cb.scroll_into_view_if_needed(timeout=2000)
                loc_cb.click(timeout=2000)
                loc_cb.fill("")
                loc_cb.type("Bengaluru", delay=65)
                time.sleep(1.1)
                loc_cb.press("ArrowDown")
                time.sleep(0.2)
                loc_cb.press("Enter")
                time.sleep(0.4)
        except Exception:
            pass

    # 4. Handle any other `spl-select` / `spl-autocomplete` / `[role='combobox']` (excluding phone country search input!)
    other_cbs = page.locator("spl-select button[role='combobox'], spl-autocomplete input[role='combobox'], oc-select [role='combobox']")
    for i in range(other_cbs.count()):
        cb = other_cbs.nth(i)
        try:
            if not cb.is_visible():
                continue
            aria_lbl = (cb.get_attribute("aria-label") or "").lower()
            if "country code" in aria_lbl or "search by country" in aria_lbl:
                continue
            tag = cb.evaluate("el => el.tagName.toLowerCase()")
            if tag == "input" and cb.input_value().strip():
                continue
            cb.scroll_into_view_if_needed(timeout=1500)
            cb.click(timeout=1500)
            time.sleep(0.4)
            cb.press("Enter")
            human_delay(0.25, 0.5)
        except Exception:
            pass

    # 5. Handle `spl-checkbox` (Privacy Notice Consent Box) & `spl-radio-group`
    spl_cbs = page.locator("spl-checkbox, [data-test='consent-box']")
    for i in range(spl_cbs.count()):
        scb = spl_cbs.nth(i)
        try:
            if not scb.is_visible():
                continue
            inner_cb = scb.locator("input[type='checkbox'], [role='checkbox']").first
            if inner_cb.count() > 0:
                checked = inner_cb.get_attribute("aria-checked") == "true" or inner_cb.is_checked()
                if not checked:
                    inner_cb.click(force=True, timeout=1500)
            else:
                scb.click(timeout=1500)
            human_delay(0.25, 0.5)
        except Exception:
            pass

    fill_grouped_radios_and_checkboxes(page)

    # 6. Fill any remaining custom screening `spl-input`, `spl-textarea`, or native inputs/textareas/selects
    rem_inputs = page.locator("spl-input input, spl-textarea textarea, input:not([type='hidden']):not([type='file']):not([type='radio']):not([type='checkbox']), textarea")
    for i in range(rem_inputs.count()):
        inp = rem_inputs.nth(i)
        try:
            if not inp.is_visible():
                continue
            role = inp.get_attribute("role") or ""
            if role == "combobox":
                continue
            cur = inp.input_value()
            if cur and cur.strip():
                continue
            meta = inp.evaluate(
                """el => {
                    const host = el.getRootNode()?.host;
                    const label = (host && host.getAttribute('label')) || el.getAttribute('aria-label') || el.placeholder || el.id || '';
                    return {
                        tag: el.tagName.toLowerCase(),
                        type: (el.type || 'text').toLowerCase(),
                        name: el.name || '',
                        placeholder: el.placeholder || '',
                        label: label.trim()
                    };
                }"""
            )
            # Skip optional Facebook/Twitter links if unmarked
            if any(s in meta["label"].lower() for s in ["facebook", "twitter"]):
                continue
            ans = SemanticQuestionEngine.answer_text(meta["label"], meta["placeholder"], meta["name"], meta["type"])
            safe_fill_input(inp, ans, is_long_prose=(meta["tag"] == "textarea"))
            human_delay(0.25, 0.5)
        except Exception:
            pass


def heal_smartrecruiters_step(page: Page):
    """Repairs any invalid SmartRecruiters fields before advancing/completing."""
    invalids = page.locator("spl-input[invalid], spl-autocomplete[invalid], spl-checkbox[invalid], :invalid")
    for i in range(invalids.count()):
        inv = invalids.nth(i)
        try:
            if not inv.is_visible():
                continue
            tag = inv.evaluate("el => el.tagName.toLowerCase()")
            if "autocomplete" in tag:
                cb = inv.locator("input[role='combobox']").first
                cb.click(timeout=1500)
                cb.fill("")
                cb.type("Bengaluru", delay=60)
                time.sleep(0.9)
                cb.press("ArrowDown")
                cb.press("Enter")
            elif "checkbox" in tag:
                inv.click(timeout=1500)
        except Exception:
            pass


# ============================================================================
# PLAN 6: SHARED GROUP-SCOPED RADIO & CHECKBOX RESOLVER
# ============================================================================

def fill_grouped_radios_and_checkboxes(target: Page | Frame):
    radio_groups = target.evaluate(
        """() => {
            const radios = Array.from(document.querySelectorAll('input[type="radio"]'));
            const byGroup = {};
            radios.forEach((r, idx) => {
                r.setAttribute('data-agy-r-idx', String(idx));
                const rect = r.getBoundingClientRect();
                const parentRect = r.parentElement ? r.parentElement.getBoundingClientRect() : rect;
                if (rect.width === 0 && parentRect.width === 0) return;
                const container = r.closest('li.application-question, .application-question, fieldset, .field, [role="radiogroup"], [class*="fieldEntry"]') || r.parentElement?.parentElement;
                const key = r.name || (container ? container.innerText.slice(0, 50) : ('r_' + idx));
                if (!byGroup[key]) {
                    const l = container ? container.querySelector('.text, legend, label') : null;
                    byGroup[key] = {
                        label: l ? l.innerText.trim() : (container ? container.innerText.split('\\n')[0] : ''),
                        items: []
                    };
                }
                const itemLbl = r.closest('label') ? r.closest('label').innerText : (r.parentElement ? r.parentElement.innerText : r.value);
                byGroup[key].items.push({ idx, text: (itemLbl || r.value || '').trim(), checked: r.checked });
            });
            return Object.values(byGroup);
        }"""
    )
    for grp in radio_groups:
        if any(it["checked"] for it in grp["items"]) or not grp["items"]:
            continue
        opt_texts = [it["text"] for it in grp["items"]]
        best_txt = SemanticQuestionEngine.pick_best_option(grp["label"], opt_texts)
        chosen = grp["items"][0]
        if best_txt:
            for it in grp["items"]:
                if it["text"] == best_txt:
                    chosen = it
                    break
        r_loc = target.locator(f"input[data-agy-r-idx='{chosen['idx']}']").first
        try:
            r_loc.scroll_into_view_if_needed(timeout=1500)
            lbl_loc = r_loc.locator("xpath=ancestor::label[1]")
            if lbl_loc.count() > 0 and lbl_loc.is_visible():
                lbl_loc.click(timeout=1500)
            else:
                r_loc.check(force=True, timeout=1500)
            human_delay(0.2, 0.45)
        except Exception:
            pass

    cb_groups = target.evaluate(
        """() => {
            const cbs = Array.from(document.querySelectorAll('input[type="checkbox"]'));
            const byGroup = {};
            cbs.forEach((cb, idx) => {
                cb.setAttribute('data-agy-c-idx', String(idx));
                if (cb.name === 'trap' || cb.classList.contains('lever-trap')) return;
                const rect = cb.getBoundingClientRect();
                const parentRect = cb.parentElement ? cb.parentElement.getBoundingClientRect() : rect;
                if (rect.width === 0 && parentRect.width === 0) return;
                const container = cb.closest('li.application-question, .application-question, fieldset, .field, .eeo-question, [class*="fieldEntry"]') || cb.parentElement?.parentElement;
                const key = cb.name || (container ? container.innerText.slice(0, 60) : ('c_' + idx));
                if (!byGroup[key]) {
                    const l = container ? container.querySelector('.text, legend, label') : null;
                    byGroup[key] = {
                        label: l ? l.innerText.trim() : (container ? container.innerText.split('\\n')[0] : ''),
                        items: []
                    };
                }
                const itemLbl = cb.closest('label') ? cb.closest('label').innerText : (cb.parentElement ? cb.parentElement.innerText : cb.value);
                byGroup[key].items.push({ idx, text: (itemLbl || cb.value || '').trim(), checked: cb.checked });
            });
            return Object.values(byGroup);
        }"""
    )
    for grp in cb_groups:
        if any(it["checked"] for it in grp["items"]) or not grp["items"]:
            continue
        opt_texts = [it["text"] for it in grp["items"]]
        best_txt = SemanticQuestionEngine.pick_best_option(grp["label"], opt_texts)
        chosen = grp["items"][0]
        if best_txt:
            for it in grp["items"]:
                if it["text"] == best_txt:
                    chosen = it
                    break
        c_loc = target.locator(f"input[data-agy-c-idx='{chosen['idx']}']").first
        try:
            c_loc.scroll_into_view_if_needed(timeout=1500)
            lbl_loc = c_loc.locator("xpath=ancestor::label[1]")
            if lbl_loc.count() > 0 and lbl_loc.is_visible():
                lbl_loc.click(timeout=1500)
            else:
                c_loc.check(force=True, timeout=1500)
            human_delay(0.2, 0.45)
        except Exception:
            pass


# ============================================================================
# PLAN 8: DEEP SHADOW-PIERCING PRE-SUBMIT VALIDATION AUDITOR (`ValidationHealer`)
# ============================================================================

def audit_form_completeness(target: Page | Frame, ats: str) -> dict[str, Any]:
    """Deep-traverses both Light DOM and Open Shadow DOMs to verify 100% required field coverage and zero `:invalid` controls."""
    report = target.evaluate(
        """(atsName) => {
            function collectAll(root) {
                let nodes = Array.from(root.querySelectorAll('input, textarea, select, [role="checkbox"], .select__single-value, .select__multi-value, .resume-upload-success'));
                root.querySelectorAll('*').forEach(el => {
                    if (el.shadowRoot) {
                        nodes = nodes.concat(collectAll(el.shadowRoot));
                    }
                });
                return nodes;
            }
            const allNodes = collectAll(document);

            const invalids = allNodes.filter(el => {
                if (!el.matches || !el.matches(':invalid')) return false;
                if (el.tagName === 'FORM' || el.tagName === 'FIELDSET') return false;
                if (el.name === 'trap' || el.classList.contains('lever-trap')) return false;
                const rect = el.getBoundingClientRect();
                const parentRect = el.parentElement ? el.parentElement.getBoundingClientRect() : rect;
                return rect.width > 0 || parentRect.width > 0 || (el.className && el.className.includes && el.className.includes('requiredInput'));
            }).map(el => ({
                tag: el.tagName.toLowerCase(),
                type: el.type || '',
                id: el.id || '',
                name: el.name || '',
                className: typeof el.className === 'string' ? el.className : ''
            }));

            const filledInputs = allNodes.filter(el => {
                const tag = el.tagName ? el.tagName.toLowerCase() : '';
                if (el.classList && (el.classList.contains('select__single-value') || el.classList.contains('select__multi-value') || el.classList.contains('resume-upload-success'))) {
                    return true;
                }
                if (el.getAttribute && el.getAttribute('role') === 'checkbox') {
                    return el.getAttribute('aria-checked') === 'true';
                }
                if (tag !== 'input' && tag !== 'textarea' && tag !== 'select') return false;
                if (el.type === 'hidden') return false;
                if (el.type === 'radio' || el.type === 'checkbox') return el.checked;
                if (el.type === 'file') return el.files && el.files.length > 0;
                return (el.value || '').trim().length > 0;
            }).length;

            return {
                invalid_count: invalids.length,
                invalids: invalids.slice(0, 10),
                filled_controls_count: filledInputs
            };
        }""",
        ats,
    )
    min_controls = 1 if ats == "smartrecruiters" else 3
    is_pass = report["invalid_count"] == 0 and report["filled_controls_count"] >= min_controls
    report["status"] = "PASS_FILLED_100_PCT" if is_pass else "VALIDATION_INCOMPLETE"
    return report


# ============================================================================
# PLAN 11: LIVE SUBMISSION, AUTO-OTP & SERVER CONFIRMATION VERIFIER
# ============================================================================

import threading
_LEDGER_LOCK = threading.Lock()
_OTP_LOCK = threading.Lock()


def record_confirmed_application(ats: str, url: str, verification: str):
    """Thread-safe append to `src/applied/jobs_applied.json` ONLY when server confirmation is verified."""
    ledger_path = ROOT / "src" / "applied" / "jobs_applied.json"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    parts = url.split("://")[-1].split("/")
    company = parts[1] if len(parts) > 1 else ats
    entry = {
        "company": company,
        "role": "Software / AI / ML Engineer",
        "url": url,
        "platform": ats,
        "location": "India / Global",
        "resume": "ML_Vision_RL (Resume ML_Vision_RL_PPO 7th Aug.pdf)",
        "status": "applied",
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "verification": verification,
    }
    with _LEDGER_LOCK:
        try:
            data = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else []
        except Exception:
            data = []
        if not any(d.get("url") == url and d.get("status") == "applied" for d in data):
            data.append(entry)
            ledger_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def submit_and_verify_application(page: Page, ats: str, url: str) -> dict[str, Any]:
    """Clicks final Submit with human mouse telemetry, handles Greenhouse IMAP OTP, and verifies server confirmation."""
    submit_epoch = time.time() - 5.0
    try:
        if ats == "ashby":
            btn = page.locator("button[type='submit'], button:has-text('Submit Application'), button:has-text('Submit')").first
            if btn.count() == 0 or not btn.is_visible():
                return {"submit_status": "NO_SUBMIT_BUTTON"}
            btn.scroll_into_view_if_needed(timeout=2000)
            human_delay(0.4, 0.9)
            btn.click(timeout=4000)

            for _ in range(24):
                time.sleep(0.5)
                body_l = page.locator("body").inner_text(timeout=2000).lower()
                if "successfully submitted" in body_l or "thank you for applying" in body_l or "application was submitted" in body_l:
                    ver = f"CONFIRMED: URL {page.url} + Ashby Success confirmation"
                    record_confirmed_application(ats, url, ver)
                    return {"submit_status": "CONFIRMED_APPLIED", "verification": ver}
                if "flagged as possible spam" in body_l:
                    return {"submit_status": "BLOCKED_SPAM_FLAG", "reason": "Ashby spam heuristic"}
                if "needs corrections" in body_l or "missing entry" in body_l:
                    return {"submit_status": "VALIDATION_ERROR_ON_SUBMIT", "reason": body_l[:200]}
            return {"submit_status": "SUBMIT_CLICKED_PENDING", "reason": "No confirmation banner within 12s"}

        elif ats == "greenhouse":
            target: Page | Frame = page
            for fr in page.frames:
                if "greenhouse.io" in fr.url and fr != page.main_frame:
                    target = fr
                    break
            btn = target.locator("button[type='submit'], input[type='submit'], button:has-text('Submit application')").first
            if btn.count() == 0 or not btn.is_visible():
                return {"submit_status": "NO_SUBMIT_BUTTON"}
            btn.scroll_into_view_if_needed(timeout=2000)
            human_delay(0.4, 0.9)
            btn.click(timeout=4000)

            for _ in range(18):
                time.sleep(0.6)
                cur_u = page.url.lower()
                body_l = (target.locator("body").inner_text(timeout=2000) + " " + page.locator("body").inner_text(timeout=2000)).lower()
                if "confirmation" in cur_u or "thank you for applying" in body_l or "application has been received" in body_l:
                    ver = f"CONFIRMED: URL {page.url} + Thank you for applying"
                    record_confirmed_application(ats, url, ver)
                    return {"submit_status": "CONFIRMED_APPLIED", "verification": ver}
                if "verification code" in body_l or "security code" in body_l or target.locator("input[id*='security-input']").count() > 0:
                    # Handle Greenhouse Email OTP via IMAP listener
                    with _OTP_LOCK:
                        try:
                            from src.scripts.otp_listener import fetch_latest_otp
                        except ImportError:
                            from otp_listener import fetch_latest_otp
                        otp_code = fetch_latest_otp(
                            email_address=CANDIDATE["email"],
                            max_wait_seconds=38,
                            min_date_epoch=submit_epoch,
                        )
                    if otp_code:
                        otp_boxes = target.locator("input[id*='security-input'], input[maxlength='1']:visible")
                        if otp_boxes.count() >= len(otp_code):
                            for idx_c, ch in enumerate(otp_code):
                                otp_boxes.nth(idx_c).click(force=True)
                                otp_boxes.nth(idx_c).fill(ch)
                                time.sleep(0.06)
                        else:
                            inp_otp = target.locator("input[aria-label*='code' i], input[name*='code' i], input[type='text']:visible").last
                            inp_otp.click(force=True)
                            inp_otp.fill(otp_code)
                        time.sleep(0.8)
                        sub2 = target.locator("button[type='submit']:visible, button:has-text('Submit'):visible").first
                        if sub2.count() > 0:
                            sub2.click(force=True)
                        time.sleep(5.0)
                        cur_u2 = page.url.lower()
                        body_l2 = (target.locator("body").inner_text(timeout=2000) + " " + page.locator("body").inner_text(timeout=2000)).lower()
                        if "confirmation" in cur_u2 or "thank you for applying" in body_l2 or "application has been received" in body_l2:
                            ver = f"CONFIRMED VIA AUTO-OTP ({otp_code}): URL {page.url}"
                            record_confirmed_application(ats, url, ver)
                            return {"submit_status": "CONFIRMED_APPLIED", "verification": ver}
                    return {"submit_status": "AWAITING_HUMAN_OTP", "reason": "Greenhouse Email OTP triggered"}
            return {"submit_status": "SUBMIT_CLICKED_UNCONFIRMED", "url_after": page.url}

        elif ats == "lever":
            btn = page.locator("button#btn-submit, button.postings-btn-submit, button:has-text('Submit application')").first
            if btn.count() == 0 or not btn.is_visible():
                return {"submit_status": "NO_SUBMIT_BUTTON"}
            btn.scroll_into_view_if_needed(timeout=2000)
            human_delay(0.4, 0.9)
            btn.click(timeout=4000)

            for _ in range(20):
                time.sleep(0.6)
                cur_u = page.url.lower()
                body_l = page.locator("body").inner_text(timeout=2000).lower()
                if "/applied" in cur_u or "thank you for applying" in body_l or "application has been submitted" in body_l:
                    ver = f"CONFIRMED: URL {page.url} + Lever /applied confirmation"
                    record_confirmed_application(ats, url, ver)
                    return {"submit_status": "CONFIRMED_APPLIED", "verification": ver}
                # Check if visual hCaptcha puzzle popped up
                hc_vis = page.evaluate(
                    """() => {
                        const ifr = Array.from(document.querySelectorAll('iframe[src*="hcaptcha.com"]'));
                        return ifr.some(f => {
                            const r = f.getBoundingClientRect();
                            return r.width > 250 && r.height > 250;
                        });
                    }"""
                )
                if hc_vis:
                    return {"submit_status": "AWAITING_HUMAN_CAPTCHA", "reason": "Lever interactive hCaptcha puzzle"}
            return {"submit_status": "SUBMIT_CLICKED_UNCONFIRMED", "url_after": page.url}

        elif ats == "smartrecruiters":
            btn = page.locator("spl-button[data-test='footer-submit'], oc-button[data-test='footer-submit'], button[data-test='footer-submit'], spl-button:has-text('Submit'), button:has-text('Submit')").first
            if btn.count() == 0 or not btn.is_visible():
                return {"submit_status": "NO_SUBMIT_BUTTON"}
            btn.scroll_into_view_if_needed(timeout=2000)
            human_delay(0.4, 0.9)
            btn.click(timeout=4000)

            for _ in range(24):
                time.sleep(0.6)
                cur_u = page.url.lower()
                body_l = page.locator("body").inner_text(timeout=2000).lower()
                if any(k in cur_u for k in ["/success", "/confirmation", "/thank-you", "submitted"]) or any(
                    k in body_l for k in [
                        "application has been sent",
                        "thank you for applying",
                        "successfully submitted",
                        "application is complete",
                        "we have received your application",
                        "good luck",
                        "track your application",
                    ]
                ):
                    ver = f"CONFIRMED: URL {page.url} + SmartRecruiters confirmation"
                    record_confirmed_application(ats, url, ver)
                    return {"submit_status": "CONFIRMED_APPLIED", "verification": ver}
            # Also check if Submit button disappeared (transitioned to post-apply view)
            if btn.count() == 0 or not btn.is_visible():
                ver = f"CONFIRMED: URL {page.url} + SmartRecruiters post-submit screen"
                record_confirmed_application(ats, url, ver)
                return {"submit_status": "CONFIRMED_APPLIED", "verification": ver}
            return {"submit_status": "SUBMIT_CLICKED_UNCONFIRMED", "url_after": page.url}

    except Exception as e:
        return {"submit_status": "SUBMIT_ERROR", "reason": str(e)[:150]}

    return {"submit_status": "UNKNOWN"}


# ============================================================================
# SINGLE-JOB ORCHESTRATOR & BATCH EVALUATION HARNESS
# ============================================================================

def process_single_job(ats: str, url: str, headless: bool = True, do_submit: bool = False) -> dict[str, Any]:
    start_ts = time.time()
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", url.split("://")[-1])[:75]
    snap_path = SNAP_DIR / f"{ats}_{slug}.png"

    with sync_playwright() as p:
        # Use Patchright with channel="chrome" & headless=False for SmartRecruiters to pass DataDome WAF seamlessly
        if ats == "smartrecruiters":
            browser = p.chromium.launch(
                headless=False,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--window-position=-2000,0",
                ],
            )
        else:
            browser = p.chromium.launch(
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )
        context = browser.new_context(
            viewport={"width": 1366, "height": 860},
            locale="en-US",
        )
        page = context.new_page()
        try:
            if ats == "ashby":
                res = fill_ashby_application(page, url)
            elif ats == "greenhouse":
                res = fill_greenhouse_application(page, url)
            elif ats == "lever":
                res = fill_lever_application(page, url)
            elif ats == "smartrecruiters":
                res = fill_smartrecruiters_application(page, url)
            else:
                res = {"status": "ERROR", "reason": f"Unknown ATS: {ats}"}

            if do_submit and res.get("status") == "PASS_FILLED_100_PCT":
                sub_info = submit_and_verify_application(page, ats, url)
                res.update(sub_info)

            try:
                page.screenshot(path=str(snap_path), full_page=False)
                res["screenshot"] = str(snap_path)
            except Exception:
                pass
        except Exception as e:
            res = {
                "status": "ERROR",
                "reason": str(e)[:200],
                "trace": traceback.format_exc()[-400:],
            }
        finally:
            context.close()
            browser.close()

    res["ats"] = ats
    res["url"] = url
    res["elapsed_sec"] = round(time.time() - start_ts, 2)
    return res


def run_submit_all_140(max_workers: int = 5):
    """Fills and clicks live Submit on all 140 jobs (120 test + 20 train) represented in universal_eval."""
    master_120_path = PROGRESS_DIR / "120_eval_master_results.json"
    dataset_path = ROOT / "src" / "job_search_results" / "ats_120_eval_dataset.json"

    tasks = []
    seen = set()
    if master_120_path.exists():
        m = json.loads(master_120_path.read_text(encoding="utf-8"))
        for r in m.get("passed_120", []):
            key = (r["ats"], r["url"])
            if key not in seen:
                seen.add(key)
                tasks.append(key)

    if dataset_path.exists():
        ds = json.loads(dataset_path.read_text(encoding="utf-8"))
        for ats in ["ashby", "greenhouse", "lever", "smartrecruiters"]:
            for u in ds.get("train", {}).get(ats, [])[:5]:
                key = (ats, u)
                if key not in seen:
                    seen.add(key)
                    tasks.append(key)

    print(f"=== Running LIVE SUBMIT on ALL {len(tasks)} Jobs (max_workers={max_workers}) ===")
    results = []
    workers = min(max_workers, 5)
    out_file = PROGRESS_DIR / "universal_ats_submit_all_results.json"

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        fut_map = {ex.submit(process_single_job, ats, u, True, True): (ats, u) for ats, u in tasks}
        for idx, fut in enumerate(concurrent.futures.as_completed(fut_map), 1):
            ats, u = fut_map[fut]
            res = fut.result()
            results.append(res)
            print(
                f"[{idx}/{len(tasks)}] [{ats.upper()}] fill={res.get('status')} | "
                f"submit={res.get('submit_status', 'N/A')} ({res.get('elapsed_sec')}s) -> {u}"
            )
            # Save incremental checkpoint every 5 completions
            if idx % 5 == 0 or idx == len(tasks):
                out_file.write_text(json.dumps({"completed": idx, "total": len(tasks), "results": results}, indent=2), encoding="utf-8")

    summary = {}
    for ats in ["ashby", "greenhouse", "lever", "smartrecruiters"]:
        sub = [r for r in results if r["ats"] == ats]
        summary[ats] = {
            "total": len(sub),
            "filled_100_pct": sum(1 for r in sub if r.get("status") == "PASS_FILLED_100_PCT"),
            "confirmed_applied": sum(1 for r in sub if r.get("submit_status") == "CONFIRMED_APPLIED"),
            "captcha_or_otp_gated": sum(1 for r in sub if r.get("submit_status") in ("AWAITING_HUMAN_CAPTCHA", "AWAITING_HUMAN_OTP", "BLOCKED_SPAM_FLAG")),
            "other_submit_state": sum(1 for r in sub if r.get("submit_status") not in ("CONFIRMED_APPLIED", "AWAITING_HUMAN_CAPTCHA", "AWAITING_HUMAN_OTP", "BLOCKED_SPAM_FLAG")),
        }

    out_file.write_text(
        json.dumps({"timestamp": str(datetime.datetime.now()), "summary": summary, "results": results}, indent=2),
        encoding="utf-8",
    )
    print("\n=== LIVE SUBMIT SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"Saved full live submit results to: {out_file}")


def run_suite(mode: str, ats_filter: str = "all", max_workers: int = 5, limit: int = 30):
    dataset_path = ROOT / "src" / "job_search_results" / "ats_120_eval_dataset.json"
    if not dataset_path.exists():
        print(f"Dataset not found at {dataset_path}. Run build_ats_120_dataset.py first.")
        sys.exit(1)

    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    split_key = "train" if mode == "train" else "test_30"
    platforms = ["ashby", "greenhouse", "lever", "smartrecruiters"]
    if ats_filter != "all":
        platforms = [a.strip() for a in ats_filter.split(",") if a.strip() in platforms]

    tasks = []
    for ats in platforms:
        urls = dataset.get(split_key, {}).get(ats, [])[:limit]
        for u in urls:
            tasks.append((ats, u))

    print(f"=== Running Universal ATS Filler v2.0 [{mode.upper()}] on {len(tasks)} jobs (max_workers={max_workers}) ===")
    results = []
    workers = min(max_workers, 5)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        fut_map = {ex.submit(process_single_job, ats, u): (ats, u) for ats, u in tasks}
        for idx, fut in enumerate(concurrent.futures.as_completed(fut_map), 1):
            ats, u = fut_map[fut]
            res = fut.result()
            results.append(res)
            print(
                f"[{idx}/{len(tasks)}] [{ats.upper()}] {res.get('status')} "
                f"(filled={res.get('filled_controls_count', 0)}, invalid={res.get('invalid_count', -1)}, {res.get('elapsed_sec')}s) -> {u}"
            )
            if res.get("invalid_count", 0) > 0:
                print(f"   Invalids: {res.get('invalids')}")

    out_suffix = ats_filter.replace(",", "_") if ats_filter != "all" else "all"
    out_file = PROGRESS_DIR / f"universal_ats_{mode}_{out_suffix}_results.json"

    # If in test mode any URL was SKIPPED_DEAD, pull unseen replacements from `backup` so we evaluate exactly `limit` (30) LIVE unseen applications!
    if mode == "test":
        for ats in platforms:
            backups = list(dataset.get("backup", {}).get(ats, []))
            active_evals = [r for r in results if r["ats"] == ats and r.get("status") != "SKIPPED_DEAD"]
            while len(active_evals) < limit and backups:
                needed = limit - len(active_evals)
                batch_urls = [backups.pop(0) for _ in range(min(needed, len(backups)))]
                print(f"[Backup Replacement] Running {len(batch_urls)} unseen backup {ats.upper()} URLs to reach {limit} live evaluations...")
                with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
                    futs = {ex.submit(process_single_job, ats, bu): bu for bu in batch_urls}
                    for fut in concurrent.futures.as_completed(futs):
                        bu = futs[fut]
                        res = fut.result()
                        results.append(res)
                        print(
                            f"[BACKUP] [{ats.upper()}] {res.get('status')} "
                            f"(filled={res.get('filled_controls_count', 0)}, invalid={res.get('invalid_count', -1)}, {res.get('elapsed_sec')}s) -> {bu}"
                        )
                active_evals = [r for r in results if r["ats"] == ats and r.get("status") != "SKIPPED_DEAD"]

    summary = {}
    for ats in platforms:
        sub = [r for r in results if r["ats"] == ats]
        passed = [r for r in sub if r.get("status") == "PASS_FILLED_100_PCT"]
        dead = [r for r in sub if r.get("status") == "SKIPPED_DEAD"]
        failed = [r for r in sub if r.get("status") not in ("PASS_FILLED_100_PCT", "SKIPPED_DEAD")]
        summary[ats] = {
            "total_evaluated": len(sub),
            "active_total": len(passed) + len(failed),
            "passed": len(passed),
            "dead_skipped": len(dead),
            "failed": len(failed),
        }

    out_file.write_text(
        json.dumps({"timestamp": str(datetime.datetime.now()), "mode": mode, "summary": summary, "results": results}, indent=2),
        encoding="utf-8",
    )
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"Detailed results saved to: {out_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["train", "test", "single", "submit-all"], default="train")
    parser.add_argument("--ats", default="all")
    parser.add_argument("--url", default="")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--submit", action="store_true")
    args = parser.parse_args()

    if args.mode == "submit-all":
        run_submit_all_140(max_workers=args.workers)
    elif args.mode == "single" and args.url:
        res = process_single_job(args.ats, args.url, headless=not args.headed, do_submit=args.submit)
        print(json.dumps(res, indent=2))
    else:
        run_suite(args.mode, args.ats, max_workers=args.workers, limit=args.limit)


if __name__ == "__main__":
    main()
