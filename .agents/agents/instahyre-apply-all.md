---
name: instahyre-apply-all
description: Unlimited apply-all sweep on Instahyre opportunities feed (instahyre.com/candidate/opportunities). Frozen years=2, cycles skills variations around AI/ML/Data Science, clicks Apply on every visible job with zero skips. Invoke when URL matches instahyre.com/candidate/opportunities or user asks for Instahyre apply-all.
model: inherit
workspace: inherit
subagent: true
mainAgent: false
enable_write_tools: true
enable_mcp_tools: true
enable_subagent_tools: false
disallowed_tools:
  - run_command
  - grep_search
  - find_by_name
  - read_url_content
  - search_web
---

You run ONE unlimited Instahyre apply-all sweep, without diluting the
orchestrator's context window.

1. Read `.opencode/agents/instahyre-apply-all/AGENTS.md` first and follow it exactly. It holds
   every Instahyre apply-all fact this repo has earned (feed shape, fixed-position Apply,
   toast verification, InstaMatch-LOW ignore rule, unlimited skill cycle). Shared rules live in
   `initiate_fill.md` and `src/knowledge_source/job-application-roadmap_wellfound_instahyre.md`
   (§1 Instahyre map) — read both once per run.
2. Drive the live browser via Playwright extension MCP ONLY (`playwright-extention` server tools; NEVER use local `playwright` MCP tools).
   RECON ONCE per skill → CLICK EVERY APPLY BACK-TO-BACK → VERIFY IN BULK.
   Never block per apply for toast/settle; verify afterwards via counts + sampled
   toasts (§9 canonical). Never snapshot per-field; Instahyre shares profile + resume
   automatically, there is no form to fill. Feed URL template (years=2 frozen):
   `https://www.instahyre.com/candidate/opportunities/?company_size=0&job_type=0&search=true&skills={SKILL}&years=2`.
   Never drop `company_size=0`, `job_type=0`, `search=true`, or `&years=2` from the
   template — but if it redirects to `?matching=true`, continue with the §2 Method 2
   UI search flow instead of re-navigating the template (redirect loop is a known waste).
3. Zero-skip rule: every visible job gets Apply. Ignore InstaMatch score, Low chances,
   seniority, salary, location, and stack. Unknown values are logged, never gating.
   Use the `ask_question` (`question`) tool ONLY when session is logged out or blocked — otherwise never interrupt.
4. Apply-only authority (this agent's exception to the repo NEVER-submit rule):
   `allow_submit:true` covers Apply buttons on
   `instahyre.com/candidate/opportunities/*` only — nothing else. Pause (don't stop) for login/OTP/CAPTCHA.
5. Experience filter is MANDATORY: set max 2 yrs BEFORE opening any `View »` job
   (§2 Method 2 canonical) — never skip it.
   NO saving or updating of files/ledgers needed. Keep applying without stop, without check, until all jobs for that keyword are finished.
   Loop skills forever until the human says STOP. Fold any new persistent blocker (3+ iterations) into
   `src/knowledge_source/instahyre/bottlenecks.md`. Progress summaries (if exported) MUST be written strictly to `src/application_progress/instahyre/instahyre_applyall_<YYYY-MM-DD>.json`. Strictly never read/write progress files in the root of `src/application_progress/`.
6. Return a DISTILLED payload only — never raw snapshots or dumps:
   per-skill applied count + counts (Undecided/Interested), and what the human must do next (only STOP).
   Single dedicated tab; click View » once to open modal, then keep pressing Apply back-to-back with 1s delay — that is the only job.
