# job-intel — AGENTS.md

Background-research playbook for the `job-intel` subagent. You produce dossiers;
fill agents (`workday-fill`, `eightfold-fill`, `avature-fill`, `successfactors-fill`,
`greenhouse-fill`, `lever-fill`, `ashby-fill`, `form-fill`) consume them. Profile truth:
`user_profile.json` + `work_ex_details.md`. Market rules: `job-application-roadmap.md` §3.

## 1. Input contract

A batch of 1–N items, each `{ url, company? }`. Treat the batch as one run: read profile
files ONCE, then process every link before writing a single line of output.

## 2. Per-job procedure (cheap by design)

1. `webfetch` the URL (markdown). If it 404s/403s on an API pattern (e.g. Workday
   `wday/cxs` 403) or returns no JD, do NOT retry more than once — mark
   `fetch: failed` + `needs_browser_recon: true` and move on.
2. Identify the ATS from fingerprints (domain + page markers):
   `myworkdayjobs.com`→workday | `careers.<co>.com` PCS / `eightfold.ai`→eightfold |
   `jobs.<co>.com/Careers`→avature | `successfactors.com` / TalentBrew `/job/`→successfactors |
   `job-boards.greenhouse.io`→greenhouse | `lever.co`→lever | `jobs.ashby.com`→ashby |
   `docs.google.com/forms`→formfill-google | `forms.cloud.microsoft`→formfill-microsoft.
   Unknown → `ats: unknown` + best-guess fill agent, never a guess stated as fact.
3. Extract: title, location, YoE band, salary band, top 5 skills, degree asks, work
   model (onsite/hybrid/remote). One `websearch` per job MAX, only for gaps that change
   the verdict (e.g. confirming a reposted req ID, like Cardinal 20183735→20184220).
4. Map resume variant by JD keywords (exact rule from `initiate_fill.md`):
   RL/decision-intelligence/optimization/planning → `ML_Vision_RL`;
   CV/VLM/multimodal/document-AI → `ML_Vision`; GenAI/LLM/agents/general-DS → `GenAI_DS`.
5. Verdict via roadmap §3 against the profile (18mo, floor 22 LPA, India/Remote-India):
   `FILL` (or `FILL-STRETCH` with the gap named) | `SKIP-<reason>` (SENIOR_TITLE/5Y_GAP,
   SALARY_FLOOR, DOMAIN_OR_INFRA_MISMATCH, LEVEL_MISMATCH, EXTERNAL_FLOW) |
   `BLOCKED-<reason>` (dead req, login wall shape, location block).

## 3. Dossier schema (one compact block per job, no JD pastes)

`company | role | url | ats | suggested_agent | title | location | yoe | salary |
skills(top5) | resume_variant | verdict + reason | unknowns(QUEUED) | needs_browser_recon`

## 4. Hard rules

- Never invent req IDs, salaries, YoE, or locations. Missing → `unknown`, not a guess.
- Never rank on JD-text-vs-sidebar disagreements silently — trust the stricter number,
  note the conflict in one line.
- Same-company second postings and external-apply instructions (`apply at http…`) get
  flagged explicitly (`SAME_COMPANY_2ND`, `EXTERNAL_FLOW`), never auto-approved.
- Output dossiers only. No ledger writes, no filings — the orchestrator owns those.

## 6. unnecessary file
- Strictly do not load any other *.md* file other that menioned in @initiate_fill.md or AGENTS.md
- Strictly do not load the *playwright-cli* based .md files when working with *playwright-mcp*
