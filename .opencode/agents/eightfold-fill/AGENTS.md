# eightfold-fill — AGENTS.md

Platform playbook for the `eightfold-fill` subagent. Read this before touching any
Eightfold-powered site (`careers.<company>.com` on the PCS stack, `*.eightfold.ai`).
Shared fill loop: `initiate_fill.md`. Master rules:
`Playwright MCP Optimized Operating Prompt.md`.

## 1. Fingerprint

- Eightfold PCS pages embed a large `themeOptions`/navbar JSON blob; footer carries
  `Powered by eightfold.ai`. Job pages: `/careers/job/<pid>?hl=en-US&domain=<company>.com`.
  The JD panel exposes Job ID, company, job area, General Summary, Minimum Qualifications,
  full description, plus an "Insights from previous hires" panel (YoE distribution, top
  skills — useful stretch calibration, not profile data).
- Apply entry: `/careers/apply?pid=<pid>&...`. Expect a candidate-auth gate FIRST.

## 2. Auth (observed live on Qualcomm, 2026-09-18)

- `dialog` "Sign in": Email textbox + Continue button, OR "Sign in using Google", OR
  "Create an account". Current employees are routed to a separate Career Hub — ignore it.
- Email-first flow sends an OTP to the address; the dialog becomes "Check your email"
  with 6 single-char boxes + Submit + resend-timer + Back. Prefilling the KNOWN profile
  email and clicking Continue is allowed (auth step, not application submit).
- STOP at the OTP Submit button: the code belongs to the human (they read their inbox).
  Never invent passwords; never create accounts with made-up secrets.

## 3. Post-login flow (recon-first — no completed run yet)

- After auth, run the standard recon unit (snapshot + `page_recon.js` evaluate + fullPage
  screenshot) before deciding anything. Record the true step list and terminal step name
  in `ats/eightfold/observation_importance.md` — this section is the highest-value gap.

## 4. Resume

- Upload the local variant by JD match (`user_profile.json → resume_files`):
  `GenAI_DS` (GenAI/LLM/agents/general DS) / `ML_Vision` (CV/VLM/multimodal/document AI) /
  `ML_Vision_RL` (RL/decision intelligence/optimization). Verify `%PDF` magic + exact byte
  count before upload.

## 5. Fit calibration (profile-backed)

- Candidate: 18mo total, Python/RAG/LangGraph agentic stack, no C++/CUDA/kernel/NPU work.
  Edge-inference/systems JDs (Qualcomm QAIRT-style: quantization, SIMD, on-device) are a
  DOMAIN gap — still fill to Review when instructed (exact-match-first per roadmap §3),
  but flag `SENIOR_TITLE/5Y_GAP` and `DOMAIN_OR_INFRA_MISMATCH` plainly in the ledger.

## 6. Output contract

Per step: `RECON → PLAN → FILL → VERIFY`, no call narration. Final: filled count,
uploads, `QUEUED` items with reasons, review-page state, `READY FOR HUMAN SUBMISSION`
(or the exact auth wall + what the human must do). Checkpoint `ats_progress.json` +
`job_links.json`.
