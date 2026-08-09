"""Guard implementations. Rules come from guards.json, which is projected from the graph.

Each guard here exists because it was paid for once. See kb/GRAPH.md for the pitfall
that produced it.
"""

import json
import os
import re
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).parent
GUARDS_JSON = ROOT / "guards.json"

OPTION_FLOOR = 0.72       # below this, do not guess — queue a question
ATTESTATION = re.compile(r"e-?signature|certify|i verify|consent|acknowledg", re.I)
HONEYPOT = re.compile(r"robots only|do not enter if you", re.I)


def load():
    return json.loads(GUARDS_JSON.read_text(encoding="utf-8"))


class SubmitBoundary(Exception):
    """G1. Raised instead of clicking the control that submits the application."""


class UploadIntegrityError(Exception):
    """G2. Raised when the bytes that reached the browser are not the bytes intended."""


# ------------------------------------------------------------------ G1

def terminal_step_guard(step_index, guards, scrape_id=None, footer=None):
    """The Gartner incident: step 4's 'Save and Continue' was the submit, and the
    progress bar's step 5 'Review' was a post-submit confirmation screen.

    Refuses unless ALLOW_SUBMIT=1 is set by a human, which automation never does.
    """
    terminal = guards.get("terminal_submit_step")
    if terminal is None:
        raise SubmitBoundary(
            "Terminal submit step is unknown for this tenant. Every continue click is "
            "treated as destructive until the graph records which step submits."
        )
    if step_index != terminal:
        return True
    if os.environ.get("ALLOW_SUBMIT") == "1":
        return True
    raise SubmitBoundary(
        f"Step {step_index} is the submit boundary for this tenant — continuing here "
        f"SUBMITS the application, irreversibly.\n"
        + (f"footer buttons: {footer}\n" if footer else "")
        + (f"to submit yourself: firecrawl interact -s {scrape_id} "
           f"--prompt \"Click Save and Continue\"\n" if scrape_id else "")
    )


# ------------------------------------------------------------------ G2

def upload_probe(url_page, filename, expect_bytes,
                 file_input="input[data-automation-id=file-upload-input-ref]",
                 confirm="[data-automation-id=file-upload-item]"):
    """Bash run inside the cloud sandbox. Verifies before the file ever reaches the page.

    Three separate failures produced this: the /dl/ URL serves HTML, its token is
    IP-bound so it must be resolved in the sandbox, and urllib gets 403 where curl
    does not. The 2.6 KB HTML page that was uploaded as a resume passed none of these.

    The file is uploaded byte-for-byte as downloaded — never re-rendered or reconstructed.
    The size assertion is what enforces that. `file_input`/`confirm` default to Workday's
    automation-ids; Phenom and other ATSs pass their own.
    """
    return f"""
PAGE=$(curl -sL "{url_page}")
LINK=$(echo "$PAGE" | grep -oE 'https://tmpfiles\\.org/dl/[0-9]+\\.[a-f0-9]+/[^"]+' | head -1)
if [ -z "$LINK" ]; then echo "G2_FAIL: no tokenized link on the page"; exit 1; fi
curl -sL -o "/tmp/{filename}" "$LINK"
SIZE=$(stat -c%s "/tmp/{filename}")
MAGIC=$(head -c 5 "/tmp/{filename}")
echo "G2 size=$SIZE magic=$MAGIC expect={expect_bytes}"
if [ "$MAGIC" != "%PDF-" ];        then echo "G2_FAIL: not a PDF (got $MAGIC)"; exit 1; fi
if [ "$SIZE" != "{expect_bytes}" ]; then echo "G2_FAIL: size $SIZE != {expect_bytes}"; exit 1; fi
agent-browser upload "{file_input}" "/tmp/{filename}"
sleep 9
agent-browser eval "Array.from(document.querySelectorAll('{confirm}')).map(e=>e.innerText.replace(/\\n/g,' ')).join(' || ')"
"""


def verify_upload(output, filename, success_marker="Successfully Uploaded"):
    """Read back what the DOM actually reports. 'Successfully Uploaded!' alone is not
    enough — the HTML page uploaded last time also reported success.

    `success_marker` is Workday's wording; other ATSs confirm differently.
    """
    if "G2_FAIL" in output:
        raise UploadIntegrityError(output.strip().splitlines()[-1])
    if filename not in output:
        raise UploadIntegrityError(f"{filename} not present in the upload list: {output[:300]}")
    if success_marker and success_marker not in output:
        raise UploadIntegrityError(f"no success confirmation in DOM: {output[:300]}")
    kb = re.search(r"([\d.]+)\s*KB", output)
    return {"filename": filename, "reported_kb": float(kb.group(1)) if kb else None}


# ------------------------------------------------------------------ G3/G6

def sanitize(text, guards):
    """Apply every free-text constraint the graph knows about, before the first fill
    rather than after the server rejects it."""
    c = guards["constraints"].get("constraint:illegal_chars")
    if not c:
        return text
    text = text.replace(">=", "at least ").replace("<=", "at most ")
    text = re.sub(r">\s*(\d)", r"over \1", text)
    text = re.sub(r"<\s*(\d)", r"under \1", text)
    text = (text.replace(chr(8220), "").replace(chr(8221), "")
                .replace(chr(8217), "'").replace(chr(8212), "-").replace(chr(8211), "-"))
    for ch in c["chars"]:
        text = text.replace(ch, "")
    return text


def validate(field_id, value, guards):
    """Returns (ok, fixed_value, message)."""
    for cid, c in guards["constraints"].items():
        if c.get("applies_to") != field_id or "regex" not in c:
            continue
        if re.match(c["regex"], value):
            return True, value, ""
        if cid == "constraint:linkedin_www":
            fixed = value.replace("https://linkedin.com", "https://www.linkedin.com")
            if re.match(c["regex"], fixed):
                return True, fixed, f"autofixed for {cid}: added www."
        return False, value, f"{cid}: {c.get('error', 'invalid')}"
    return True, value, ""


def harvest_errors(page_text):
    """Workday puts validation text nowhere machine-readable — not errorMessage, not
    role=alert, and aria-invalid elements are empty. Lines starting with 'Error' are
    the only reliable surface."""
    return [ln.strip() for ln in page_text.splitlines() if ln.strip().startswith("Error")]


# ------------------------------------------------------------------ G7

def resolve_option(wanted, offered, aliases=None):
    """Never type into a dropdown. Enumerate, then match.

    Returns (choice, score, is_alias). choice is None below the floor — queue a question
    rather than guessing, because 'Mobile' vs 'Personal Mobile' is a cheap miss but
    'Bachelor's' vs 'Master's' is not.
    """
    aliases = aliases or {}
    if wanted in aliases and aliases[wanted] in offered:
        return aliases[wanted], 1.0, True
    if wanted in offered:
        return wanted, 1.0, False

    best, score = None, 0.0
    for o in offered:
        s = SequenceMatcher(None, wanted.lower(), o.lower()).ratio()
        if s > score:
            best, score = o, s
    return (best, score, False) if score >= OPTION_FLOOR else (None, score, False)


def is_honeypot(label):
    """'Enter website. This input is for robots only, do not enter if you're human.'"""
    return bool(HONEYPOT.search(label or ""))


# ------------------------------------------------------------------ G11

def is_attestation(label):
    return bool(ATTESTATION.search(label or ""))


# ------------------------------------------------------------------ G5

class QuestionQueue:
    """Never block a human with a live session open — that cost two sessions and a
    reconnect last time. Collect, keep filling, ask once at the end."""

    def __init__(self):
        self.items = []

    def ask(self, field, question, options=None, why=""):
        self.items.append({"field": field, "question": question,
                           "options": options or [], "why": why})

    def resolve(self, graph, question, tenant=None):
        """Try the answer bank first. Screening questions repeat across employers,
        except the ones that name an employer — those stay with their tenant."""
        node, score = graph.find_answer(question, tenant=tenant)
        if node:
            return node["attrs"]["value"], score, node["attrs"]["decided_by"]
        return None, score, None

    def __bool__(self):
        return bool(self.items)

    def report(self):
        if not self.items:
            return "no open questions"
        lines = [f"{len(self.items)} question(s) need a human answer:"]
        for i, q in enumerate(self.items, 1):
            lines.append(f"  {i}. [{q['field']}] {q['question']}")
            if q["options"]:
                lines.append(f"     options: {q['options']}")
            if q["why"]:
                lines.append(f"     why: {q['why']}")
        return "\n".join(lines)
