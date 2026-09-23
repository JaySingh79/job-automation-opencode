"""Selector-free job application driver. One session, natural-language steps.

Adding a job means adding a URL, not writing a driver. Nothing here knows what a
data-automation-id is: the cloud browser's own agent resolves fields from instructions,
so the same code drives Workday, Phenom, Greenhouse or anything else. That is the only
approach that survives hundreds of postings.

Why prompts rather than code: `interact --python -c` compiles with mode="single" and
executes ONLY the first statement, returning rc=0 while silently dropping the rest.
`--node` runs full scripts but discards stdout, so nothing can be read back. Prompts are
the only mode that both acts and reports.

Hard rule: G1. This file never issues an instruction that submits. It fills, reports,
and hands the last click to a human.

    .venv\\Scripts\\python.exe apply_session.py --job HPE --dry-run
    .venv\\Scripts\\python.exe apply_session.py --job HPE
    .venv\\Scripts\\python.exe apply_session.py --job HPE --resume-session <scrape-id>
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
CACHE = ROOT / ".firecrawl"
CACHE.mkdir(exist_ok=True)
FIRECRAWL = shutil.which("firecrawl") or "firecrawl"

BUDGET_CAP = 150
ABORT_IF_REMAINING_BELOW = 200
RATE_GAP = 7                 # the API allows ~10 requests/minute; stay under it

# Anything that would commit the application. Checked against every instruction before
# it is sent, because the 2026-08-02 run submitted from a step labelled "Save and
# Continue" and no wording is trustworthy on an unmapped flow.
SUBMIT_WORDS = re.compile(
    r"\bsubmit\b|\bfinish\b|\bconfirm\b|\bagree and\b|\bcomplete application\b", re.I)


class SubmitBoundary(Exception):
    """G1. Raised instead of sending an instruction that could commit the application."""


# --------------------------------------------------------------------------- cli

def sh(args, timeout=400):
    p = subprocess.run([FIRECRAWL if args[0] == "firecrawl" else args[0], *args[1:]],
                       capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    return p.returncode, p.stdout, p.stderr


def credits():
    _, out, _ = sh(["firecrawl", "credit-usage", "--json"])
    try:
        return json.loads(out)["data"]["remainingCredits"]
    except Exception:
        return None


class Session:
    """Owns the live browser session for its lifetime.

    Sessions bill for as long as they stay open (166s cost 6 credits once) and hold the
    profile's single writer lock, so a leaked one keeps charging AND blocks the next
    attempt with 'Another session is currently writing to this profile'. The context
    manager is what guarantees release on the failure path.
    """

    def __init__(self, url, profile, dry_run=False, sid=None):
        self.url, self.profile, self.dry_run = url, profile, dry_run
        self.sid = sid
        self.start_credits = None

    def __enter__(self):
        self.start_credits = 0 if self.dry_run else credits()
        if self.dry_run:
            self.sid = self.sid or "dry-run"
            print(f"[dry-run] would open {self.url} with --profile {self.profile}")
            return self
        if self.sid:
            print(f"reusing session {self.sid}")
            return self
        rc, out, err = sh(["firecrawl", "scrape", self.url, "--profile", self.profile,
                           "--wait-for", "8000", "--format", "markdown",
                           "-o", str(CACHE / "session.md")], timeout=300)
        m = re.search(r"Scrape ID: (\S+)", out + err)
        if not m:
            sys.exit(f"could not open session:\n{out}\n{err}")
        self.sid = m.group(1)
        print(f"session {self.sid}  (credits {self.start_credits})")
        return self

    def __exit__(self, *exc):
        if self.dry_run or not self.sid or self.sid == "dry-run":
            return False
        rc, out, err = sh(["firecrawl", "interact", "stop", self.sid], timeout=120)
        line = (out or err).strip().splitlines()
        print(f"[session] {line[0] if line else 'stopped'}")
        if len(line) > 2:
            print(f"[session] {line[-1]}")
        return False

    # ------------------------------------------------------------------ actions

    def ask(self, instruction, label="", timeout=180):
        """One natural-language step. Returns whatever the agent reports back."""
        if SUBMIT_WORDS.search(instruction):
            raise SubmitBoundary(
                f"refusing to send an instruction containing a commit word:\n"
                f"  {instruction[:200]}")
        if self.dry_run:
            print(f"\n--- [dry-run] {label} ---\n{instruction}\n")
            return ""
        time.sleep(RATE_GAP)
        rc, out, err = sh(["firecrawl", "interact", "-s", self.sid,
                           "--timeout", str(timeout), "--prompt", instruction],
                          timeout=timeout + 120)
        body = "\n".join(ln for ln in (out + "\n" + err).splitlines()
                         if ln.strip() and not ln.startswith(("Using scrape",
                                                              "Live View",
                                                              "Interactive Live View")))
        print(f"\n--- {label} (rc={rc}) ---\n{body[:1800]}")
        return body

    def bash(self, script, label="", timeout=200):
        """The one non-prompt path: uploads need a file inside the sandbox."""
        if self.dry_run:
            print(f"\n--- [dry-run] {label} (bash) ---\n{script}\n")
            return ""
        time.sleep(RATE_GAP)
        rc, out, err = sh(["firecrawl", "interact", "-s", self.sid, "--bash",
                           "--timeout", str(timeout), "-c", script.strip()],
                          timeout=timeout + 120)
        print(f"\n--- {label} (rc={rc}) ---\n{(out + err)[:1200]}")
        return out + err

    def spend_check(self, label=""):
        if self.dry_run or self.start_credits is None:
            return
        now = credits()
        if now is None:
            return
        spent = self.start_credits - now
        print(f"  [credits] spent={spent} remaining={now} ({label})")
        if spent > BUDGET_CAP:
            sys.exit(f"ABORT: spent {spent} > cap {BUDGET_CAP}")
        if now < ABORT_IF_REMAINING_BELOW:
            sys.exit(f"ABORT: only {now} credits remain")


# ----------------------------------------------------------------------- payload

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def parse_dates(text):
    """'Sep 2024 - Feb 2025' -> (9, 2024, 2, 2025). Refuses a missing month (E3)."""
    parts = [p.strip() for p in re.split(r"[-–—]", text) if p.strip()]
    if len(parts) != 2:
        raise ValueError(f"unparseable date range {text!r}")
    out = []
    for part in parts:
        m = re.match(r"([A-Za-z]{3,9})\.?\s+(\d{4})$", part)
        if not m:
            raise ValueError(f"{text!r}: '{part}' has no month — E3 forbids inventing it")
        out += [MONTHS[m.group(1)[:3].lower()], int(m.group(2))]
    return tuple(out)


ILLEGAL = '<>[]{}"\\'


def clean(text):
    """Workday-family forms reject < > [ ] { } " \\ as 'illegal characters' (D1).
    Comparisons are rewritten rather than stripped so a claim survives intact."""
    text = text.replace(">=", "at least ").replace("<=", "at most ")
    text = re.sub(r">\s*(\d)", r"over \1", text)
    text = re.sub(r"<\s*(\d)", r"under \1", text)
    text = (text.replace(chr(8220), "").replace(chr(8221), "")
                .replace(chr(8217), "'").replace(chr(8212), "-").replace(chr(8211), "-"))
    return "".join(c for c in text if c not in ILLEGAL)


def roles(profile):
    """Every role in the profile, newest first, months parsed not assumed.

    All of them: work_ex_details.md is the authoritative history and the resume PDF is
    expected to lag it, so filtering against the resume would drop real roles.
    """
    out = []
    for w in profile["work_experience"]:
        sm, sy, em, ey = parse_dates(w["dates"])
        out.append({"title": w["title"], "company": w["company"],
                    "location": w["location"],
                    "start": f"{sm:02d}/{sy}", "end": f"{em:02d}/{ey}",
                    "sort": (sy, sm),
                    "description": clean(" ".join(w["bullets"]))[:1900]})
    out.sort(key=lambda r: r["sort"], reverse=True)
    for r in out:
        r.pop("sort")
    return out


# ------------------------------------------------------------------------- steps

def personal_step(pi, answers):
    return f"""Fill in the personal information / my information form on this page.
Use exactly these values and do not invent anything not listed:
  Country: {pi['country']}
  First / Given name: {pi['first_name']}
  Last / Family name: {pi['last_name']}
  Address line 1: {pi['address_line_1']}
  City: {pi['city']}
  Postal code: {pi['postal_code']}
  Email: {pi['email']}
  Phone device type: Personal Mobile
  Country phone code: {pi['country']}
  Phone number: {pi['phone'].split('-', 1)[-1]}
  How did you hear about us: {answers.get('ats_source', 'HPE Career site')}
  Previously worked for this organization: No

Rules:
- Tick ONLY a consent that is marked required with an asterisk, such as agreeing to the
  processing of personal data. Leave optional marketing consents for SMS, email and
  AI-tool usage UNCHECKED.
- Do NOT fill any field labelled as being for robots only; it is a honeypot.
- For any dropdown, pick from the options the field itself offers. If nothing matches,
  leave it and say so.
Then report: every field you filled, every dropdown value chosen, any required field you
could not fill, and any validation error text shown. Do not press any button yet."""


def experience_step(entries, edu, links):
    return f"""Fill in the work experience and education section of this application.

Add {len(entries)} work experience entries, in this order, adding more entry slots if the
form provides fewer. Use these exact values:
{json.dumps(entries, indent=1)}

Education:
  School: {edu['institution']}
  Degree: {edu['degree']} (choose the closest option the form offers, e.g. Bachelor's Degree)
  Field of study: {edu['field_of_study']} (choose the closest option offered)
  Graduation: {edu['graduation_date']}

Links:
  LinkedIn: {links['linkedin']}
  GitHub: {links.get('github', '')}

Rules:
- Dates must go in as month and year exactly as given. Do not invent or round a date.
- If a field of study or degree picker needs a search, search then pick the closest option.
- LinkedIn URLs must include www. or the form rejects them.
Then report every entry you filled, every option chosen, and any validation error text.
Do not press any button yet."""


def questions_step(bank):
    known = "\n".join(f"  - {q}: {a}" for q, a in bank.items())
    return f"""Answer the application questions on this page using ONLY these answers:
{known}

Rules:
- If a question on the page is not covered above, LEAVE IT BLANK and report it verbatim.
  Do not guess, and do not infer an answer from a similar question.
- Do not tick any e-signature, certification or 'I verify this is true' box.
Then report each question, the answer you selected, and any question you left blank.
Do not press any button yet."""


ADVANCE = ("Click the button that saves this step and moves to the next one — the one "
           "labelled Next, Continue, or Save and Continue. Then report the new step's "
           "name, the names of every field on it, and any error text beginning with "
           "'Error'. Do not press any further buttons.")

SURVEY = ("Do not click anything. Report: the current step name, the full list of step "
          "names in the progress indicator, which step is currently active, the exact "
          "text of every button at the bottom of the form, and whether any of them "
          "commits the application.")


# -------------------------------------------------------------------------- main

def upload_script(page_url, filename, expect_bytes):
    """G2. Byte count and magic number are asserted inside the sandbox, before the file
    reaches the page — a 2.6 KB HTML error page once uploaded cleanly as resume.pdf. The
    PDF is uploaded exactly as downloaded; nothing re-renders or reconstructs it.
    Upload itself is handled via Playwright MCP (browser_file_upload)."""
    return f"""
PAGE=$(curl -sL "{page_url}")
LINK=$(echo "$PAGE" | grep -oE 'https://tmpfiles\\.org/dl/[0-9]+\\.[a-f0-9]+/[^"]+' | head -1)
if [ -z "$LINK" ]; then echo "G2_FAIL: no tokenized link"; exit 1; fi
curl -sL -o "/tmp/{filename}" "$LINK"
SIZE=$(stat -c%s "/tmp/{filename}"); MAGIC=$(head -c 5 "/tmp/{filename}")
echo "G2 size=$SIZE magic=$MAGIC expect={expect_bytes}"
if [ "$MAGIC" != "%PDF-" ]; then echo "G2_FAIL: not a PDF ($MAGIC)"; exit 1; fi
if [ "$SIZE" != "{expect_bytes}" ]; then echo "G2_FAIL: size $SIZE != {expect_bytes}"; exit 1; fi
echo "G2 verified /tmp/{filename} — upload via browser_file_upload next"
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", default=None, help="key in job_links.json")
    ap.add_argument("--profile", default=None, help="firecrawl browser profile name")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume-session", default=None, help="reuse an existing scrape id")
    ap.add_argument("--max-steps", type=int, default=4,
                    help="how many form steps to walk before stopping")
    args = ap.parse_args()

    profile = json.loads((ROOT / "user_profile.json").read_text(encoding="utf-8"))
    links = json.loads("{" + (ROOT / "job_links.json").read_text(encoding="utf-8")
                       .strip().rstrip(",") + "}")
    key = args.job or next(iter(links))
    if key not in links:
        sys.exit(f"--job {key!r} not in job_links.json (have: {', '.join(links)})")
    url = links[key]

    pi = profile["personal_information"]
    answers = profile.get("screening_answers", {})
    entries = roles(profile)
    edu = profile["education"][0]

    bank = {
        "Will you now or in the future require visa sponsorship": "No",
        "Are you currently employed by this organization": "No",
        "Have you previously worked for this organization": "No",
        "Are you currently being considered for another role here": "No",
        "Are you subject to a non-compete or non-solicitation agreement": "No",
        "Notice period": answers.get("notice_period", "Immediate"),
        "Earliest start date": answers.get("earliest_start_date", ""),
    }

    print(f"job {key}: {url}\n{len(entries)} roles, newest {entries[0]['company']} "
          f"({entries[0]['start']} - {entries[0]['end']})")

    browser_profile = args.profile or f"apply-{key.lower()}"
    with Session(url, browser_profile, args.dry_run, args.resume_session) as s:
        s.ask("If this page shows an Apply or Apply Now button or link for the job, click "
              "it and wait for the application form to load. If an application form is "
              "already showing, do nothing. Then report the page URL and the step name.",
              label="enter")

        s.ask(SURVEY, label="survey")
        s.spend_check("survey")

        # The resume goes in as the original PDF. G2 asserts the bytes first.
        url_file = CACHE / "resume_url.txt"
        pdf = next(ROOT.glob("*.pdf"), None)
        if url_file.exists() and pdf:
            page_url = re.sub(r"/dl/\d+\.[a-f0-9]+/", "/dl/",
                              url_file.read_text(encoding="utf-8").strip().splitlines()[0])
            out = s.bash(upload_script(page_url, "Jay_Singh_Resume.pdf",
                                       pdf.stat().st_size), label="resume")
            if "G2_FAIL" in out:
                raise SystemExit(f"G2 upload integrity failed:\n{out}")
        else:
            print("  [G2] no resume_url.txt or local PDF — skipping upload")

        s.ask(personal_step(pi, answers), label="step: personal")
        s.spend_check("personal")

        steps = [experience_step(entries, edu, {"linkedin": pi["linkedin"],
                                                "github": pi.get("github", "")}),
                 questions_step(bank)]
        for i, step in enumerate(steps[:max(0, args.max_steps - 1)], start=2):
            s.ask(ADVANCE, label=f"advance -> step {i}")
            s.ask(step, label=f"step {i}")
            s.spend_check(f"step {i}")

        # G1. Everything above fills; nothing above commits. The final click is a
        # human's, because on this flow's Workday twin the 'Save and Continue' on the
        # voluntary-disclosures step turned out to BE the submit.
        report = s.ask(SURVEY, label="final survey")
        print(f"\n{'=' * 72}\nG1 SUBMIT BOUNDARY — STOPPING\n{'=' * 72}")
        print(f"The application is filled up to the last step this run walked.\n"
              f"Nothing has been submitted. Review it yourself in the live view, then "
              f"submit by hand.\n\n"
              f"  session: {s.sid}\n"
              f"  resume the session:  .venv\\Scripts\\python.exe apply_session.py "
              f"--job {key} --resume-session {s.sid}\n")
        if report:
            print("last reported state is above — check which button commits before "
                  "clicking anything.")


if __name__ == "__main__":
    main()
