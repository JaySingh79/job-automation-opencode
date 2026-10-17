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
Checkpoint `ats_progress.json` + `job_links.json`.

## 6. unnecessary file
- Strictly do not load any other *.md* file other that menioned in @initiate_fill.md or AGENTS.md

## 7. Strict rules — 2026-10-14 (user order, no exceptions)
- SINGLE-JOB TAB RULE (per-agent sequential, multi-agent parallel): All agents may work in parallel, but each agent must finish the current job (fill → verify → submit → close) before opening a different tab with a different application. One job at a time per agent — never parallel-fill across tabs within the same agent.
- FRESHNESS PRE-FILTER: Strictly filter out job openings that have expired or are more than 1 month old BEFORE opening (and wasting time). Check posted/indexed date; if expired/closed/404 or >30 days old, mark SKIP-EXPIRED/STALE with reason, no navigate, no snapshot, no recon.