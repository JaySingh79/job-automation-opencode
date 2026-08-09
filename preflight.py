"""Pre-flight gate. Runs before any field is typed, spends no credits.

G9  resume vs profile consistency  — blocks on mismatch (user's standing decision)
G8  semantic ambiguity             — blocks on ambiguous profile keys
C4  upload host reachability       — warns, orders hosts by last-known-good

Exit codes: 0 clear, 1 blocked. `--warn-only` downgrades blockers to warnings.

    python preflight.py
    python preflight.py --warn-only
"""

import json
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "kb"))
from kb import Graph  # noqa: E402

ROOT = Path(__file__).parent
RESUME_MD = ROOT / ".firecrawl" / "resume.md"

BLOCK, WARN = "BLOCK", "warn"


def check_consistency(profile, resume_text):
    """G9. Guards against fabrication, not against staleness.

    work_ex_details.md is the authoritative work history (user's standing decision,
    2026-08-03); the resume PDF lags behind it. So a role the resume omits is expected
    and only worth flagging — blocking on it stopped every run for a normal condition.
    Invented months stay a blocker, because that is fabrication rather than lag (E3).
    """
    findings = []
    resume_norm = _norm(resume_text)

    for role in profile.get("work_experience", []):
        company = role["company"]
        on_resume = _mentions(resume_norm, company)
        if not on_resume:
            findings.append((WARN, "G9", "role_not_on_resume",
                             f"'{company}' is in user_profile.json but not in the attached resume. "
                             f"Expected when the resume lags work_ex_details.md; the recruiter sees "
                             f"a role on the form that the PDF does not mention."))

        title = role.get("title", "")
        if on_resume and title and not _mentions(resume_norm, title):
            findings.append((WARN, "G9", "title_mismatch",
                             f"'{company}': profile title '{title}' does not appear in the resume."))

        if not _has_month(role.get("dates", "")):
            findings.append((BLOCK, "G9", "date_granularity",
                             f"'{company}' dates are '{role.get('dates')}' with no month. "
                             f"Workday requires MM/YYYY, so months would be invented."))
    return findings


def check_ambiguity(profile, graph):
    """G8. Keys whose value has two opposite readings must not be auto-filled.

    An ambiguous key is cleared once the answer bank corroborates the stated value — the
    danger in E1 was an unreviewed guess, not the key existing. Nothing corroborating it,
    or a bank that disagrees, still blocks: the failure mode is a disqualifying answer.

    What this cannot check is the job's country, which preflight never sees. A value
    confirmed for one country is NOT revalidated for another, so the escalation on a
    country change stays with the human.
    """
    findings = []
    ambiguous = {p["label"]: p["attrs"].get("ambiguity", "")
                 for p in graph.query(type="profile_field") if p["attrs"].get("ambiguous")}

    for key, note in ambiguous.items():
        leaf = key.split(".")[-1]
        for section in ("screening_answers", "personal_information"):
            stated = profile.get(section, {}).get(leaf)
            if stated is None:
                continue
            bank = _bank_answer(graph, leaf)
            if bank is None:
                findings.append((BLOCK, "G8", "ambiguous_value",
                                 f"{section}.{leaf} = '{stated}' and nothing in the answer "
                                 f"bank corroborates it. {note}"))
            elif str(bank["attrs"]["value"]).lower() != str(stated).lower():
                findings.append((BLOCK, "G8", "graph_disagrees_with_profile",
                                 f"Profile says '{stated}', the answer bank says "
                                 f"'{bank['attrs']['value']}' (decided by "
                                 f"{bank['attrs']['decided_by']}). Reconcile them before "
                                 f"any field is typed — they cannot both be filled."))
            else:
                findings.append((WARN, "G8", "ambiguous_value_confirmed",
                                 f"{section}.{leaf} = '{stated}', matching the answer bank "
                                 f"(decided by {bank['attrs']['decided_by']}). Confirmed for "
                                 f"India-based roles only — re-confirm if this job is not in "
                                 f"the candidate's country of residence."))
    return findings


def _bank_answer(graph, leaf):
    """The answer-bank entry covering a profile key, matched on the key's content words."""
    words = [w for w in leaf.split("_") if len(w) > 4]
    for ans in graph.query(type="answer"):
        label = ans["label"].lower()
        if any(w in label for w in words):
            return ans
    return None


def check_hosts(graph, probe=True):
    """C4. Four hosts were burned live last time. Probe in last-known-good order."""
    findings = []
    hosts = sorted(graph.query(type="host"),
                   key=lambda h: (h["attrs"]["status"] != "ok", h["label"]))
    if not probe:
        return findings, [h["label"] for h in hosts]

    order = []
    for h in hosts:
        name = h["label"]
        rc = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-m", "12",
                             "-w", "%{http_code}", f"https://{name}/"],
                            capture_output=True, text=True).stdout.strip()
        alive = rc not in ("000", "")
        order.append(name) if alive else None
        if h["attrs"]["status"] == "ok" and not alive:
            findings.append((WARN, "C4", "host_down",
                             f"{name} was the working host but is unreachable now (curl={rc}). "
                             f"Fallback order: {[x['label'] for x in hosts if x['label'] != name]}"))
    if not order:
        findings.append((BLOCK, "C4", "no_upload_host",
                         "No upload host reachable. Resume cannot reach the cloud sandbox."))
    return findings, order


def check_resume_present(profile):
    findings = []
    if not RESUME_MD.exists():
        findings.append((BLOCK, "G9", "resume_not_parsed",
                         f"{RESUME_MD} missing. Run `firecrawl parse <resume.pdf> "
                         f"-o .firecrawl/resume.md` first — consistency cannot be checked without it."))
    local = Path(profile.get("resume_file_path", ""))
    if profile.get("resume_file_path") and not local.exists():
        candidates = list(ROOT.glob("*.pdf"))
        findings.append((WARN, "G2", "resume_path_stale",
                         f"resume_file_path points at {local}, which does not exist. "
                         f"Local PDFs found: {[c.name for c in candidates] or 'none'}"))
    return findings


# ------------------------------------------------------------------ helpers

def _norm(text):
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower())


def _mentions(resume_norm, phrase, threshold=0.86):
    """Resume text is OCR-ish and reflowed, so exact substring matching is too brittle.
    Fall back to a sliding fuzzy match over same-length windows."""
    target = _norm(phrase)
    core = target.split("(")[0].strip()
    if core and core in resume_norm:
        return True
    words = resume_norm.split()
    n = len(core.split())
    if n == 0:
        return False
    for i in range(max(0, len(words) - n + 1)):
        window = " ".join(words[i:i + n])
        if SequenceMatcher(None, core, window).ratio() >= threshold:
            return True
    return False


def _has_month(dates):
    if not dates:
        return False
    months = ("jan", "feb", "mar", "apr", "may", "jun",
              "jul", "aug", "sep", "oct", "nov", "dec")
    low = dates.lower()
    return any(m in low for m in months) or bool(re.search(r"\b\d{1,2}/\d{4}\b", dates))


# --------------------------------------------------------------------- main

def main(argv):
    warn_only = "--warn-only" in argv
    no_probe = "--no-probe" in argv

    profile = json.loads((ROOT / "user_profile.json").read_text(encoding="utf-8"))
    graph = Graph()
    resume_text = RESUME_MD.read_text(encoding="utf-8") if RESUME_MD.exists() else ""

    findings = []
    findings += check_resume_present(profile)
    if resume_text:
        findings += check_consistency(profile, resume_text)
    findings += check_ambiguity(profile, graph)
    host_findings, order = check_hosts(graph, probe=not no_probe)
    findings += host_findings

    blockers = [f for f in findings if f[0] == BLOCK]
    warnings = [f for f in findings if f[0] == WARN]

    print("=" * 72)
    print("PRE-FLIGHT")
    print("=" * 72)
    for level, guard, kind, msg in blockers + warnings:
        tag = "BLOCK" if level == BLOCK else " warn"
        print(f"[{tag}] {guard} {kind}\n        {msg}")
    if not findings:
        print("clear — no blockers, no warnings")
    if order:
        print(f"\nupload host order: {' > '.join(order)}")

    print(f"\n{len(blockers)} blocker(s), {len(warnings)} warning(s)")
    if blockers and not warn_only:
        print("\nRun blocked. Reconcile the items above, or re-run with --warn-only to override.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
