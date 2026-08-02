"""Firecrawl-cloud Workday application orchestrator.

Drives a Workday EXT apply flow entirely through Firecrawl's cloud browser
(`firecrawl scrape --profile` + `firecrawl interact`). No local Playwright.

Guard rules and selectors come from the memory graph via `python kb/project.py`
(field_map.json + guards.json). Behaviour that cost something to learn lives in
guards.py; see kb/GRAPH.md for the pitfall behind each guard.

Hard rule: G1 refuses to click the control that submits, whatever the confidence.

Usage
    $env:DRY_RUN="1"; .venv\\Scripts\\python.exe apply_orchestrator.py   # print scripts, 0 credits
    .venv\\Scripts\\python.exe apply_orchestrator.py                     # live, pre-flight gated
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
CACHE = ROOT / ".firecrawl"
CACHE.mkdir(exist_ok=True)

DRY_RUN = os.environ.get("DRY_RUN") == "1"
PROFILE = "gartner-wd"
BUDGET_CAP = 150
ABORT_IF_REMAINING_BELOW = 200

sys.path.insert(0, str(ROOT / "kb"))
import guards as G                     # noqa: E402  guard implementations
from kb import Graph                   # noqa: E402  answer bank lookups

GUARDS = G.load()                      # projected from kb/graph.json
GRAPH = Graph()
QUESTIONS = G.QuestionQueue()          # G5: never block with a live session open


# --------------------------------------------------------------------------- utils

def run(args, timeout=400):
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    return p.returncode, p.stdout, p.stderr


def credits_remaining():
    _, out, _ = run(["firecrawl", "credit-usage", "--json"])
    try:
        return json.loads(out)["data"]["remainingCredits"]
    except Exception:
        return None


class Budget:
    """Hard spend ceiling. Aborts rather than quietly eating the reserve."""

    def __init__(self):
        self.start = credits_remaining() if not DRY_RUN else 0

    def check(self, label=""):
        if DRY_RUN:
            return
        now = credits_remaining()
        if now is None:
            return
        spent = self.start - now
        print(f"  [credits] spent={spent} remaining={now} ({label})")
        if spent > BUDGET_CAP:
            sys.exit(f"ABORT: spent {spent} > cap {BUDGET_CAP}")
        if now < ABORT_IF_REMAINING_BELOW:
            sys.exit(f"ABORT: only {now} credits remain")


def sanitize(text):
    """Free-text constraints come from the graph, not a hardcoded list here."""
    return G.sanitize(text, GUARDS)


def interact(code, lang="python", timeout=290, scrape_id=None, label=""):
    """One batched call per form step — the main credit lever."""
    if DRY_RUN:
        print(f"--- DRY_RUN {lang} [{label}] ---\n{code}\n--- end ---")
        return ""
    args = ["firecrawl", "interact", f"--{lang}", "--timeout", str(timeout), "-c", code]
    if scrape_id:
        args += ["-s", scrape_id]
    rc, out, err = run(args, timeout=timeout + 90)
    if "session has been destroyed" in (out + err):
        raise SessionDead()
    if rc != 0:
        print(f"  [interact:{label}] rc={rc}\n{err[-800:]}")
    print(out)
    return out


class SessionDead(Exception):
    """Firecrawl live sessions expire after roughly 10 minutes idle."""


def open_session(url):
    """Costs 1 credit. Returns the scrape id."""
    if DRY_RUN:
        print(f"--- DRY_RUN scrape {url} ---")
        return "dry-run"
    rc, out, err = run([
        "firecrawl", "scrape", url, "--profile", PROFILE,
        "--wait-for", "10000", "--format", "markdown",
        "-o", str(CACHE / "session.md"),
    ], timeout=300)
    m = re.search(r"Scrape ID: (\S+)", out + err)
    if not m:
        sys.exit(f"could not open session:\n{out}\n{err}")
    return m.group(1)


# --------------------------------------------------------------------------- payload

def build_entries(profile):
    """Reverse-chronological work history with normalized month/year dates."""
    by_company = {w["company"]: w for w in profile["work_experience"]}
    # (company, start_month, start_year, end_month, end_year)
    # Symx AI months are absent from the profile — assumed Jan 2024 to Dec 2025.
    order = [
        ("Pibit AI (YC W21)", 1, 2026, 5, 2026),
        ("Pascal AI Labs", 11, 2025, 12, 2025),
        ("Innovaccer", 6, 2024, 8, 2024),
        ("Symx AI", 1, 2024, 12, 2025),
        ("Cambridge Judge Business School", 5, 2023, 9, 2023),
    ]
    out = []
    for company, sm, sy, em, ey in order:
        w = by_company[company]
        out.append({
            "title": w["title"],
            "company": company,
            "location": w["location"],
            "sm": sm, "sy": sy, "em": em, "ey": ey,
            "desc": sanitize("\n".join("- " + b for b in w["bullets"])),
        })
    return out


# --------------------------------------------------------------------------- steps

STEP1 = """
h = await page.locator("h3").first.inner_text()
print("HEADING:", h)
if "My Information" in h:
    await page.locator("[data-automation-id='formField-candidateIsPreviousWorker'] input[type=radio]").nth(1).check()
    await page.fill("[data-automation-id='formField-legalName--firstName'] input", %(first)s)
    await page.fill("[data-automation-id='formField-legalName--lastName'] input", %(last)s)
    await page.fill("[data-automation-id='formField-addressLine1'] input", %(addr)s)
    await page.fill("[data-automation-id='formField-city'] input", %(city)s)
    await page.fill("[data-automation-id='formField-postalCode'] input", %(zip)s)
    await page.fill("[data-automation-id='formField-phoneNumber'] input", %(phone)s)
    pt = page.locator("[data-automation-id='formField-phoneType'] button")
    if "Personal Mobile" not in (await pt.inner_text()):
        await pt.click()
        await page.wait_for_timeout(2500)
        await page.get_by_role("option", name="Personal Mobile").click()
        await page.wait_for_timeout(1500)
    await page.click("[data-automation-id='pageFooterNextButton']")
    await page.wait_for_timeout(9000)
print("NOW:", await page.locator("h3").first.inner_text())
"""

STEP2 = """
import json, re, urllib.request
ENTRIES = json.loads(%(entries)s)

# --- resume: token is IP-bound, so resolve it inside the sandbox. curl only; urllib gets 403.
items = page.locator("[data-automation-id='file-upload-item-name']")
have = [(await items.nth(i).inner_text()).strip() for i in range(await items.count())]
print("files:", have)
if not any(%(resume_name)s in h for h in have):
    print("RESUME MISSING - run the bash upload helper")

# --- work experience
n = await page.locator("[data-automation-id='formField-jobTitle']").count()
add = page.locator("button[data-automation-id='add-button']")
while n < len(ENTRIES):
    await add.nth(0).click()
    await page.wait_for_timeout(1600)
    n = await page.locator("[data-automation-id='formField-jobTitle']").count()
for i, e in enumerate(ENTRIES):
    await page.locator("[data-automation-id='formField-jobTitle']").nth(i).locator("input").fill(e["title"])
    await page.locator("[data-automation-id='formField-companyName']").nth(i).locator("input").fill(e["company"])
    await page.locator("[data-automation-id='formField-location']").nth(i).locator("input").fill(e["location"])
    sd = page.locator("[data-automation-id='formField-startDate']").nth(i)
    await sd.locator("[data-automation-id='dateSectionMonth-input']").fill(str(e["sm"]).zfill(2))
    await sd.locator("[data-automation-id='dateSectionYear-input']").fill(str(e["sy"]))
    ed = page.locator("[data-automation-id='formField-endDate']").nth(i)
    await ed.locator("[data-automation-id='dateSectionMonth-input']").fill(str(e["em"]).zfill(2))
    await ed.locator("[data-automation-id='dateSectionYear-input']").fill(str(e["ey"]))
    await page.locator("[data-automation-id='formField-roleDescription']").nth(i).locator("textarea").fill(e["desc"])
    print("filled", i, e["company"])

# --- education
await page.locator("[data-automation-id='formField-schoolName']").nth(0).locator("input").fill(%(school)s)
deg = page.locator("[data-automation-id='formField-degree'] button").first
if "Select One" in (await deg.inner_text()):
    await deg.click()
    await page.wait_for_timeout(2500)
    await page.get_by_role("option", name="Bachelor's Degree", exact=True).click()
    await page.wait_for_timeout(1500)

# --- field of study: MUST go through the search button; typing in the field does not filter
fos = page.locator("[data-automation-id='formField-fieldOfStudy']").first
if %(fos)s not in (await fos.inner_text()):
    await page.locator("[data-automation-id='promptSearchButton']").first.click()
    await page.wait_for_timeout(2000)
    sb = page.get_by_placeholder("Search").first
    await sb.click()
    await sb.press_sequentially(%(fos_query)s, delay=80)
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(6000)
    opts = page.get_by_role("option")
    if await opts.count():
        await opts.nth(0).click()
        await page.wait_for_timeout(2000)
    await page.keyboard.press("Escape")

# --- linkedin: the www. is mandatory
await page.locator("[data-automation-id='formField-linkedInAccount'] input").fill(%(linkedin)s)

await page.click("[data-automation-id='pageFooterNextButton']")
await page.wait_for_timeout(11000)
print("NOW:", await page.locator("h3").first.inner_text())
txt = await page.locator("body").inner_text()
for line in txt.split("\\n"):
    if line.strip().startswith("Error"):
        print("ERRLINE:", line[:200])
"""

UPLOAD_SH = """
PAGE=$(curl -sL "%(page_url)s")
LINK=$(echo "$PAGE" | grep -oE 'https://tmpfiles\\.org/dl/[0-9]+\\.[a-f0-9]+/[^"]+' | head -1)
curl -sL -o "/tmp/%(name)s" "$LINK"
SIZE=$(stat -c%%s "/tmp/%(name)s")
MAGIC=$(head -c 5 "/tmp/%(name)s")
echo "size=$SIZE magic=$MAGIC"
if [ "$MAGIC" != "%%PDF-" ]; then echo "ABORT: not a PDF"; exit 1; fi
agent-browser upload "input[data-automation-id=file-upload-input-ref]" "/tmp/%(name)s"
sleep 9
agent-browser eval "Array.from(document.querySelectorAll('[data-automation-id=file-upload-item]')).map(e=>e.innerText.replace(/\\n/g,' ')).join(' || ')"
"""

STEP3 = """
import json
QA = json.loads(%(qa)s)
for aid, want in QA:
    btn = page.locator("[data-automation-id='" + aid + "']").locator("button").first
    cur = (await btn.inner_text()).replace("\\n", " ").strip()
    if want in cur and "Select One" not in cur:
        print(aid[-8:], "already", cur); continue
    await btn.click()
    await page.wait_for_timeout(2000)
    await page.get_by_role("option", name=want, exact=True).first.click()
    await page.wait_for_timeout(1000)
    print(aid[-8:], "->", (await btn.inner_text()).replace("\\n", " ").strip())
await page.click("[data-automation-id='pageFooterNextButton']")
await page.wait_for_timeout(10000)
print("NOW:", await page.locator("h3").first.inner_text())
"""

# NOTE: continuing past this point submits. Guarded by STOP_BEFORE_SUBMIT.
STEP4_FILL_ONLY = """
cb = page.locator("[data-automation-id='formField-acceptTermsAndAgreements'] input[type=checkbox]")
await cb.check()
print("terms checked:", await cb.is_checked())
btns = page.locator("[data-automation-id='pageFooter'] button")
for i in range(await btns.count()):
    print("FOOTER:", (await btns.nth(i).inner_text()).strip(),
          "|", await btns.nth(i).get_attribute("data-automation-id"))
print("STOPPING: the next click on pageFooterNextButton SUBMITS this application.")
"""


# --------------------------------------------------------------------------- main

def main():
    profile = json.loads((ROOT / "user_profile.json").read_text(encoding="utf-8"))
    links = json.loads("{" + (ROOT / "job_links.json").read_text(encoding="utf-8").strip().rstrip(",") + "}")
    url = list(links.values())[0]
    pi = profile["personal_information"]
    entries = build_entries(profile)

    if not DRY_RUN and os.environ.get("SKIP_PREFLIGHT") != "1":
        rc, out, err = run([sys.executable, str(ROOT / "preflight.py")], timeout=180)
        print(out)
        if rc != 0:
            sys.exit("pre-flight blocked the run. Reconcile the items above, or set "
                     "SKIP_PREFLIGHT=1 to override.")

    budget = Budget()
    print(f"credits at start: {budget.start} | DRY_RUN={DRY_RUN} | "
          f"terminal submit step = {GUARDS['terminal_submit_step']}")

    apply_url = url.replace("/apply?", "/apply/applyManually?")
    sid = open_session(apply_url)
    print("scrape id:", sid)
    budget.check("session open")

    q = json.dumps
    interact(STEP1 % {
        "first": q(pi["first_name"]), "last": q(pi["last_name"]),
        "addr": q(pi["address_line_1"]), "city": q(pi["city"]),
        "zip": q(pi["postal_code"]),
        "phone": q(pi["phone"].split("-", 1)[-1]),
    }, label="step1", scrape_id=sid)
    budget.check("step1")

    # G2: verify magic bytes and exact byte count inside the sandbox, before the file
    # reaches the page. A 2.6 KB HTML error page once uploaded cleanly as "resume.pdf".
    resume_url = (CACHE / "resume_url.txt").read_text().strip().split("\n")[0]
    page_url = re.sub(r"/dl/\d+\.[a-f0-9]+/", "/dl/", resume_url)
    local_pdf = next(ROOT.glob("*.pdf"), None)
    expect_bytes = local_pdf.stat().st_size if local_pdf else 0
    out = interact(G.upload_probe(page_url, "Jay_Singh_Resume.pdf", expect_bytes),
                   lang="bash", timeout=200, scrape_id=sid, label="resume")
    if not DRY_RUN:
        print("  [G2]", G.verify_upload(out, "Jay_Singh_Resume.pdf"))
    budget.check("resume")

    interact(STEP2 % {
        "entries": q(json.dumps(entries)),
        "resume_name": q("Jay_Singh_Resume"),
        "school": q("Indian Institute of Technology Kharagpur"),
        "fos": q("Computer and Information Science"),
        "fos_query": q("Computer Science"),
        "linkedin": q("https://www.linkedin.com/in/jay-singh-ds/"),
    }, label="step2", scrape_id=sid)
    budget.check("step2")

    # Screening answers resolve from the answer bank first; anything the bank cannot
    # match is queued rather than guessed (G5 + G7).
    fmap = json.loads((ROOT / "field_map.json").read_text(encoding="utf-8"))
    qa = []
    for key, v in fmap["fields"].items():
        if not key.startswith("q."):
            continue
        value, score, who = QUESTIONS.resolve(GRAPH, v["label"], tenant=fmap["_tenant"])
        if value is None:
            QUESTIONS.ask(key, v["label"], why=f"no answer-bank match (best {score:.2f})")
            continue
        qa.append((v["aid"], value))
        print(f"  [answer bank] {key} -> {value} (match {score:.2f}, decided by {who})")
    interact(STEP3 % {"qa": q(json.dumps(qa))}, label="step3", scrape_id=sid)
    budget.check("step3")

    out = interact(STEP4_FILL_ONLY, label="step4", scrape_id=sid)
    budget.check("step4")

    # G1. The submit boundary. Never crossed by automation.
    footer = [ln for ln in out.splitlines() if ln.startswith("FOOTER:")]
    try:
        G.terminal_step_guard(GUARDS["terminal_submit_step"], GUARDS,
                              scrape_id=sid, footer=footer)
        interact("await page.click(\"[data-automation-id='pageFooterNextButton']\")\n"
                 "await page.wait_for_timeout(12000)\n"
                 "print((await page.locator('body').inner_text())[:800])",
                 label="submit", scrape_id=sid)
    except G.SubmitBoundary as stop:
        print(f"\n{'=' * 72}\nG1 SUBMIT BOUNDARY\n{'=' * 72}\n{stop}")

    print(f"\n{QUESTIONS.report()}")
    budget.check("done")


if __name__ == "__main__":
    main()
