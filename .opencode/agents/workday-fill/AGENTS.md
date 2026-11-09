# workday-fill — AGENTS.md

Platform playbook for the `workday-fill` subagent. Read this before touching any
`*.myworkdayjobs.com` tenant. Shared fill loop: `initiate_fill.md`. Master rules:
`Playwright MCP Optimized Operating Prompt.md`. Raw history: `ats/workday/NOTES.md`.

## 1. Fingerprint

- Job pages AND apply flows live on `<employer>.wd1|wd5.myworkdayjobs.com/<locale>/EXT/...`.
- Progress bar names steps; step count varies per tenant (Cardinal req 20184220: 6 steps —
  Autofill → My Information → My Experience → Application Questions → Voluntary
  Disclosures → Review). Never assume another tenant's count.
- "Save and Continue" advances; it is NOT the submit (Gartner correction stands).
  Terminal step is a Review page with a Submit button — stop there.

## 2. Entry

- Prefer the tenant job URL directly (`/en-US/EXT/job/<location>/<slug>_<reqId>`).
- Dead requisitions return 404 + CXS 403 on `wday/cxs/...` endpoints. That means CLOSED,
  not blocked-by-bot: search the tenant (`/en-US/EXT?q=<title>`) for a live sibling req
  (same title/team/location, new ID) and report it instead of retrying.
- Step 1 may demand Create Account / Sign In first. Pause for the human; never invent a password.

## 3. Resume

- Upload the local variant by JD match (`user_profile.json → resume_files`):
  `GenAI_DS` (GenAI/LLM/agents/general DS) / `ML_Vision` (CV/VLM/multimodal/document AI) /
  `ML_Vision_RL` (RL/decision intelligence/optimization). Verify `%PDF` magic + exact byte
  count before upload. Filename + "Successfully Uploaded!" in snapshot = proof.

## 4. Widget quirks (earned, don't rediscover)

- `data-automation-id` sits on wrapper divs — descend to `input/textarea/button`.
- Searchable prompts (Degree, Field of Study, Country codes) do NOT filter on typing.
  Open the prompt button → Search box → Enter, then pick. If the value isn't listed
  (e.g. "Metallurgical and Materials Engineering"), leave optional fields EMPTY rather
  than forcing a wrong value.
- Date sections (work From/To, education years) MUST be typed via native fill
  (`browser_fill_form`/`browser_type` on the Month/Year spinbuttons). Values set through
  `browser_evaluate` display but FAIL validation ("field required"). Phone likewise:
  pick Country Phone Code first, then type the NATIONAL number only.
- A honeypot input for robots exists: `input[data-automation-id="beecatcher"]`. Strictly filter out and never touch `beecatcher`. Any interaction flags automated bot abuse.
- Legal Notice / Cookie Consent Overlay: On tenants like Valeo (`wd3`) and Pitney Bowes (`wd1`), a blocking banner `[data-automation-id="legalNotice"]` covers the viewport. Immediately click `[data-automation-id="legalNoticeAcceptButton"]` before attempting to locate the Apply button.
- Apply CTA Flow: Click `[data-automation-id="adventureButton"]` (Apply) -> click sub-option `[data-automation-id="applyManually"]`. Never navigate directly to `/apply/applyManually` via URL, as React router will reset to the main JD without an active session click.
- Stale error alerts persist after fixing fields; only the post-Continue validation counts.

## 5. Validation traps

- Errors surface ONLY as `innerText` lines starting with `Error` — not `errorMessage`,
  `role=alert`, or `aria-invalid`. Read them with one `browser_evaluate innerText` pass.
- LinkedIn URLs must contain `www.` or the field rejects.
- Role Description rejects `< > [ ] { } " \`` — sanitize (`over 90 percent`, single quotes).
- Known-good option vocab: YoE `1-3 years` (for 18mo); Degree `Bachelors`; education
  `Bachelor's / College Degree (3 or 4 years)`; English `Advanced – ...`; sponsorship `No`
  for India roles (profile-confirmed pattern). Re-verify per tenant — never assume.

## 6. Question bank defaults (profile-backed, override with explicit instruction)

- Background / criminal / drug / medical / random-drug screens: `Yes`.
- 18+: `Yes`. Authorized + docs (India): `Yes`. Non-compete: `No`. Ever employed here: `No`.
- Sponsorship (India): `No`. Relocate: `Yes`. Notice: `Immediate`.
- Source: prefer URL param (`?source=LinkedIn`) else profile default.
- For open-ended screening questions matching 'tell me what you have done', 'what all projects have you worked on', 'your ML journey', 'what makes you special', or candidate overview, strictly use `src/knowledge_source/submission_pitch.md`. For company interest, use `src/knowledge_source/wellfound/wellfound_interest_answer.md`.

## 7. Output contract

Per step: `RECON → PLAN → FILL → VERIFY`, no narration of calls. Final: filled count,
uploads, `QUEUED` items with reasons, review-page state, `READY FOR HUMAN SUBMISSION`.
Checkpoint `src/application_progress/workday/src/application_progress/workday/ats_progress.json` + `job_links.json`; append new findings to `ats/workday/NOTES.md`. Strictly never read/write progress files in the root of `src/application_progress/`.

## 6. unnecessary file
- Strictly do not load any other *.md* file other that menioned in @initiate_fill.md or AGENTS.md

## 7. Strict rules — 2026-10-14 (user order, no exceptions)
- SINGLE-JOB TAB RULE (per-agent sequential, multi-agent parallel): All agents may work in parallel, but each agent must finish the current job (fill → verify → submit → close) before opening a different tab with a different application. One job at a time per agent — never parallel-fill across tabs within the same agent.
- FRESHNESS PRE-FILTER: Strictly filter out job openings that have expired or are more than 1 month old BEFORE opening (and wasting time). Check posted/indexed date; if expired/closed/404 or >30 days old, mark SKIP-EXPIRED/STALE with reason, no navigate, no snapshot, no recon.
- ANTI-BOT DETECTION HUMAN EMULATION (MANDATORY):
  1. DEFINITELY SCROLL 4 TIMES: On every Workday page/step, perform at least 4 smooth scrolls (25%, 50%, 75%, 100% of viewport) to trigger viewport observers, lazy components, and human behavior telemetry.
  2. SEQUENTIAL TOP-TO-BOTTOM ORDER: Fill fields strictly in top-to-bottom visual order per wizard step.
  3. RANDOM DELAYS: Add 800ms - 2200ms randomized delays between fields and 60ms - 180ms delay between keystrokes. Never perform instantaneous bulk DOM sets.
  4. 5 AGENTS MAX: Process at most 5 jobs/agents at a time.

