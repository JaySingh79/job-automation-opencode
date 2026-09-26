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
  `EXTERNAL_FLOW` case in `ats_progress.json`), DEFER to the human — do not treat an
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
Checkpoint `ats_progress.json` + `job_links.json`.

## 6. unnecessary file
- Strictly do not load any other *.md* file other that menioned in @initiate_fill.md or AGENTS.md
- Strictly do not load the *playwright-cli* based .md files when working with *playwright-mcp*
