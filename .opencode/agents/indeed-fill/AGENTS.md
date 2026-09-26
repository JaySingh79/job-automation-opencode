# indeed-fill — AGENTS.md

Platform playbook for the `indeed-fill` subagent. Read this before touching any Indeed page
(`in.indeed.com/jobs*`). Shared fill loop: `initiate_fill.md`. Master rules:
`Playwright MCP Optimized Operating Prompt.md`.

## 1. Fingerprint

- Entry: `https://in.indeed.com/?r=us` (homepage, logged out: Sign in link, cookie banner
  with Reject All, `q` + `l` comboboxes, Find jobs button). Dismiss cookies first.
- Search shape: `/jobs?q=<keywords>&l=<location>` (e.g.
  `?q=fresher+data+scientist&l=Bengaluru%2C+Karnataka`). The `q`/`l` inputs are
  `role=combobox` text inputs — type with `slowly:true` to trigger suggestions; never set
  `.value` via raw JS (React state misses it and Find jobs no-ops). Results heading states
  the count (observed: `200 Fresher Data Scientist Job Vacancies in Bengaluru, Karnataka`).
- Results page: left list (cards: title button, company, location, salary snippet, Easily
  apply marker, Save toggle) + right detail pane (Job details, Location, Full job
  description, `Apply with Indeed` / `Save job` / `Share Job`). Cards are the discovery
  source — harvest from them, don't page blindly; pagination links exist (`start=10…`).
- Apply paths: (a) `Easily apply` / `Apply with Indeed` → in-flow Indeed form (profile +
  resume + screening questions); (b) external company-site apply → EXTERNAL_FLOW, DEFER to
  the human, never treat as an Indeed apply.
- Login wall: `secure.indeed.com/auth…` (Sign in). No Indeed password exists in
  `user_profile.json` — pause and ask via the question tool (email + password/OTP), never
  guess. Pre-filling the known email is safe; the secret comes from the human.

## 2. Token-cheap per-job loop

1. Arrive via search URL (or card click for the detail pane).
2. `evaluate` recon only: title, company, location, salary (`₹X–₹Y a year`), snippet,
   Easily-apply vs external markers, experience line. SKIP HERE on filter fail — never
   snapshot a card you won't fill.
3. `snapshot` once (Apply ref only) → open the apply flow.
4. `find` for the apply dialog/fields → targeted `snapshot(target=dialog)` → ONE batched
   `fill_form` for text/email/phone + resume variant by JD match (`GenAI_DS` / `ML_Vision` /
   `ML_Vision_RL` from `user_profile.json → resume_files`, `%PDF` magic + byte-count
   verified). Long prose via the base64 React-setter path, never typed raw.
5. Verify by reading state back (confirmation text / applied marker / pane state), never by
   assuming the click worked.

## 3. Answers (profile-backed only)

- 18mo total experience, Immediate notice, India authorization, sponsorship `No` for India
  roles, pay `22-26 LPA (negotiable)` / numeric `22`. Prose from `work_ex_details.md` only —
  Pascal DFR-Tracer (LangGraph RAG, pgvector, citation loop, 4hr→2min), Pibit 94.2%
  classification pipeline, Symx 87%/92%, Innovaccer Sara RAG, Cambridge agentic workflows.
- Relevance filter: fresher software/data roles (AI/ML/DS/GenAI/agentic/RAG/eval/NLP
  preferred under the broader scope), India/Remote-India, exp 0–2y ideal (2–4y ok on exact
  skill identity), range tops ≥18L on exact matches. Skip taxonomy (shared):
  SENIOR_TITLE/5Y_GAP, SALARY_FLOOR (≤10L), VOICE_OR_SECURITY_CORE_GAP, LEVEL_MISMATCH
  (intern/gig/support), SAME_COMPANY_2ND, DOMAIN_OR_INFRA_MISMATCH, EXTERNAL_FLOW.
- Observed fresher-relevant examples (2026-09-18, Bengaluru): Ascent HR LLM/ML up to ₹18L
  (Python/SQL/TF/FastAPI/cloud/K8s — strong identity), Giniminds LLM ₹10–15L, CoffeeBeans
  (mentorship, fresher-friendly), Fuku healthcare pipelines, Genpact 4A (band check first).

## 4. Verification and ledgers

- Confirm each apply from the DOM (confirmation copy / applied state / pane change) and
  record the exact strings in `ats/indeed/observation_importance.md` so the next run matches
  verbatim.
- `ats_progress.json`: applied / blocked (LOGIN_WALL, OTP/CAPTCHA) / skipped-with-reason.
  `jobs_applied.json`: append `{company, role, location, salary, url, status}`. `job_links.json`:
  `{Company: job_url}`. Checkpoint every 2–3 applies.
- Never mutate profile prefs, location, salary, or resume choice mid-batch without human
  confirmation. Same-company second applications need explicit approval.

## 5. Output contract

`RECON → PLAN → FILL → VERIFY` per job, no call narration. Final: filled count, uploads,
`QUEUED` items with reasons, confirmation evidence, ledger paths touched, human next action
(Submit ownership, OTP/CAPTCHA, external-flow links). Waste-log reminders: no per-field
snapshots, no cookie-banner re-clicks, no homepage search re-typing after the URL works.

## 6. unnecessary file
- Strictly do not load any other *.md* file other that menioned in @initiate_fill.md or AGENTS.md
- Strictly do not load the *playwright-cli* based .md files when working with *playwright-mcp*
