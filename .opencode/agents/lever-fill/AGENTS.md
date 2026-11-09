# lever-fill — AGENTS.md

Platform playbook for the `lever-fill` subagent. Read this before touching any Lever
board (`*.lever.co` postings). Shared fill loop: `initiate_fill.md`. Master rules:
`Playwright MCP Optimized Operating Prompt.md`.

## 1. Fingerprint (recon-first — no completed Lever run yet)

- Lever postings are typically ONE long form page: personal info → resume upload →
  EEO → custom questions → final Submit. Confirm the shape on arrival with the standard
  recon unit (snapshot + `page_recon.js` evaluate + fullPage screenshot) and record the
  true layout in `ats/lever/observation_importance.md` before filling.
- If the posting redirects off-board (e.g. LinkedIn-only, like the Pixis
  `EXTERNAL_FLOW` case in `src/application_progress/ashby_lever_greenhouse/ats_progress.json`), DEFER to the human — do not treat an
  external button as the application.

## 2. Resume

- Upload the local variant by JD match (`user_profile.json → resume_files`):
  `GenAI_DS` (GenAI/LLM/agents/general DS) / `ML_Vision` (CV/VLM/multimodal/document AI) /
  `ML_Vision_RL` (RL/decision intelligence/optimization). Verify `%PDF` magic + exact byte
  count before upload.

## 3. Answers (profile-backed only)

- 18mo total experience, Immediate notice, India authorization, sponsorship `No` for
  India roles, pay `22-26 LPA (negotiable)` / numeric `22`. Prose from
  `work_ex_details.md` verbatim claims only — never invent metrics or titles.
- For screening questions matching 'tell me what you have done', 'what all projects have you worked on', 'your ML journey', 'what makes you special', or candidate overview, strictly use `src/knowledge_source/submission_pitch.md`. For company interest, use `src/knowledge_source/wellfound/wellfound_interest_answer.md`.
- Relevance filter (roadmap §3): AI/ML/DS/GenAI/agentic/RAG/eval/NLP, India/Remote-India,
  range tops ≥18L on exact skill matches. Skip taxonomy: SENIOR_TITLE/5Y_GAP,
  SALARY_FLOOR, DOMAIN_OR_INFRA_MISMATCH, LEVEL_MISMATCH, EXTERNAL_FLOW.

## 4. Verification

- Read the confirmation state back from the DOM after the human's Submit (success text /
  confirmation URL) — never assume the click worked. Record the exact strings in
  `ats/lever/observation_importance.md` so the next run matches them verbatim.

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
  1. DEFINITELY SCROLL 4 TIMES: On every Lever page, perform at least 4 smooth scrolls (25%, 50%, 75%, 100% of viewport) to trigger viewport observers, lazy components, and human behavior telemetry.
  2. SEQUENTIAL TOP-TO-BOTTOM ORDER: Fill fields strictly in order: Personal info -> Resume upload -> Custom questions -> EEO/Demographics -> Submit area.
  3. RANDOM DELAYS: Add 800ms - 2200ms randomized delays between fields and 60ms - 180ms delay between keystrokes. Never perform instantaneous bulk DOM sets.
  4. 5 AGENTS MAX: Process at most 5 jobs/agents at a time.

## 8. Hard-Won Field Knowledge & Anti-Pattern Mitigations (2026-10-18 Audit)

### A. Invasive Cookie Banner Dismissal
- Lever application pages frequently load an invasive cookie consent overlay (`button:has-text('Dismiss')` or `button:has-text('Accept')`) that intercepts clicks and obscures inputs. Always dismiss it first.

### B. The hCaptcha Barrier & Protocol
- Lever integrates hCaptcha (`#h-captcha`, sitekey `e33f87f8-88ec-4e1a-9a13-df9bbb1d8120`). Automated clicks on `#btn-submit` routinely trigger interactive visual challenges (e.g., dragging animals into matching outlines).
- Protocol: Never attempt automated heuristic puzzle solving on anti-bot widgets.
  1. Fill 100% of required fields (personal, custom screening, demographic, resume attachment).
  2. Verify `emptyRequired: 0` and `invalidCount: 0`.
  3. Capture full-page screenshot artifact (`src/accessability_snapshot/<company>_review_ready.png`).
  4. Leave the tab in focus on the browser, log status as `awaiting_human_captcha_submit` in `src/application_progress/ashby_lever_greenhouse/ats_progress.json`, and report `READY FOR HUMAN SUBMISSION`.

### C. Native `<select>` Elements
- Custom questions for currency (`INR`), pay period (`Annual`), gross/net (`gross`), and location (`India`) are native `<select>` controls. Use Playwright `page.locator('select').selectOption({ label: ... })`.

### D. Earned Server Confirmation Truth
- Verified URL pattern: `https://jobs.lever.co/<org>/<id>/applied` with heading `Thank you for applying.`
- Tab must remain open until human solves captcha and submits; close immediately once confirmation is observed.

