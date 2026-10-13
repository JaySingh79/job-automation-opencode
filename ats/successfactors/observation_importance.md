# SuccessFactors / TalentBrew — observation_importance.md

Driver: Playwright MCP (`playwright_browser_*`). No completed post-login run yet.

## Fingerprint (confirmed live 2026-10-05, Alstom req 1429022633)
- Details page is TalentBrew: `jobsearch.<co>.com/job/<Location-Slug>/<reqId>/`
  (e.g. `/job/Bangalore-AI-Engineer-KA/1429022633/`), title `AI Engineer`, sections
  Overview / Success profile / Responsibilities / Values / Benefits, `Job ID: 1429022633`,
  share widget + `Save job` + `Apply now` buttons (buttons, not anchors — href scrape
  via `a` misses them).
- Backend is SuccessFactors: `Log in` link → `https://career5.successfactors.eu/career?company=ALSTOM`
  (`career*.successfactors.eu/com` + `career_ns=job_application&career_job_req_id=`).
  Same shape as AGENTS.md NetApp precedent (career*.successfactors.com).
- Full JD readable pre-auth (cheap): Alstom AI Engineer lists Mandatory
  `Degree (min 8 years of Exp)`, 8y AI/ML incl GenAI/RAG/LLM-eval (faithfulness,
  groundedness, RAGAS, LangChain/LangGraph/LlamaIndex), Python/SQL, AWS
  (Bedrock/SageMaker/Lambda), MLOps (MLflow, Docker/Kubernetes), Agile/Scrum.

## Flow shape (expected, not yet traversed post-login)
- Details → Apply → SuccessFactors Sign In wall (Email + Password, mandatory account,
  no guest path observed on NetApp) → application steps → terminal Review step.
- NEVER click Submit/Apply/Send/Finish; stop on Review → `READY FOR HUMAN SUBMISSION`.
- Auth wall = PAUSE for human (they sign in), never invent passwords; prefilling known
  profile email is safe.

## Blocker / contention note (2026-10-05)
- Shared Playwright browser is multi-agent contended: tab indices shift between calls
  (HPE tab closed, DP World Oracle tab opened mid-run; Alstom moved index 2→1).
  `browser_evaluate` landed on Scalio Google Form and DP World Oracle page after
  successful Alstom snapshots. Mitigation: list tabs → select → single action →
  re-verify `location.href` in the same evaluate return; never assume sticky tab;
  avoid extra navigations when another agent owns the current tab.

## Cost
- One snapshot of the TalentBrew details page is enough to decide SKIP vs FILL
  (YoE gate is in the JD). No reconFn/screenshot needed for senior-gated skips.
