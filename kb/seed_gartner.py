"""One-shot seeder: fold the 2026-08-02 Gartner run into the memory graph.

Run once. Re-running is idempotent (add_node/add_edge merge rather than duplicate).
Everything here was observed live; nothing is speculative.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kb import Graph, log_event  # noqa: E402

DAY = "2026-08-02"
APP = "app:gartner-110911"
ATS = "ats:workday"
TEN = "tenant:gartner.wd5/EXT"

g = Graph()
N = lambda *a, **k: g.add_node(*a, seen=DAY, app=APP, **k)
E = lambda *a, **k: g.add_edge(*a, app=APP, **k)


# ----------------------------------------------------------------- guards

GUARDS = [
    ("G1", "terminal-step guard",
     "Before any continue click, resolve is_terminal_submit for the step. If true, refuse: "
     "dump footer buttons and progress bar, print the submit one-liner, exit. ALLOW_SUBMIT=1 is "
     "the only override and automation never sets it."),
    ("G2", "upload integrity",
     "Assert magic bytes match the declared type, byte count equals the local source, filename is "
     "distinct and candidate-named, and the post-upload DOM shows success plus the expected size. "
     "Abort on any mismatch."),
    ("G4", "session batching",
     "One batched interact call per form step. Firecrawl live sessions die after ~10 min idle."),
    ("G5", "no blocking question with an open session",
     "Never pause for a human answer while a session is live. Resolve from the answer bank, or "
     "finish every other field and ask at the end."),
    ("G6", "error harvest",
     "After every save, grep page innerText for lines starting with 'Error'. Workday does not put "
     "validation text in errorMessage or role=alert. Any new error becomes a constraint node."),
    ("G7", "option resolver",
     "Never type a value into a dropdown. Enumerate the field's own options, fuzzy-match, record a "
     "maps_to edge. Below the similarity floor, queue a question."),
    ("G8", "semantic ambiguity guard",
     "Profile keys marked ambiguous, or whose value conflicts with the job's country, escalate "
     "before any field is typed."),
    ("G9", "resume/profile consistency pre-flight",
     "Diff parsed resume against user_profile.json. Any role, title or date-granularity mismatch "
     "blocks the run until reconciled."),
    ("G10", "credit measurement",
     "Measure unit cost over at least 5 calls before extrapolating. A single 0-delta reading is noise."),
    ("G11", "attestation guard",
     "Fields matching /e-?signature|certify|I verify|consent/i are classed attestation: filled only "
     "under the hard-stop flow and listed explicitly in the handover report."),
    ("G12", "profile writer lock",
     "One writer per browser profile. Concurrent readers must pass --no-save-changes."),
]
for gid, label, desc in GUARDS:
    N(f"guard:{gid}", "guard", label, description=desc)


# ----------------------------------------------------------------- pitfalls

PITFALLS = [
    # (id, severity, what happened, guard)
    ("A1", "fatal", "Application submitted with no human review: 'Save and Continue' on step 4 of 5 "
     "WAS the submit. The progress bar's step 5 'Review' is a post-submit confirmation screen.", "G1"),
    ("A2", "fatal", "Resume uploaded as a 2.6 KB HTML error page named resume.pdf. Workday accepted "
     "it silently. Magic bytes were never checked.", "G2"),
    ("A3", "high", "T&C e-signature checkbox ticked automatically. It attests the application is true "
     "and complete.", "G11"),

    ("B1", "medium", "Live session died after ~10 min idle; two sessions lost mid-run.", "G4"),
    ("B2", "medium", "Asked the human a question with a live session open. Session died, costing a "
     "reconnect and a step re-walk.", "G5"),
    ("B3", "low", "Concluded interact was free from one 0-delta credit reading. Actual ~2 credits/call.", "G10"),
    ("B4", "low", "'Another session is currently writing to this profile' when two scrapes shared "
     "--profile.", "G12"),

    ("C1", "medium", "tmpfiles.org /dl/<id>/<name> returns HTML, not the file. The real link is a "
     "tokenized href inside that page.", "G2"),
    ("C2", "high", "The tmpfiles token is IP-bound. Resolved locally it yields HTML in the cloud "
     "sandbox. Must be resolved inside the sandbox.", "G2"),
    ("C3", "medium", "urllib from the Python sandbox gets HTTP 403 from tmpfiles. curl from the bash "
     "sandbox works.", "G2"),
    ("C4", "low", "Four upload hosts burned before one worked: file.io dead, 0x0.st unreachable, "
     "litterbox 403, bashupload DNS failure.", "G2"),
    ("C5", "medium", "Two uploads with the same filename were indistinguishable; could not tell which "
     "one landed.", "G2"),

    ("D1", "high", "Role Description rejects < > [ ] { } \" and backslash: 'Contains illegal characters'. "
     "Discovered only after a failed save.", "G6"),
    ("D2", "medium", "LinkedIn URL must contain www. 'https://linkedin.com/in/...' is rejected with "
     "'Invalid LinkedIn URL'.", "G6"),
    ("D3", "high", "Validation errors are NOT in errorMessage or role=alert. aria-invalid=true elements "
     "have empty text. Only reliable read is innerText lines starting with 'Error'.", "G6"),
    ("D4", "medium", "Searchable prompts do not filter when you type into the field: they return the "
     "first 100 alphabetically. Must use promptSearchButton then the Search box then Enter.", "G7"),
    ("D5", "low", "promptOption matched a different widget's options than intended. Enumeration must be "
     "scoped to the field's own container.", "G7"),
    ("D6", "low", "data-automation-id sits on wrapper DIVs, not on inputs. Must descend to input/textarea/button.", "G7"),
    ("D7", "medium", "Option label mismatches: Mobile -> Personal Mobile, Computer Science -> Computer "
     "and Information Science, B.Tech -> Bachelor's Degree.", "G7"),
    ("D8", "low", "agent-browser snapshot refs go stale after any DOM change. Refs for reading, "
     "automation-ids for acting.", "G7"),
    ("D9", "high", "Honeypot input present: 'Enter website. This input is for robots only, do not enter "
     "if you're human.' Filling it flags the application as a bot.", "G7"),
    ("D10", "low", "Several add-buttons share one automation-id, separated only by nth index.", "G7"),
    ("D11", "low", "candidateHome renders a phantom '1 error' banner after a direct goto. Benign.", "G6"),

    ("E1", "fatal", "work_authorization_sponsorship: 'Yes' is semantically ambiguous. Taken literally it "
     "would have submitted a disqualifying answer for an India-based role.", "G8"),
    ("E2", "high", "Symx AI is in work_ex_details.md but not on the attached resume PDF. Now permanent "
     "on a live application.", "G9"),
    ("E3", "medium", "Symx AI dates had no months ('2024 - 2025'); months were invented as 01/2024-12/2025.", "G9"),
    ("E4", "low", "Cambridge title differs: profile 'Research Associate' vs resume 'Research Apprenticeship'.", "G9"),

    ("F1", "medium", "The DRY_RUN gate the plan mandated was skipped; the run was driven ad hoc.", "G1"),
    ("F2", "low", "apply_orchestrator.py was written after the run it was meant to drive.", "G1"),
    ("F3", "medium", "Sanitization was designed only after the server rejected the input.", "G6"),
]
for pid, sev, what, guard in PITFALLS:
    N(f"pitfall:{pid}", "pitfall", what, severity=sev)
    E(f"pitfall:{pid}", f"guard:{guard}", "prevented_by")
    E(f"pitfall:{pid}", APP, "observed_in")


# --------------------------------------------------------- ATS and tenant

N(ATS, "ats", "Workday", vendor="Workday, Inc.")
N(TEN, "tenant", "Gartner EXT", host="gartner.wd5.myworkdayjobs.com",
  site="EXT", auth="email/password, no verification interstitial",
  entry_choices=["Autofill with Resume", "Apply Manually", "Use My Last Application"],
  chosen_entry="Apply Manually")
E(ATS, TEN, "has_tenant")

# Constraints belong to the ATS product, not the tenant: every Workday shares them.
N("constraint:illegal_chars", "constraint", "Free-text rejects < > [ ] { } \" backslash",
  applies_to="free_text", chars=["<", ">", "[", "]", "{", "}", '"', chr(92)],
  error="Contains illegal characters",
  rewrites={">N": "over N", "<N": "under N"})
N("constraint:linkedin_www", "constraint", "LinkedIn URL must contain www.",
  applies_to="field:social.linkedin", regex=r"^https://www\.linkedin\.com/in/",
  error="Invalid LinkedIn URL", autofix="insert www. after https://")
N("constraint:error_readback", "constraint", "Validation errors readable only via innerText",
  applies_to="page", recipe="grep page innerText for lines starting with 'Error'")
for c in ("constraint:illegal_chars", "constraint:linkedin_www", "constraint:error_readback"):
    E(ATS, c, "constrained_by")

STEPS = [
    (0, "Sign In", False),
    (1, "My Information", False),
    (2, "My Experience", False),
    (3, "Application Questions", False),
    (4, "Voluntary Disclosures", True),   # <-- the submit
    (5, "Review", False),                 # post-submit confirmation only
]
for num, name, terminal in STEPS:
    sid = f"step:{TEN}#{num}"
    N(sid, "step", name, index=num, is_terminal_submit=terminal,
      note=("continue on this step SUBMITS the application" if terminal else
            "post-submit confirmation screen, not a review page" if num == 5 else ""))
    E(TEN, sid, "has_step")
    if terminal:
        E(sid, "guard:G1", "is_terminal_submit")


# --------------------------------------------------- canonical fields

# (canonical id, label, step, selector automation-id, interaction, value, profile key)
FIELDS = [
    ("auth.email", "Email Address", 0, "email", "text_bare",
     None, "credentials.workday.email"),
    ("auth.password", "Password", 0, "password", "password_bare",
     None, "credentials.workday.password"),
    ("auth.submit", "Sign In submit", 0, "signInSubmitButton", "button_bare", None, None),
    ("control.next", "Save and Continue", 0, "pageFooterNextButton", "button_bare",
     None, None),
    ("control.back", "Back", 0, "pageFooterBackButton", "button_bare", None, None),
    ("control.add_another", "Add Another", 2, "add-button", "button_indexed", None, None),
    ("identity.first_name", "Given Name(s)", 1, "formField-legalName--firstName", "text",
     "Jay", "personal_information.first_name"),
    ("identity.last_name", "Family Name", 1, "formField-legalName--lastName", "text",
     "Singh", "personal_information.last_name"),
    ("address.line1", "Address Line 1", 1, "formField-addressLine1", "text",
     "Gaya", "personal_information.address_line_1"),
    ("address.city", "City", 1, "formField-city", "text", "Gaya", "personal_information.city"),
    ("address.postal_code", "Postal Code", 1, "formField-postalCode", "text",
     "823001", "personal_information.postal_code"),
    ("address.country", "Country", 1, "formField-country", "prompt_dropdown",
     "India", "personal_information.country"),
    ("phone.device_type", "Phone Device Type", 1, "formField-phoneType", "prompt_dropdown",
     "Personal Mobile", None),
    ("phone.country_code", "Country Phone Code", 1, "formField-countryPhoneCode", "multiselect",
     "India (+91)", None),
    ("phone.number", "Phone Number", 1, "formField-phoneNumber", "text",
     "8651274328", "personal_information.phone"),
    ("phone.sms_opt_in", "SMS opt-in", 1, "phone-sms-opt-in", "checkbox", "UNCHECKED", None),
    ("history.previous_employee", "Have you previously worked for this organization?", 1,
     "formField-candidateIsPreviousWorker", "radio", "No (index 1)", None),
    ("work.title", "Job Title", 2, "formField-jobTitle", "text_indexed", None, "work_experience[].title"),
    ("work.company", "Company", 2, "formField-companyName", "text_indexed", None, "work_experience[].company"),
    ("work.location", "Location", 2, "formField-location", "text_indexed", None, "work_experience[].location"),
    ("work.start_date", "From", 2, "formField-startDate", "date_mm_yyyy", None, "work_experience[].dates"),
    ("work.end_date", "To", 2, "formField-endDate", "date_mm_yyyy", None, "work_experience[].dates"),
    ("work.description", "Role Description", 2, "formField-roleDescription", "textarea_indexed",
     None, "work_experience[].bullets"),
    ("education.school", "School or University", 2, "formField-schoolName", "text",
     "Indian Institute of Technology Kharagpur", "education[].institution"),
    ("education.degree", "Degree", 2, "formField-degree", "prompt_dropdown",
     "Bachelor's Degree", "education[].degree"),
    ("education.field_of_study", "Field of Study", 2, "formField-fieldOfStudy", "searchable_prompt",
     "Computer and Information Science", "education[].field_of_study"),
    ("attachment.resume", "Resume/CV", 2, "file-upload-input-ref", "file",
     "Jay_Singh_Resume.pdf (120.35 KB)", "resume_file_path"),
    ("social.linkedin", "LinkedIn", 2, "formField-linkedInAccount", "text",
     "https://www.linkedin.com/in/jay-singh-ds/", "personal_information.linkedin"),
    ("legal.terms_accept", "Terms & Conditions consent", 4, "formField-acceptTermsAndAgreements",
     "attestation_checkbox", "CHECKED", None),
]

INTERACTION_RECIPES = {
    "prompt_dropdown": "click the wrapper's button, wait, click get_by_role('option', name=X, exact=True)",
    "searchable_prompt": "click promptSearchButton, click placeholder='Search', type, press Enter, "
                         "click the returned option. Typing in the field itself does NOT filter.",
    "date_mm_yyyy": "fill dateSectionMonth-input (zero-padded) then dateSectionYear-input",
    "text_indexed": "locator(wrapper).nth(i).locator('input')",
    "textarea_indexed": "locator(wrapper).nth(i).locator('textarea')",
    "multiselect": "pre-populated from country; verify rather than set",
    "attestation_checkbox": "e-signature — G11 applies",
    "text_bare": "automation-id is on the input itself, not a wrapper",
    "password_bare": "automation-id is on the input itself; never log the value",
    "button_bare": "automation-id is on the button itself",
    "button_indexed": "several buttons share this automation-id: nth(0)=Work Experience, "
                      "nth(1)=Education, nth(2)=Languages",
}

for fid, label, step, aid, interaction, value, pkey in FIELDS:
    node = f"field:{fid}"
    N(node, "field", label, canonical=fid)
    E(f"step:{TEN}#{step}", node, "has_field")

    sel = f"selector:{TEN}#{aid}"
    N(sel, "selector", aid, automation_id=aid, interaction=interaction,
      recipe=INTERACTION_RECIPES.get(interaction, "wrapper DIV holds the automation-id; descend to the control"),
      value_used=value)
    E(node, sel, "located_by")

    if pkey:
        N(f"profile_field:{pkey}", "profile_field", pkey)
        E(node, f"profile_field:{pkey}", "maps_to")

# Option vocabularies actually offered, plus the mismatches that forced a mapping.
OPTIONS = {
    "field:phone.device_type": (["Home", "Personal Mobile"], {"Mobile": "Personal Mobile"}),
    "field:education.degree": (
        ["Other", "None", "GED", "High School", "Associate's Degree", "Bachelor's Degree",
         "Master's Degree", "Juris Doctor", "Doctor of Medicine", "Doctorate", "University",
         "Honours", "Diploma"],
        {"Bachelor of Technology (B.Tech)": "Bachelor's Degree"}),
    "field:education.field_of_study": (
        ["Computer and Information Science"],
        {"Computer Science / Data Science": "Computer and Information Science"}),
}
for fid, (opts, mismatches) in OPTIONS.items():
    for o in opts:
        oid = f"option:{o}"
        N(oid, "option", o)
        E(fid, oid, "accepts_option")
    for wanted, actual in mismatches.items():
        N(f"option:{wanted}", "option", wanted, exists_in_ats=False)
        E(f"option:{wanted}", f"option:{actual}", "maps_to",
          reason="requested value absent from this ATS; nearest offered option")

# Profile data this tenant never asked for — not data loss, just absent demand.
for pkey in ["personal_information.state", "personal_information.github",
             "screening_answers.notice_period", "screening_answers.earliest_start_date",
             "screening_answers.source", "education[].coursework", "skills"]:
    N(f"profile_field:{pkey}", "profile_field", pkey)
    E(TEN, f"profile_field:{pkey}", "not_asked")

N("profile_field:screening_answers.work_authorization_sponsorship", "profile_field",
  "work_authorization_sponsorship", ambiguous=True,
  ambiguity="'Yes' could mean 'I am authorized' or 'I need sponsorship'. Opposite meanings, "
            "opposite outcomes. Never fill without confirming against the job's country.")


# ---------------------------------------------------------- answer bank

ANSWERS = [
    ("Are you currently being considered for a job or have you recently applied at Gartner?",
     "No", "high", "agent", "No other active application for this account at fill time."),
    ("Are you currently employed by Gartner?",
     "No", "high", "agent", "No Gartner role in profile or resume."),
    ("Has Gartner employed you in the past?",
     "No", "high", "agent", "No Gartner role in work history."),
    ("Will you, now or in the future, require Visa/Sponsorship within the country for which you are applying?",
     "No", "high", "user", "Profile said 'Yes' but the role is in Gurgaon, India and the candidate is "
     "an Indian citizen. Escalated; user chose No."),
    ("Are you currently a Gartner license user?",
     "No", "high", "agent", "Student/intern history; no research subscription."),
    ("In your current role, are you involved in procuring, negotiating, approving, or influencing "
     "contracts or expenditures for Gartner services?",
     "No", "high", "agent", "Individual-contributor intern roles; no procurement authority."),
    ("Are you currently subject to a non-competition or non-solicitation agreement that could impact "
     "future employment?",
     "No", "medium", "agent", "No non-compete recorded in profile. Assumed none."),
    ("Have you previously worked for this organization?",
     "No", "high", "agent", "No Gartner role in work history."),
    ("Yes, I have read and consent to the Terms & Conditions above.",
     "CHECKED", "high", "agent", "Required to proceed. E-signature — G11 applies."),
]
for question, value, conf, who, why in ANSWERS:
    aid = f"answer:{question[:60]}"
    N(aid, "answer", question, confidence=conf, value=value, decided_by=who, reasoning=why)
    E(aid, APP, "observed_in")
    if who == "user":
        E(aid, "guard:G8", "prevented_by")

# Screening automation-ids are per-requisition GUIDs, so they belong on the answer->tenant
# edge, not on the answer itself. The answer text is what transfers to the next employer.
SCREENING_AIDS = {
    "Are you currently being considered for a job or have you recently applied at Gartner?":
        "formField-f05acb97f85d10014e58303374460000",
    "Are you currently employed by Gartner?":
        "formField-f05acb97f85d10014e58303374460004",
    "Has Gartner employed you in the past?":
        "formField-f05acb97f85d10014e5830cd6bfc0002",
    "Will you, now or in the future, require Visa/Sponsorship within the country for which you are applying?":
        "formField-f05acb97f85d10014e5830cd6bfc0005",
    "Are you currently a Gartner license user?":
        "formField-f05acb97f85d10014e5831683c390001",
    "In your current role, are you involved in procuring, negotiating, approving, or influencing "
    "contracts or expenditures for Gartner services?":
        "formField-f05acb97f85d10014e5831683c390004",
    "Are you currently subject to a non-competition or non-solicitation agreement that could impact "
    "future employment?":
        "formField-f05acb97f85d10014e58320207550001",
}
for question, aid in SCREENING_AIDS.items():
    employer_specific = "Gartner" in question
    g.add_edge(f"answer:{question[:60]}", TEN, "observed_in", app=APP,
               aid=aid, requisition="110911", employer_specific=employer_specific)


# --------------------------------------------------------------- hosts

HOSTS = [
    ("tmpfiles.org", "ok", DAY, None,
     "POST file to https://tmpfiles.org/api/v1/upload. The returned /dl/<id>/<name> URL serves HTML, "
     "not the file: fetch that page INSIDE the sandbox and grep the tokenized href "
     "https://tmpfiles.org/dl/<epoch>.<hex>/<id>/<name>. Token is IP-bound. Use curl, not urllib "
     "(urllib gets 403). Expires ~60 min."),
    ("file.io", "fail", None, DAY, "Returns a Gatsby HTML landing page; free upload API discontinued."),
    ("0x0.st", "fail", None, DAY, "Connection timeout from this network."),
    ("litterbox.catbox.moe", "fail", None, DAY, "403 Forbidden on the upload endpoint."),
    ("bashupload.com", "fail", None, DAY, "DNS resolution failure."),
]
for host, status, ok, fail, recipe in HOSTS:
    N(f"host:{host}", "host", host, status=status, last_ok=ok, last_fail=fail, fetch_recipe=recipe)


# ----------------------------------------------------------- tool facts

FACTS = [
    ("firecrawl.session_ttl", "Firecrawl live sessions expire after roughly 10 minutes idle."),
    ("firecrawl.interact_cost", "interact costs ~2 credits per call. Measured over the whole run: "
     "66 credits for 4 scrapes + 1 parse + ~30 interacts."),
    ("firecrawl.scrape_cost", "scrape = 1 credit. parse = ~1 credit per PDF page. --query = +5."),
    ("firecrawl.profile_lock", "One writer per --profile at a time. Readers need --no-save-changes."),
    ("firecrawl.sandbox_net", "The bash sandbox has outbound internet and a writable /tmp. curl works; "
     "urllib from the python sandbox is blocked by some hosts (403)."),
    ("firecrawl.sandbox_upload", "agent-browser upload <selector> <path> puts a sandbox file into a "
     "page file input. Playwright set_input_files works identically."),
    ("workday.step_persistence", "Workday persists each step on Save and Continue, so a reconnect can "
     "walk forward through completed steps and resume cleanly."),
    ("workday.phantom_error", "candidateHome shows a '1 error' banner after a direct goto. Benign."),
]
for fid, text in FACTS:
    N(f"tool_fact:{fid}", "tool_fact", text)


# ------------------------------------------------------- the application

N(APP, "application", "Gartner — Data Scientist (Classical ML, NLP & LLM/GenAI/Agentic AI)",
  requisition="110911", submitted=True, submitted_date=DAY, status="In Process",
  credits_spent=66, outcome="submitted without human review — see pitfall:A1",
  roles_submitted=5, resume="Jay_Singh_Resume.pdf (120.35 KB)")
E(APP, TEN, "observed_in")

g.save()
log_event("seed", day=DAY, application=APP,
          nodes=len(g.nodes), edges=len(g.edges),
          source="live run 2026-08-02, execution_instruction.md, field_map.json v2")

print(f"nodes={len(g.nodes)} edges={len(g.edges)}")
for t in sorted({n['type'] for n in g.nodes.values()}):
    print(f"  {t:15s} {len(g.query(type=t))}")
