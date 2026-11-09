# Global Antigravity (`agy`) Instructions (`~/.gemini/GEMINI.md`)

## 1. Core Operating Principles
- **Ultimate Goal Priority**: The user's query is the ultimate goal. Execute thoroughly, concisely, and accurately.
- **Python & Package Management**: Always use `uv` (`uv run python ...`, `uv pip install ...`, `uv venv`) and active `.venv` virtual environments for all Python operations. Never invoke raw `pip`.
- **Context Discipline & Subagent Delegation**:
  - Keep the primary orchestrator context lean.
  - Delegate read-only codebase/file exploration to `explore` or `research` subagents (`invoke_subagent` with `Model: "inherit"`), returning distilled insights with `file:line` anchors rather than raw file dumps.
  - Delegate external documentation and library research to `scout` or `research` subagents.
  - Delegate parallel multi-step tasks and ATS/form-filling sessions to specialized subagents in `.agents/agents/*.md` or `general` / `self`.

## 2. Browser & Job Automation Discipline (Playwright MCP)
When operating in job-automation workspaces (such as `D:\Projects\PRACTICE\firecrawl_test`):
- Follow the workspace `GEMINI.md`, `AGENTS.md`, and `initiate_fill.md` (`RECON ONCE → DECIDE ONCE → ACT IN BATCHES → VERIFY ONCE`).
- Route every job link or portal to its matching subagent in `.agents/agents/*.md` (`job-intel` first for batch JD research/scoring, then `workday-fill`, `ashby-fill`, `greenhouse-fill`, `lever-fill`, `eightfold-fill`, `avature-fill`, `successfactors-fill`, `wellfound-fill`, `indeed-fill`, `hirist-fill`, `instahyre-apply-all`, `form-fill`, `profile-fill`, `cover_letter_agent`, `answer-writer`).
- **Single-Tab-At-A-Time Per Agent**: Each filler agent must complete its current job (`fill → verify → stage/submit → close`) before opening another tab.
- **Never Click Final Submit Without Authority**: Stop on the final review step and report `READY FOR HUMAN SUBMISSION` unless a verified `*_submit_authority.json` (or explicit apply-all playbook rule) grants submit permission.
- **Strict Security Hygiene**: Never read or edit `.env` (except `.env.example`), `*.pem`, `*.key`, `**/secrets/**`, or `runs/`.
