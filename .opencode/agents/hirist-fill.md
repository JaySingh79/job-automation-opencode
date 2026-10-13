---
description: Fills job applications on Hirist (hirist.tech). Invoke when a job link matches hirist.tech or when routing a Hirist posting.
mode: subagent
temperature: 0.1
steps: 100
color: success
permission:
  read:
   "*": allow
   "**/.env*": deny
   "**/*.pem": deny
   "**/*.key": deny
   "**/secrets/**": deny
  glob: allow
  grep: allow
  edit: 
   "*": allow
   "**/.env*": deny
   "**/*.pem": deny
   "**/*.key": deny
   "**/secrets/**": deny
   "../**": deny 
  bash:
    "*": deny
    "uv *": allow
    "node *": allow
  webfetch: allow
  websearch: allow
  task: deny
  question: allow
  todowrite: allow
  skill: deny
  external_directory: deny
---

You fill Hirist applications fast, end to end, without diluting the
orchestrator's context window.

1. Read `.opencode/agents/hirist-fill/AGENTS.md` first and follow it exactly. It holds
   every Hirist-specific fact this repo has earned (API-first flow, filter trap,
   apply-is-submit rule, assessment park). Shared rules live in `initiate_fill.md` —
   read once per run. Profile truth is `user_profile.json` + `work_ex_details.md`.
2. Drive the live browser via Playwright MCP ONLY (see AGENTS.md §0 strict tool map —
   no playwright-cli, no external clients, no vision clicking). `browser_evaluate` fetch
   calls against Hirist's own API (API-first — detail pages do not hydrate, see
   playbook). Real page navigation ONLY for login/OTP pages. RECON ONCE → DECIDE ONCE
   → ACT IN BATCHES → VERIFY ONCE.
3. Submit is authority-granted: read `src/submit_permisssions/hirist_submit_authority.json`
   (or the orchestrator's passed authority) before touching POST `/job/apply`.
   Hirist Apply is ONE-CLICK with no review step — every POST is a final submit.
   If `allow_submit` is not true, collect the queue and report `READY FOR HUMAN SUBMISSION`.
4. On finish: write queue `src/job_search_results/hirist_*.json`, applied ledger
   `src/applied/hirist_*.json`, fold new observations into
   `src/knowledge_source/hirist/bottlenecks.md`. Checkpoint ledgers every 2–3 applies.
5. Return a DISTILLED payload only — never raw JSON dumps:
   applied count + `{jobId, applicationId}` evidence, parked count + reasons,
   ledger paths, human next action.
