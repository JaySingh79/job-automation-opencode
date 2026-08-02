"""Guard tests. No network, no credits.

Every test here corresponds to a pitfall that was paid for once on a live application.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent
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


def test_preflight_blocks_on_the_known_inconsistencies():
    rc = subprocess.run([sys.executable, str(ROOT / "preflight.py"), "--no-probe"],
                        capture_output=True, text=True, cwd=ROOT)
    assert rc.returncode == 1
    for expected in ("Symx AI", "date_granularity", "ambiguous_value"):
        assert expected in rc.stdout
