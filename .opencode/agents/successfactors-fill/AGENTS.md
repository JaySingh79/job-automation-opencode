# successfactors-fill — AGENTS.md

Platform playbook for the `successfactors-fill` subagent. Read this before touching any
SuccessFactors portal (`career*.successfactors.com`) or its TalentBrew details pages
(`careers.<company>.com/job/...`). Shared fill loop: `initiate_fill.md`. Master rules:
`Playwright MCP Optimized Operating Prompt.md`.

## 1. Fingerprint

- Details pages are TalentBrew (`/job/<location-slug>/<reqId>`): Overview / Success profile /
  Responsibilities / Values / Benefits sections, `Job ID: <req>-en_US`, and an `Apply` link
  carrying `feedId/tcsource/p_sid/p_uid/ss` params. Read the FULL JD here first (cheap,
  no auth) and pick the resume variant before touching the portal.
- Apply lands on `career*.successfactors.com/career?company=<...>&career_ns=job_application
  &career_job_req_id=<req>` — a Sign In wall: Email + Password (+Show toggle), "Forgot your
  password?", and a "Not a registered user yet? Create an account" path. Internal
  employees are routed to People Central — ignore it.

## 2. Auth (observed live on NetApp, 2026-09-18)

- No guest path was offered: account is mandatory. Pause for the human (they sign in or
  create the account); never invent passwords. Prefilling the KNOWN profile email is safe.
- Post-login flow has NO completed run yet — recon-first: run the full recon unit
  (snapshot + `page_recon.js` evaluate + fullPage screenshot) on the first application
  page, record the true step list + terminal step name in
  `ats/successfactors/observation_importance.md`. That note is this agent's dearest gap.

## 3. Resume

- Variant by JD match (`user_profile.json → resume_files`): `GenAI_DS` (GenAI/LLM/agents/
  general DS) / `ML_Vision` (CV/VLM/multimodal/document AI) / `ML_Vision_RL` (RL/decision
  intelligence/optimization). Verify `%PDF` magic + exact byte count before upload.

## 4. Privacy particulars (read on the details page, don't skip)

- These tenants disclose automated screening (NetApp names Eightfold matching + Findem,
  with human review and an opt-out via email including resume + job ID + subject
  `Data Privacy Request`). Note the disclosure in the ledger; it never changes answers.

## 5. Fit calibration (profile-backed)

- Candidate: 18mo, Python/RAG/LangGraph agentic stack. `4-8 years` floors with exact
  skill identity (LangGraph/LangChain/RAG/MCP/A2A, FAISS/Milvus) are fill-to-Review per
  roadmap §3 precedent — flag the stretch in the ledger, keep every number truthful
  (never inflate YoE to fit a band).

## 6. Output contract

Per step: `RECON → PLAN → FILL → VERIFY`, no call narration. Final: filled count,
uploads, `QUEUED` items with reasons, review-page state, `READY FOR HUMAN SUBMISSION`
(or the exact auth wall + what the human must do). Checkpoint `ats_progress.json` +
`job_links.json`.

## 6. unnecessary file
- Strictly do not load any other *.md* file other that menioned in @initiate_fill.md or AGENTS.md
- Strictly do not load the *playwright-cli* based .md files when working with *playwright-mcp*
