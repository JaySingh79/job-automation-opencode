# greenhouse-fill — AGENTS.md

Platform playbook for the `greenhouse-fill` subagent. Read this before touching any
Greenhouse board (`job-boards.greenhouse.io/<org>/jobs/<id>`). Shared fill loop:
`initiate_fill.md`. Master rules: `Playwright MCP Optimized Operating Prompt.md`.

## 1. Fingerprint

- Single org-scoped boards; each posting is usually ONE long form page (no multi-step
  wizard): personal info → resume/CV upload → EEO/voluntary → custom screening questions
  → Submit. The terminal control is a final Submit — never yours.
- No account needed in past runs (CommerceIQ, Dscout, Lynx Analytics — all applied,
  see `ats_progress.json`). If a board ever gates on login, pause for the human.

## 2. Resume

- Upload the local variant by JD match (`user_profile.json → resume_files`):
  `GenAI_DS` (GenAI/LLM/agents/general DS) / `ML_Vision` (CV/VLM/multimodal/document AI) /
  `ML_Vision_RL` (RL/decision intelligence/optimization). Verify `%PDF` magic + exact byte
  count before upload. Prefer file upload; use Drive `resume_links` only if the field
  demands a URL.

## 3. Screening questions (custom per org — the real work)

- Answer ONLY from profile facts: 18mo total experience, Immediate notice, India
  authorization, sponsorship `No` for India roles, pay band `22-26 LPA (negotiable)` /
  numeric `22`. Prose answers come from `work_ex_details.md` verbatim claims only.
- For screening questions matching 'tell me what you have done', 'what all projects have you worked on', 'your ML journey', 'what makes you special', or candidate overview, strictly use `src/knowledge_source/submission_pitch.md`. For company interest, use `src/knowledge_source/wellfound/wellfound_interest_answer.md`.
- "Imperfect-checklist welcome" JDs (Dscout-style) and exact skill-identity matches
  (LangGraph/RAG/pgvector/citation-evals) justify applying into higher YoE bands — flag
  the stretch, never pad numbers.

## 4. Verification strings (earned — match these, don't paraphrase)

- CommerceIQ: URL `/confirmation` + `Thank you for applying to CommerceIQ! Your
  application has been received.`
- Dscout: URL `/confirmation` + `We have officially received your application.`
- Lynx Analytics: URL `/confirmation` + `Thank You for applying. Your application has
  been received.`
- New org, same pattern: confirm via `/confirmation` URL + received-application text read
  back from the DOM — never assume the click worked.

## 5. Relevance filter (roadmap §3)

- Apply: AI/ML/DS/GenAI/agentic/RAG/eval/NLP, India/Remote-India, range tops ≥18L on
  exact skill matches. Skip with reason: SENIOR_TITLE/5Y_GAP, SALARY_FLOOR,
  DOMAIN_OR_INFRA_MISMATCH, EXTERNAL_FLOW (LinkedIn-only postings → defer to human).

## 6. Output contract

`RECON → PLAN → FILL → VERIFY` per page, no call narration. Final: filled count,
uploads, `QUEUED` items with reasons, confirmation evidence, human next action.
Checkpoint `ats_progress.json` every 2–3 applies + `job_links.json`.

## 6. unnecessary file
- Strictly do not load any other *.md* file other that menioned in @initiate_fill.md or AGENTS.md

## 7. Strict rules — 2026-10-14 (user order, no exceptions)
- SINGLE-JOB TAB RULE (per-agent sequential, multi-agent parallel): All agents may work in parallel, but each agent must finish the current job (fill → verify → submit → close) before opening a different tab with a different application. One job at a time per agent — never parallel-fill across tabs within the same agent.
- FRESHNESS PRE-FILTER: Strictly filter out job openings that have expired or are more than 1 month old BEFORE opening (and wasting time). Check posted/indexed date; if expired/closed/404 or >30 days old, mark SKIP-EXPIRED/STALE with reason, no navigate, no snapshot, no recon.

