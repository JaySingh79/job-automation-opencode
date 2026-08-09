"""Firecrawl-cloud job application orchestrator.

Drives a multi-step apply flow entirely through Firecrawl's cloud browser
(`firecrawl scrape --profile` + `firecrawl interact`). No local Playwright.

Two drivers, selected per job by URL:

    workday  Gartner EXT — fields addressed by data-automation-id on wrapper divs
    phenom   HPE careers — a Workday-shaped schema rendered by Phenom's own DOM,
             addressed by plain element ids

The layers above the DOM are shared: the answer bank, the free-text constraints, the
question queue and every guard apply to both. Only the selector layer differs, which is
the whole point of keeping selectors per-tenant in the graph.

Guard rules and selectors come from the memory graph via `python kb/project.py <tenant>`
(field_map.json + guards.json). Behaviour that cost something to learn lives in
guards.py; see kb/GRAPH.md for the pitfall behind each guard.

Hard rule: G1 refuses to click the control that submits, whatever the confidence.

Usage
    $env:JOB="HPE"; $env:DRY_RUN="1"; .venv\\Scripts\\python.exe apply_orchestrator.py
    $env:JOB="HPE"; .venv\\Scripts\\python.exe apply_orchestrator.py   # live, pre-flight gated
    .venv\\Scripts\\python.exe apply_orchestrator.py                   # first job in job_links.json
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
CACHE = ROOT / ".firecrawl"
CACHE.mkdir(exist_ok=True)

DRY_RUN = os.environ.get("DRY_RUN") == "1"
BUDGET_CAP = 150
ABORT_IF_REMAINING_BELOW = 200

# Per-tenant facts that are not DOM knowledge and so do not belong in the graph: which
# driver renders the flow, which browser profile owns it (G12: one writer per profile),
# and how to recognise the tenant from a job URL.
TENANTS = {
    "gartner": {
        "match": "gartner.wd5.myworkdayjobs.com",
        "graph_tenant": "tenant:gartner.wd5/EXT",
        "driver": "workday",
        "profile": "gartner-wd",
    },
    "hpe": {
        "match": "careers.hpe.com",
        "graph_tenant": "tenant:hpe.phenom/HPE1US",
        "driver": "phenom",
        "profile": "hpe-phenom",
    },
}


def tenant_for(url):
    for name, cfg in TENANTS.items():
        if cfg["match"] in url:
            return name, cfg
    sys.exit(f"no driver knows how to fill {url}\n"
             f"known tenants: {', '.join(c['match'] for c in TENANTS.values())}")

sys.path.insert(0, str(ROOT / "kb"))
import guards as G                     # noqa: E402  guard implementations
from kb import Graph                   # noqa: E402  answer bank lookups

GUARDS = G.load()                      # projected from kb/graph.json
GRAPH = Graph()
QUESTIONS = G.QuestionQueue()          # G5: never block with a live session open


# --------------------------------------------------------------------------- utils

FIRECRAWL = shutil.which("firecrawl") or "firecrawl"


def run(args, timeout=400):
    # On Windows the CLI is a .CMD shim, and CreateProcess does not apply PATHEXT to a
    # bare name — subprocess raises FileNotFoundError where the same word works in a
    # shell. Resolve it once rather than shelling out.
    if args and args[0] == "firecrawl":
        args = [FIRECRAWL, *args[1:]]
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
    """One batched call per form step — the main credit lever.

    The code is stripped first. A leading newline makes the CLI report
    "option '-c, --code <code>' argument missing" and fall through to its
    'provide an AI prompt' error, so every triple-quoted script here would fail
    silently-looking on its first character. Multi-line bodies are fine.

    The flag is --python/--bash/--node on v1.19.27; --language <lang> is a different
    version's spelling and is rejected as an unknown option.
    """
    code = code.strip()
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


def stop_session(scrape_id):
    """Sessions bill by wall-clock, not per call — 166s cost 6 credits — and they hold
    the profile's single writer lock (G12) until stopped. A crashed run that leaks one
    therefore keeps charging and blocks the next attempt with 'Another session is
    currently writing to this profile'. Always run this, even on the failure path.
    """
    if DRY_RUN or not scrape_id or scrape_id == "dry-run":
        return
    rc, out, err = run(["firecrawl", "interact", "stop", scrape_id], timeout=120)
    print(f"  [session] {(out or err).strip().splitlines()[0] if (out or err) else 'stopped'}")


SESSION = {}          # the live scrape id, so the finally-block can always release it


def open_session(url, profile):
    """Costs 1 credit up front, then bills for as long as the session stays open."""
    if DRY_RUN:
        print(f"--- DRY_RUN scrape {url} ---")
        return "dry-run"
    rc, out, err = run([
        "firecrawl", "scrape", url, "--profile", profile,
        "--wait-for", "10000", "--format", "markdown",
        "-o", str(CACHE / "session.md"),
    ], timeout=300)
    m = re.search(r"Scrape ID: (\S+)", out + err)
    if not m:
        sys.exit(f"could not open session:\n{out}\n{err}")
    SESSION["id"] = m.group(1)
    return m.group(1)


# --------------------------------------------------------------------------- payload

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def parse_dates(text):
    """'Sep 2024 - Feb 2025' -> (9, 2024, 2, 2025).

    Raises rather than defaulting a missing month. The previous version carried a
    hardcoded table with 'Symx AI months are absent — assumed Jan 2024 to Dec 2025',
    and those invented months went onto a submitted application (pitfall E3). A profile
    that cannot supply a month is a bug in the profile, not something to paper over.
    """
    parts = [p.strip() for p in re.split(r"[-–—]", text) if p.strip()]
    if len(parts) != 2:
        raise ValueError(f"unparseable date range {text!r}")
    out = []
    for part in parts:
        m = re.match(r"([A-Za-z]{3,9})\.?\s+(\d{4})$", part)
        if not m:
            raise ValueError(f"{text!r}: '{part}' has no month. Add one to "
                             f"user_profile.json — E3 forbids inventing it.")
        month = MONTHS.get(m.group(1)[:3].lower())
        if month is None:
            raise ValueError(f"{text!r}: unknown month '{m.group(1)}'")
        out += [month, int(m.group(2))]
    return tuple(out)


def build_entries(profile):
    """Every role in the profile, reverse-chronological, months parsed not assumed.

    All of them: work_ex_details.md is the authoritative history and the resume PDF is
    expected to lag it (user's standing decision, 2026-08-03), so filtering entries down
    to what the resume mentions would silently drop real roles.
    """
    out = []
    for w in profile["work_experience"]:
        sm, sy, em, ey = parse_dates(w["dates"])
        out.append({
            "title": w["title"],
            "company": w["company"],
            "location": w["location"],
            "sm": sm, "sy": sy, "em": em, "ey": ey,
            "desc": sanitize("\n".join("- " + b for b in w["bullets"])),
        })
    out.sort(key=lambda e: (e["sy"], e["sm"]), reverse=True)
    return out


# ------------------------------------------------------------------ workday steps

WD_STEP1 = """
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

WD_STEP2 = """
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

WD_UPLOAD_SH = """
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

WD_STEP3 = """
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
WD_STEP4_FILL_ONLY = """
cb = page.locator("[data-automation-id='formField-acceptTermsAndAgreements'] input[type=checkbox]")
await cb.check()
print("terms checked:", await cb.is_checked())
btns = page.locator("[data-automation-id='pageFooter'] button")
for i in range(await btns.count()):
    print("FOOTER:", (await btns.nth(i).inner_text()).strip(),
          "|", await btns.nth(i).get_attribute("data-automation-id"))
print("STOPPING: the next click on pageFooterNextButton SUBMITS this application.")
"""


# ------------------------------------------------------------------- phenom steps
#
# Phenom element ids contain dots, and one contains a space
# ('cntryFields.firstName', 'Additional Fields.noticeAgreement'). A CSS '#id' selector
# reads the dot as a class and the space as a descendant combinator, so every id here
# goes through an attribute selector instead. This tenant's version of D6.

PH_SEL = """
def sel(i):
    return "[id='" + i + "']"
"""

# Enter through the posting's own Apply Now link. The bare /apply?jobSeqNo= URL renders
# for a scraper but does not carry the job context through a real navigation, so the
# session has to arrive the way a candidate would. No login is required either way.
PH_ENTER = """
# The interact session starts on about:blank rather than the scraped page, so navigate
# explicitly instead of assuming the scrape left the browser where it was.
if "careers.hpe.com" not in page.url:
    await page.goto(%(job_url)s, wait_until="domcontentloaded")
    await page.wait_for_timeout(8000)
print("FROM:", page.url)

link = page.locator("a[href*='/apply?jobSeqNo=']").first
if await link.count():
    await link.click()
    await page.wait_for_timeout(12000)
else:
    print("no Apply Now link found; going direct")
    await page.goto(%(apply_url)s, wait_until="domcontentloaded")
    await page.wait_for_timeout(12000)

print("LANDED:", page.url)
print("STEPS:", [t.strip() for t in
      (await page.locator("h1, h2, h3, .step-name, [class*=step]").all_inner_texts())
      if t.strip()][:12])
print("FIELDS:", await page.locator("input, select").count())
"""

PH_STEP1 = PH_SEL + """
# Country first: it re-renders the whole cntryFields block, wiping anything typed before it.
await page.select_option(sel("country"), label=%(country)s)
await page.wait_for_timeout(3500)

await page.fill(sel("cntryFields.firstName"), %(first)s)
await page.fill(sel("cntryFields.lastName"), %(last)s)
await page.fill(sel("cntryFields.addressLine1"), %(addr)s)
await page.fill(sel("cntryFields.city"), %(city)s)
await page.fill(sel("cntryFields.postalCode"), %(zip)s)
await page.fill(sel("email"), %(email)s)

# D7 alias: the profile says 'Mobile', the only matching option is 'Personal Mobile'.
await page.select_option(sel("deviceType"), label=%(device)s)
await page.select_option(sel("phoneWidget.countryPhoneCode"), label=%(phonecc)s)
await page.fill(sel("phoneWidget.phoneNumber"), %(phone)s)

await page.select_option(sel("source"), label=%(heard)s)
src = await page.locator(sel("applicantSource") + " option").all_inner_texts()
print("applicantSource options:", src)
if len(src) == 2:
    await page.select_option(sel("applicantSource"), index=1)

# G11. Only the mandatory data-processing agreement is ticked. The AI-tools, SMS and
# email consents are optional and deliberately left alone; both facts go in the report.
await page.check(sel("Additional Fields.noticeAgreement"))
print("ATTESTATION ticked: Additional Fields.noticeAgreement (required to proceed)")
for opt in ("aiConsent", "smsOptIn", "emailCommunication"):
    box = page.locator(sel(opt))
    if await box.count():
        print("ATTESTATION left unchecked:", opt, await box.is_checked())

print("READBACK first=", await page.input_value(sel("cntryFields.firstName")),
      "email=", await page.input_value(sel("email")),
      "phone=", await page.input_value(sel("phoneWidget.phoneNumber")))
"""

PH_ADVANCE = PH_SEL + """
await page.click(sel("next"))
await page.wait_for_timeout(%(wait)s)
print("URL:", page.url)
# G6. Validation text is not in role=alert; 'Error'-prefixed innerText lines are the read.
body = await page.locator("body").inner_text()
for line in body.split("\\n"):
    s = line.strip()
    if s.startswith("Error") or "is required" in s:
        print("ERRLINE:", s[:200])
"""

# Steps 2-5 are unmapped. This dumps their shape without typing anything, so the next
# batched call can fill them. Reading via interact costs less than a fresh scrape+parse.
PH_PROBE = """
print("URL:", page.url)
for tag in ("input", "select", "textarea", "button"):
    loc = page.locator(tag)
    for i in range(min(await loc.count(), 60)):
        el = loc.nth(i)
        ident = await el.get_attribute("id")
        if not ident:
            continue
        print(tag.upper(), ident, "|", (await el.get_attribute("aria-label"))
              or (await el.get_attribute("type")) or "")
"""


# --------------------------------------------------------------------------- main

def resume_source():
    """(tmpfiles page URL, exact local byte count). G2 compares the two."""
    resume_url = (CACHE / "resume_url.txt").read_text(encoding="utf-8").strip().split("\n")[0]
    page_url = re.sub(r"/dl/\d+\.[a-f0-9]+/", "/dl/", resume_url)
    local_pdf = next(ROOT.glob("*.pdf"), None)
    return page_url, (local_pdf.stat().st_size if local_pdf else 0)


def screening_answers(fmap):
    """Resolve q.* fields from the answer bank; queue whatever it cannot match.

    Shared by both drivers — screening questions are the layer that transfers between
    employers, so nothing here is tenant-specific except the tenant lock on
    employer-named questions.
    """
    qa = []
    for key, v in fmap["fields"].items():
        if not key.startswith("q."):
            continue
        value, score, who = QUESTIONS.resolve(GRAPH, v["label"], tenant=fmap["_tenant"])
        if value is None:
            QUESTIONS.ask(key, v["label"], why=f"no answer-bank match (best {score:.2f})")
            continue
        qa.append((v.get("aid") or v.get("automation_id"), value))
        print(f"  [answer bank] {key} -> {value} (match {score:.2f}, decided by {who})")
    return qa


def guards_for(cfg):
    """Guard rules only count when they were projected for the tenant being filled.

    field_map.json and guards.json hold one tenant at a time. Reusing another tenant's
    projection would let G1 compare step 4 of this flow against step 4 of a different
    one — and terminal_step_guard returns True, permitting the click, whenever the
    indexes fail to match. An unprojected tenant therefore has no known boundary, which
    is the state G1 already treats as destructive.
    """
    fmap = json.loads((ROOT / "field_map.json").read_text(encoding="utf-8"))
    if fmap.get("_tenant") != cfg["graph_tenant"]:
        return {**GUARDS, "terminal_submit_step": None}, False
    return GUARDS, True


def stop_or_submit(step_index, guards, sid, footer, click_code):
    """G1. The submit boundary. Never crossed by automation, for any driver."""
    try:
        G.terminal_step_guard(step_index, guards, scrape_id=sid, footer=footer)
    except G.SubmitBoundary as stop:
        print(f"\n{'=' * 72}\nG1 SUBMIT BOUNDARY\n{'=' * 72}\n{stop}")
        return False
    interact(click_code, label="submit", scrape_id=sid)
    return True


# ------------------------------------------------------------------ workday driver

def run_workday(cfg, url, profile, entries, budget):
    pi = profile["personal_information"]
    q = json.dumps

    sid = open_session(url.replace("/apply?", "/apply/applyManually?"), cfg["profile"])
    print("scrape id:", sid)
    budget.check("session open")

    interact(WD_STEP1 % {
        "first": q(pi["first_name"]), "last": q(pi["last_name"]),
        "addr": q(pi["address_line_1"]), "city": q(pi["city"]),
        "zip": q(pi["postal_code"]),
        "phone": q(pi["phone"].split("-", 1)[-1]),
    }, label="step1", scrape_id=sid)
    budget.check("step1")

    # G2: verify magic bytes and exact byte count inside the sandbox, before the file
    # reaches the page. A 2.6 KB HTML error page once uploaded cleanly as "resume.pdf".
    page_url, expect_bytes = resume_source()
    out = interact(G.upload_probe(page_url, "Jay_Singh_Resume.pdf", expect_bytes),
                   lang="bash", timeout=200, scrape_id=sid, label="resume")
    if not DRY_RUN:
        print("  [G2]", G.verify_upload(out, "Jay_Singh_Resume.pdf"))
    budget.check("resume")

    interact(WD_STEP2 % {
        "entries": q(json.dumps(entries)),
        "resume_name": q("Jay_Singh_Resume"),
        "school": q("Indian Institute of Technology Kharagpur"),
        "fos": q("Computer and Information Science"),
        "fos_query": q("Computer Science"),
        "linkedin": q("https://www.linkedin.com/in/jay-singh-ds/"),
    }, label="step2", scrape_id=sid)
    budget.check("step2")

    fmap = json.loads((ROOT / "field_map.json").read_text(encoding="utf-8"))
    interact(WD_STEP3 % {"qa": q(json.dumps(screening_answers(fmap)))},
             label="step3", scrape_id=sid)
    budget.check("step3")

    out = interact(WD_STEP4_FILL_ONLY, label="step4", scrape_id=sid)
    budget.check("step4")

    guards, _ = guards_for(cfg)
    stop_or_submit(guards.get("terminal_submit_step"), guards, sid,
                   [ln for ln in out.splitlines() if ln.startswith("FOOTER:")],
                   "await page.click(\"[data-automation-id='pageFooterNextButton']\")\n"
                   "await page.wait_for_timeout(12000)\n"
                   "print((await page.locator('body').inner_text())[:800])")


# ------------------------------------------------------------------- phenom driver

def run_phenom(cfg, url, profile, entries, budget):
    pi = profile["personal_information"]
    q = json.dumps

    sid = open_session(url, cfg["profile"])
    print("scrape id:", sid)
    budget.check("session open")

    seq = re.search(r"/job/(\d+)", url)
    apply_url = (f"https://careers.hpe.com/us/en/apply?jobSeqNo="
                 f"HPE1US{seq.group(1)}EXTERNALENUS" if seq else url)
    interact(PH_ENTER % {"job_url": q(url), "apply_url": q(apply_url)},
             label="enter", scrape_id=sid)
    budget.check("enter")

    # The resume goes in on step 1 here, not step 2, and HPE caps it at 1 MB.
    page_url, expect_bytes = resume_source()
    if expect_bytes > 1_000_000:
        sys.exit(f"resume is {expect_bytes} bytes; HPE rejects anything over 1 MB")
    out = interact(G.upload_probe(page_url, "Jay_Singh_Resume.pdf", expect_bytes,
                                  file_input="input[type=file]",
                                  confirm="[class*=file], [class*=upload]"),
                   lang="bash", timeout=200, scrape_id=sid, label="resume")
    if not DRY_RUN:
        # Phenom does not use Workday's 'Successfully Uploaded!' wording, so the byte
        # and magic assertions inside the sandbox carry G2 here.
        print("  [G2]", G.verify_upload(out, "Jay_Singh_Resume.pdf", success_marker=""))
    budget.check("resume")

    interact(PH_STEP1 % {
        "country": q(pi["country"]),
        "first": q(pi["first_name"]), "last": q(pi["last_name"]),
        "addr": q(pi["address_line_1"]), "city": q(pi["city"]),
        "zip": q(pi["postal_code"]), "email": q(pi["email"]),
        "device": q("Personal Mobile"),
        "phonecc": q(f"{pi['country']} (+91)"),
        "phone": q(pi["phone"].split("-", 1)[-1]),
        "heard": q(profile["screening_answers"].get("ats_source", "HPE Career site")),
    }, label="step1", scrape_id=sid)
    budget.check("step1")

    interact(PH_ADVANCE % {"wait": 9000}, label="step1-next", scrape_id=sid)
    budget.check("step1-next")

    # Steps 2-5 have never been observed on this tenant. Probe rather than guess: an
    # unmapped step is exactly the state in which G1 refuses to click anything.
    interact(PH_PROBE, label="probe-step2", scrape_id=sid)
    budget.check("probe")

    print(f"\n{'=' * 72}\nPHENOM FLOW UNMAPPED PAST STEP 1\n{'=' * 72}\n"
          f"Step 1 is filled and saved. Steps 2-5 are dumped above but not yet in the\n"
          f"graph, so no continue click is safe. Fold the probe output into\n"
          f"kb/seed_hpe.py, re-project, and re-run to fill the rest.")

    # The step labels match Gartner's exactly, where step 4's continue turned out to be
    # the submit (A1). Until this tenant's own boundary is observed, every continue here
    # is treated as that same click.
    guards, projected = guards_for(cfg)
    stop_or_submit(guards.get("terminal_submit_step"), guards, sid, [],
                   PH_SEL + "await page.click(sel('next'))\n"
                            "await page.wait_for_timeout(12000)\n"
                            "print((await page.locator('body').inner_text())[:800])")


# --------------------------------------------------------------------------- main

def main():
    profile = json.loads((ROOT / "user_profile.json").read_text(encoding="utf-8"))
    links = json.loads("{" + (ROOT / "job_links.json").read_text(encoding="utf-8").strip().rstrip(",") + "}")

    want = os.environ.get("JOB")
    if want and want not in links:
        sys.exit(f"JOB={want!r} not in job_links.json (have: {', '.join(links)})")
    key = want or next(iter(links))
    url = links[key]
    name, cfg = tenant_for(url)
    entries = build_entries(profile)

    if not DRY_RUN and os.environ.get("SKIP_PREFLIGHT") != "1":
        rc, out, err = run([sys.executable, str(ROOT / "preflight.py")], timeout=180)
        print(out)
        if rc != 0:
            sys.exit("pre-flight blocked the run. Reconcile the items above, or set "
                     "SKIP_PREFLIGHT=1 to override.")

    budget = Budget()
    guards, projected = guards_for(cfg)
    terminal = guards.get("terminal_submit_step")
    print(f"job: {key} | tenant: {name} | driver: {cfg['driver']} | DRY_RUN={DRY_RUN}\n"
          f"credits at start: {budget.start} | {len(entries)} work entries\n"
          f"terminal submit step = "
          f"{terminal if projected else 'UNKNOWN — graph has never seen this tenant, '
                                        'so G1 blocks every continue click'}")
    if not projected:
        print(f"  (field_map.json is projected for another tenant; run "
              f"`kb/project.py {cfg['graph_tenant']}` once the flow is mapped)")

    driver = {"workday": run_workday, "phenom": run_phenom}[cfg["driver"]]
    try:
        driver(cfg, url, profile, entries, budget)
    finally:
        # Billed by duration and holds the G12 writer lock, so it is released even when
        # a guard aborts the run — otherwise the next attempt cannot open the profile.
        stop_session(SESSION.get("id"))

    print(f"\n{QUESTIONS.report()}")
    budget.check("done")


if __name__ == "__main__":
    main()
