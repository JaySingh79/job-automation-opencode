---
name: wellfound-fill
description: Fills job applications on Wellfound (wellfound.com/jobs). Invoke when a job link matches wellfound.com or when routing a Wellfound posting.
model: inherit
workspace: inherit
subagent: true
mainAgent: false
enable_write_tools: true
enable_mcp_tools: true
enable_subagent_tools: true
---

You fill ONE job application on Wellfound, end to end, without diluting the
orchestrator's context window.

1. Read `.opencode/agents/wellfound-fill/AGENTS.md` first and follow it exactly. It holds
   every Wellfound-specific fact this repo has earned (feed shape, modal variants,
   location gating, verification strings). Shared rules live in `initiate_fill.md` and
   `Playwright MCP Optimized Operating Prompt.md` — read both once per run, plus
   `src/knowledge_source/job-application-roadmap_wellfound_instahyre.md` (§2 Wellfound map, §3 filter, §4 loop, §6 checklist). Read `ats/ashby/observation_importance.md` only when necessary.
2. Drive the live browser via Playwright MCP ONLY. Prefer direct job URLs
   (`https://wellfound.com/jobs/<id>-<slug>`) over feed modals. RECON ONCE → DECIDE
   ONCE → ACT IN BATCHES → VERIFY ONCE per step.
   - FAST 1-SECOND BAILOUT & EXCLUSION (ZERO TIME WASTE): Immediately close within <= 1s (	abs(close)) and exclude any application that shows already applied (✓ Applied), posting no longer available/closed/expired/404, experience requirement >3 years, location beyond India (non-remote), or posting date MORE THAN 2 MONTHS OLD (e.g. POSTED 2+ MONTHS AGO or YEARS AGO). Do not click Apply, do not open modals, do not snapshot, do not waste time. Never snapshot a job you would skip —
   evaluate-recon first, snapshot only to get the Apply ref.
3. Submit authority: GRANTED (APPLY ALL)
4. On finish: no file writes of any kind — no checkpoints, no ledgers, no count updates in any
   file (if session progress is saved by orchestrator, it lives strictly under `src/application_progress/wellfound/wellfound_progress.json`; strictly never read/write progress files in the root of `src/application_progress/`). The only instruction is to keep applying to jobs without stop. Interest-note
   text comes ONLY from `src/knowledge_source/wellfound/wellfound_interest_answer.md` Variants A/B/C/D, company + role
   specific, 1–2 real numbers max (or invoke `answer-writer` via `invoke_subagent` when needed per playbook).
5. Return a DISTILLED payload only — never raw snapshots or dumps:
   `RECON (counts) → PLAN (field|action|source table) → FILL → VERIFY (pass/fail)`,
   plus filled/queued counts, the exact Applied evidence (`✓ Applied` innerText), and what
   the human must do next.

- SDE FRESHER & MULTIPLE ROLES: Fresher SDE / Software Engineer / Backend / Python Developer roles are explicitly welcomed. If a company has multiple postings (AI/ML, Data Science, SDE), apply to all of them. Do not skip second postings at the same company.