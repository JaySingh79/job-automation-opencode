"""Guard tests. No network, no credits.

Every test here corresponds to a pitfall that was paid for once on a live application.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent   # tests live in testing_files/, code at repo root
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "kb"))

import guards as G          # noqa: E402
from kb import Graph        # noqa: E402

GUARDS = G.load()


# ------------------------------------------------------------------ D1 sanitizer

@pytest.mark.parametrize("ch", ["<", ">", "[", "]", "{", "}", '"', chr(92)])
def test_sanitizer_strips_every_illegal_char(ch):
    assert ch not in G.sanitize(f"before{ch}after", GUARDS)


def test_sanitizer_rewrites_comparisons_instead_of_deleting_them():
    # ">90% accuracy" must survive as a claim, not become "90% accuracy"
    assert G.sanitize(">90% alignment accuracy", GUARDS) == "over 90% alignment accuracy"
    assert G.sanitize("<2s latency", GUARDS) == "under 2s latency"


def test_sanitizer_handles_the_exact_text_that_failed():
    original = ('Eliminated the "black box" problem — >90% accuracy across 7+ years')
    out = G.sanitize(original, GUARDS)
    assert not any(c in out for c in GUARDS["constraints"]["constraint:illegal_chars"]["chars"])
    assert "over 90%" in out
    assert "black box" in out          # content preserved, only the quotes go


# ------------------------------------------------------------------ D2 linkedin

def test_linkedin_without_www_is_rejected_and_autofixed():
    ok, fixed, msg = G.validate("field:social.linkedin",
                                "https://linkedin.com/in/jay-singh-ds/", GUARDS)
    assert ok and fixed == "https://www.linkedin.com/in/jay-singh-ds/"
    assert "www" in msg


def test_linkedin_with_www_passes_untouched():
    ok, fixed, _ = G.validate("field:social.linkedin",
                              "https://www.linkedin.com/in/jay-singh-ds/", GUARDS)
    assert ok and fixed == "https://www.linkedin.com/in/jay-singh-ds/"


def test_unfixable_url_is_rejected():
    ok, _, msg = G.validate("field:social.linkedin", "jay-singh-ds", GUARDS)
    assert not ok and "Invalid LinkedIn URL" in msg


# ------------------------------------------------------------------ A1 / G1

def test_terminal_step_refuses_without_explicit_override(monkeypatch):
    monkeypatch.delenv("ALLOW_SUBMIT", raising=False)
    with pytest.raises(G.SubmitBoundary) as e:
        G.terminal_step_guard(GUARDS["terminal_submit_step"], GUARDS, scrape_id="abc")
    assert "irreversibly" in str(e.value)
    assert "abc" in str(e.value)          # hands the human the exact command


def test_non_terminal_steps_pass(monkeypatch):
    monkeypatch.delenv("ALLOW_SUBMIT", raising=False)
    assert G.terminal_step_guard(1, GUARDS) is True


def test_unknown_terminal_step_is_treated_as_destructive():
    with pytest.raises(G.SubmitBoundary):
        G.terminal_step_guard(3, {"terminal_submit_step": None})


def test_human_override_is_honoured(monkeypatch):
    monkeypatch.setenv("ALLOW_SUBMIT", "1")
    assert G.terminal_step_guard(GUARDS["terminal_submit_step"], GUARDS) is True


# ------------------------------------------------------------------ A2 / G2

def test_upload_probe_asserts_magic_and_size():
    sh = G.upload_probe("https://tmpfiles.org/dl/x/y.pdf", "R.pdf", 123239)
    assert '"%PDF-"' in sh
    assert "123239" in sh
    assert "G2_FAIL" in sh
    assert "curl" in sh and "urllib" not in sh      # urllib gets 403 from tmpfiles


def test_verify_upload_rejects_the_html_page_that_slipped_through():
    with pytest.raises(G.UploadIntegrityError):
        G.verify_upload("G2_FAIL: not a PDF (got <!DOC)", "Jay_Singh_Resume.pdf")


def test_verify_upload_rejects_missing_success_confirmation():
    with pytest.raises(G.UploadIntegrityError):
        G.verify_upload("Jay_Singh_Resume.pdf 120.35 KB", "Jay_Singh_Resume.pdf")


def test_verify_upload_accepts_the_real_confirmation():
    out = '"Jay_Singh_Resume.pdf 120.35 KB Successfully Uploaded!"'
    assert G.verify_upload(out, "Jay_Singh_Resume.pdf")["reported_kb"] == 120.35


# ------------------------------------------------------------------ D7 / G7

def test_option_resolver_uses_a_known_alias():
    choice, score, alias = G.resolve_option(
        "Mobile", ["Home", "Personal Mobile"], GUARDS["option_aliases"])
    assert (choice, alias) == ("Personal Mobile", True)


def test_option_resolver_refuses_to_guess_between_degrees():
    # Bachelor's vs Master's is exactly the kind of miss that must not be silent
    choice, score, _ = G.resolve_option("PhD", ["Bachelor's Degree", "Master's Degree"])
    assert choice is None and score < G.OPTION_FLOOR


def test_option_resolver_exact_match_short_circuits():
    assert G.resolve_option("Home", ["Home", "Personal Mobile"])[0] == "Home"


# ------------------------------------------------------------------ D3 / G6

def test_error_harvest_finds_what_the_dom_hides():
    page = ("Role Description\n"
            "Error: Contains illegal characters < > [ ] \" { } \\\n"
            "LinkedIn\nError: Invalid LinkedIn URL\nSave and Continue")
    errs = G.harvest_errors(page)
    assert len(errs) == 2
    assert any("illegal characters" in e for e in errs)


# ------------------------------------------------------------------ D9 / G11

def test_honeypot_is_recognised():
    assert G.is_honeypot("Enter website. This input is for robots only, "
                         "do not enter if you're human.")
    assert not G.is_honeypot("LinkedIn")


def test_attestation_is_recognised():
    assert G.is_attestation("Yes, I have read and consent to the Terms & Conditions above.")
    assert G.is_attestation("I verify that all of the information is true")
    assert not G.is_attestation("Phone Number")


# ------------------------------------------------------------------ answer bank

def test_find_answer_matches_a_reworded_question():
    g = Graph()
    node, score = g.find_answer(
        "Will you now or in the future require visa sponsorship "
        "within the country for which you are applying?")
    assert node is not None and node["attrs"]["value"] == "No"
    assert node["attrs"]["decided_by"] == "user"      # provenance survives


def test_find_answer_matches_a_shorter_rewording_from_another_ats():
    """The compounding claim: the same question asked briefly elsewhere still resolves."""
    g = Graph()
    node, score = g.find_answer(
        "Will you now or in the future require visa sponsorship for employment?")
    assert node is not None and node["attrs"]["value"] == "No"


def test_find_answer_declines_an_unrelated_question():
    g = Graph()
    node, score = g.find_answer("What is your expected annual compensation?")
    assert node is None


def test_employer_specific_answers_do_not_leak_to_another_company():
    """'Are you currently employed by Gartner?' scores 0.90 against the Acme version.
    Answering Acme's form from Gartner's entry would be a factual error."""
    g = Graph()
    node, _ = g.find_answer("Are you currently employed by Acme?",
                            tenant="tenant:acme.greenhouse.io")
    assert node is None


def test_employer_specific_answers_still_resolve_on_their_own_tenant():
    g = Graph()
    node, _ = g.find_answer("Are you currently employed by Gartner?",
                            tenant="tenant:gartner.wd5/EXT")
    assert node is not None and node["attrs"]["value"] == "No"


def test_generic_answers_transfer_to_any_tenant():
    g = Graph()
    node, _ = g.find_answer(
        "Will you now or in the future require visa sponsorship for employment?",
        tenant="tenant:acme.greenhouse.io")
    assert node is not None and node["attrs"]["value"] == "No"


# ------------------------------------------------------------------ G5 queue

def test_question_queue_collects_instead_of_blocking():
    q = G.QuestionQueue()
    assert not q
    q.ask("q.salary", "Expected compensation?", why="not in profile")
    assert q and "Expected compensation?" in q.report()


# ------------------------------------------------------------------ projection

def test_projection_round_trips_the_handwritten_map():
    handwritten = ROOT / ".firecrawl" / "field_map.handwritten.json"
    if not handwritten.exists():
        pytest.skip("no handwritten baseline to compare against")
    old = json.loads(handwritten.read_text(encoding="utf-8"))
    new = json.loads((ROOT / "field_map.json").read_text(encoding="utf-8"))

    def aids(fm):
        out = {}
        for v in fm["fields"].values():
            if not isinstance(v, dict):
                continue
            a = v.get("automation_id") or v.get("aid")
            if not a and "data-automation-id='" in v.get("selector", ""):
                a = v["selector"].split("data-automation-id='")[1].split("'")[0]
            if a:
                out[a] = v.get("value")
        return out

    o, n = aids(old), aids(new)
    assert not set(o) - set(n), f"projection lost: {sorted(set(o) - set(n))}"
    assert not {k: (o[k], n[k]) for k in set(o) & set(n) if o[k] != n[k]}


def test_projected_guards_know_the_submit_boundary():
    assert GUARDS["terminal_submit_step"] == 4
    assert "constraint:illegal_chars" in GUARDS["constraints"]
    assert GUARDS["upload_hosts"][0]["status"] == "ok"       # best host first


# ------------------------------------------------------------------ accumulation

def test_harvest_grows_shared_layers_without_touching_tenant_selectors(tmp_path, monkeypatch):
    """A second application on a different ATS must reuse the canonical field and
    answer layers while leaving the Workday selector subtree alone."""
    import kb as kbmod
    import harvest as hv

    scratch = tmp_path / "graph.json"
    scratch.write_text((ROOT / "kb" / "graph.json").read_text(encoding="utf-8"),
                       encoding="utf-8")
    monkeypatch.setattr(kbmod, "GRAPH", scratch)
    monkeypatch.setattr(kbmod, "EVENTS", tmp_path / "events.jsonl")

    before = json.loads(scratch.read_text(encoding="utf-8"))
    hv.harvest(ROOT / "runs" / "example-greenhouse.json")
    after = json.loads(scratch.read_text(encoding="utf-8"))

    bn = {n["id"] for n in before["nodes"]}
    an = {n["id"] for n in after["nodes"]}
    assert len(an) > len(bn)

    wd = lambda nodes: {n["id"] for n in nodes
                        if n["id"].startswith("selector:tenant:gartner")}
    assert wd(before["nodes"]) == wd(after["nodes"]), "tenant selector layer must not move"

    assert any(n["id"].startswith("selector:tenant:acme") for n in after["nodes"])

    reused = [n for n in after["nodes"]
              if n["type"] == "field" and len(n["applications"]) > 1]
    assert {n["id"] for n in reused} >= {"field:identity.first_name", "field:social.linkedin"}


def test_harvest_links_a_reworded_question_to_the_original(tmp_path, monkeypatch):
    import kb as kbmod
    import harvest as hv

    scratch = tmp_path / "graph.json"
    scratch.write_text((ROOT / "kb" / "graph.json").read_text(encoding="utf-8"),
                       encoding="utf-8")
    monkeypatch.setattr(kbmod, "GRAPH", scratch)
    monkeypatch.setattr(kbmod, "EVENTS", tmp_path / "events.jsonl")

    hv.harvest(ROOT / "runs" / "example-greenhouse.json")
    after = json.loads(scratch.read_text(encoding="utf-8"))
    links = [e for e in after["edges"]
             if e["rel"] == "maps_to" and e["from"].startswith("answer:")]
    assert links, "reworded sponsorship question should point at the original"
    assert all(e["attrs"]["similarity"] >= kbmod.THRESHOLD for e in links)


def test_preflight_passes_once_the_inconsistencies_are_reconciled():
    rc = subprocess.run([sys.executable, str(ROOT / "preflight.py"), "--no-probe"],
                        capture_output=True, text=True, cwd=ROOT)
    assert rc.returncode == 0, rc.stdout
    assert "0 blocker(s)" in rc.stdout


# --------------------------------------------------- G9: fabrication vs staleness

def test_role_missing_from_the_resume_only_warns():
    """work_ex_details.md is the authoritative history and the resume PDF lags it, so a
    role the resume omits is expected. Blocking on it stopped every run."""
    import preflight as P
    profile = {"work_experience": [
        {"company": "Symx AI", "title": "Data Scientist", "dates": "Sep 2024 - Feb 2025"}]}
    findings = P.check_consistency(profile, "Innovaccer  Pibit AI  Cambridge Judge")
    kinds = {(level, kind) for level, _, kind, _ in findings}
    assert (P.WARN, "role_not_on_resume") in kinds
    assert not [f for f in findings if f[0] == P.BLOCK]


def test_year_only_dates_still_block():
    """E3: 'Symx AI months are absent — assumed Jan 2024 to Dec 2025' reached a submitted
    application. Inventing a month is fabrication, not lag, so it stays a blocker."""
    import preflight as P
    profile = {"work_experience": [
        {"company": "Symx AI", "title": "Data Scientist", "dates": "2024 - 2025"}]}
    blocks = [f for f in P.check_consistency(profile, "Symx AI") if f[0] == P.BLOCK]
    assert [f[2] for f in blocks] == ["date_granularity"]


# --------------------------------------------------------------- G8 reconciliation

def test_ambiguous_value_clears_when_the_answer_bank_agrees():
    import preflight as P
    profile = {"screening_answers": {"work_authorization_sponsorship": "No"}}
    findings = P.check_ambiguity(profile, Graph())
    assert not [f for f in findings if f[0] == P.BLOCK]
    assert any(kind == "ambiguous_value_confirmed" for _, _, kind, _ in findings)


def test_ambiguous_value_blocks_when_the_answer_bank_disagrees():
    """The two cannot both be filled, and 'Yes' here is the disqualifying answer (E1)."""
    import preflight as P
    profile = {"screening_answers": {"work_authorization_sponsorship": "Yes"}}
    blocks = [f for f in P.check_ambiguity(profile, Graph()) if f[0] == P.BLOCK]
    assert [f[2] for f in blocks] == ["graph_disagrees_with_profile"]


# ------------------------------------------------------------- E3 date parsing

@pytest.mark.parametrize("text,expected", [
    ("Sep 2024 - Feb 2025", (9, 2024, 2, 2025)),
    ("Dec 2024 - Apr 2025", (12, 2024, 4, 2025)),
    ("May 2023 - Sep 2023", (5, 2023, 9, 2023)),
])
def test_dates_parse_from_the_profile(text, expected):
    import apply_orchestrator as A
    assert A.parse_dates(text) == expected


def test_a_missing_month_raises_instead_of_being_invented():
    import apply_orchestrator as A
    with pytest.raises(ValueError, match="no month"):
        A.parse_dates("2024 - 2025")


def test_every_profile_role_reaches_the_form():
    """Entries are not filtered against the resume — that would silently drop real roles."""
    import apply_orchestrator as A
    profile = json.loads((ROOT / "user_profile.json").read_text(encoding="utf-8"))
    entries = A.build_entries(profile)
    assert len(entries) == len(profile["work_experience"])
    assert [e["company"] for e in entries][0:2] == ["Pibit AI (YC W21)", "Pascal AI Labs"]


# ------------------------------------------------------- G2 across both drivers

def test_upload_probe_targets_the_tenants_own_file_input():
    """Phenom has no data-automation-id; the Workday default must stay the default."""
    wd = G.upload_probe("https://tmpfiles.org/dl/x/y.pdf", "R.pdf", 10)
    ph = G.upload_probe("https://tmpfiles.org/dl/x/y.pdf", "R.pdf", 10,
                        file_input="input[type=file]", confirm="[class*=upload]")
    assert "file-upload-input-ref" in wd and "input[type=file]" not in wd
    assert "input[type=file]" in ph and "file-upload-input-ref" not in ph
    for sh in (wd, ph):
        assert '"%PDF-"' in sh and "G2_FAIL" in sh      # integrity survives the swap


def test_upload_verification_survives_a_tenant_without_workdays_wording():
    out = '"Jay_Singh_Resume.pdf 120.35 KB"'
    assert G.verify_upload(out, "Jay_Singh_Resume.pdf", success_marker="")["reported_kb"] == 120.35
    with pytest.raises(G.UploadIntegrityError):
        G.verify_upload("G2_FAIL: size 2600 != 123239", "Jay_Singh_Resume.pdf",
                        success_marker="")
