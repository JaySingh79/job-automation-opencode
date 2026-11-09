# ashby-fill — AGENTS.md

Platform playbook for the `ashby-fill` subagent. Read this before touching any Ashby
board (`jobs.ashby.com/<org>/<slug>`). Shared fill loop: `initiate_fill.md`.

# Rules
## 1. Fingerprint (recon-first — no completed Ashby run yet)

- Ashby postings are typically ONE long form page: personal info → resume upload →
  custom questions → EEO/voluntary → final Submit. Confirm the shape on arrival with the
  standard recon unit (snapshot + `page_recon.js` evaluate + fullPage screenshot) and
  record the true layout in `ats/ashby/observation_importance.md` before filling.
- If the posting redirects off-board (LinkedIn-only etc.), treat as `EXTERNAL_FLOW` and
  DEFER to the human — never treat an external button as the application.

## 2. Resume

- Upload the local variant by JD match (`user_profile.json → resume_files`):
  `GenAI_DS` (GenAI/LLM/agents/general DS) / `ML_Vision` (CV/VLM/multimodal/document AI) /
  `ML_Vision_RL` (RL/decision intelligence/optimization). Verify `%PDF` magic + exact byte
  count before upload.

## 3. Answers (profile-backed only)

- 18mo total experience, Immediate notice, India authorization, sponsorship `No` for
  India roles, pay `22-26 LPA (negotiable)` / numeric `22`. Prose from
  `work_ex_details.md` verbatim claims only — never invent metrics or titles.
- For screening questions matching 'tell me what you have done', 'what all projects have you worked on', 'your ML journey', 'what makes you special', or general candidate overview, strictly use `src/knowledge_source/submission_pitch.md`. For company-specific interest questions, use `src/knowledge_source/wellfound/wellfound_interest_answer.md`.
- Relevance filter (roadmap §3): AI/ML/DS/GenAI/agentic/RAG/eval/NLP, India/Remote-India,
  range tops ≥18L on exact skill matches. Skip taxonomy: SENIOR_TITLE/5Y_GAP,
  SALARY_FLOOR, DOMAIN_OR_INFRA_MISMATCH, LEVEL_MISMATCH, EXTERNAL_FLOW.

## 4. Verification

- Read the confirmation state back from the DOM after the human's Submit (success text /
  confirmation URL) — never assume the click worked. Record the exact strings in
  `ats/ashby/observation_importance.md` so the next run matches them verbatim.

## 5. Output contract

`RECON → PLAN → FILL → VERIFY` per page, no call narration. Final: filled count,
uploads, `QUEUED` items with reasons, confirmation evidence, human next action.
Checkpoint `src/application_progress/ashby_lever_greenhouse/src/application_progress/ashby_lever_greenhouse/ats_progress.json` + `job_links.json`. Strictly never read/write progress files in the root of `src/application_progress/`.

## 6. unnecessary file
- Strictly do not load any other *.md* file other that menioned in @initiate_fill.md or AGENTS.md

## 7. Strict rules — 2026-10-14 (user order, no exceptions)
- SINGLE-JOB TAB RULE (per-agent sequential, multi-agent parallel): All agents may work in parallel, but each agent must finish the current job (fill → verify → submit → close) before opening a different tab with a different application. One job at a time per agent — never parallel-fill across tabs within the same agent.
- FRESHNESS PRE-FILTER: Strictly filter out job openings that have expired or are more than 1 month old BEFORE opening (and wasting time). Check posted/indexed date; if expired/closed/404 or >30 days old, mark SKIP-EXPIRED/STALE with reason, no navigate, no snapshot, no recon.
- ANTI-BOT DETECTION HUMAN EMULATION (MANDATORY):
  1. DEFINITELY SCROLL 4 TIMES: On every Ashby page, perform at least 4 smooth scrolls (25%, 50%, 75%, 100% of viewport) to trigger viewport observers, lazy components, and human behavior telemetry (crucial to avoid Google reCAPTCHA Enterprise "flagged as possible spam" blocks).
  2. SEQUENTIAL TOP-TO-BOTTOM ORDER: Fill fields strictly in order: Personal info -> Location -> Resume upload -> Custom screener questions -> Submit.
  3. RANDOM DELAYS: Add 800ms - 2200ms randomized delays between fields and 60ms - 180ms delay between keystrokes. Never perform instantaneous bulk DOM sets.
  4. 5 AGENTS MAX: Process at most 5 jobs/agents at a time.

## 8. Hard-Won Field Knowledge & Anti-Pattern Mitigations (2026-10-18 Audit)

### A. Initial Form Expansion / Apply Button
- Many Ashby job boards land on the description view with the application form unmounted. Always check for and click `button:has-text('Apply')` or `a:has-text('Apply for this job')` to mount the form fields before taking a snapshot or filling.

### B. Location Combobox Protocol
- The Ashby Location field is an interactive combobox (`div[role='combobox']:has-text('Start typing')` or `input[placeholder*='Start typing']`).
- Protocol: Click the field, type `India`, wait 500ms for the autocomplete popup, then send an `Enter` keypress to select the location chip.

### C. React Synthetic Event Requirement
- Setting input values directly in JS via `el.value = ...` will not register in React state. Always use Playwright native `page.locator().fill(...)`, `browser_fill_form`, or the prototype descriptor setter (`Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, val)`) followed by `input`, `change`, and `blur` events.

### D. File Upload Verification
- Attach resume using `input[type='file']`. Verify that the green `Success` badge / attached filename renders in the DOM before proceeding to submit.

### E. Earned Server Confirmation Truth
- Verified confirmation states on Ashby:
  - Demandbase: URL `jobs.ashbyhq.com/demandbase/<id>/application` + heading `Success` + text `Your application was successfully submitted. We'll contact you if there are next steps.`
  - Anyone AI: URL `jobs.ashbyhq.com/anyone-ai/<id>/application` + heading `Success` + text `Your application was successfully submitted.`
- Capture full-page screenshot artifact to `src/accessability_snapshot/<company>-success.png`.
- Tab must be closed immediately after recording confirmation.
