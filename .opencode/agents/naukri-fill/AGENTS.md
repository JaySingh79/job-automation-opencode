# naukri-fill — AGENTS.md

Platform playbook for the `naukri-fill` subagent. Read this before touching any Naukri page (`naukri.com/job-listings-*`). Shared fill loop: `initiate_fill.md`. Master rules: `GEMINI.md` and `AGENTS.md`.

## 1. Fingerprint & Detection

- Entry: `https://www.naukri.com/job-listings-<slug>-<id>`
- Apply Button Identification:
  - If button text has `Apply on company site` or selector has external redirect markers: **EXTERNAL_FLOW**. Bail out immediately (do not fill here, leave for external ATS filler).
  - If button text is `Apply` (native internal apply): Proceed with `naukri-fill`.
- Apply Types on Naukri:
  1. **Instant 1-Click Apply**: Clicking Apply triggers immediate application using pre-uploaded Naukri profile & resume. Button updates to `Applied` with confirmation toast/banner: `"Application successfully sent to recruiter"`.
  2. **Recruiter Questionnaire Drawer**: A sliding drawer (`.drawer-wrapper`, `.apply-drawer`, or modal) appears requiring answers to recruiter questions (CTC, notice period, experience, technical skills, short text).
  3. **Chatbot / Screening Flow**: An automated chatbot widget asks screening questions step-by-step.
     * **Long Chat & Human Input Protocol**: If the application requires a long chat or complex custom inputs, inform the orchestrator agent with the job title, company, and link for human input. Let the agent hold/wait for **2 minutes (120s)**. Then check snapshot: if submitted, record confirmation and move to the next application; if not submitted after 2 minutes, log status as `ready_for_human_submission`, close the tab, and proceed to the next job.

## 2. Token-Cheap Per-Job Loop (RECON → DECIDE → ACT → VERIFY)

1. **Recon Once**:
   - Check if page is loaded and title matches the job.
   - Run 4 smooth viewport scrolls (25%, 50%, 75%, 100%) to trigger telemetry and lazy elements.
   - Inspect `#apply-button` or `.apply-button` / `button:has-text("Apply")`.
   - Confirm it is NOT "Apply on company site". If already applied (`✓ Applied`), bail out immediately (<=1s).
2. **Decide Once**:
   - Determine if it is 1-click apply or requires questionnaire drawer.
3. **Act in Batches**:
   - Click `#apply-button`.
   - If drawer/modal opens:
     - Fill numeric fields (Total Exp: `1.5`, Expected CTC: `22`, Current CTC: `0` or appropriate fresher value).
     - Select Notice Period: `Immediate` / `0-15 Days` / `Serving Notice`.
     - Select Radio/Checkboxes matching candidate skills.
     - Fill short answers from `user_profile.json` and `work_ex_details.md`. For open-ended questions use `src/knowledge_source/submission_pitch.md`.
     - Human delays: 800ms–2200ms between inputs.
4. **Verify Once**:
   - Check confirmation text: `"Applied"`, `"Application sent"`, or `"Your application has been received"`.
   - **Error Handling Gate**: If the page displays `"There was an error while processing your job application, please try again"`, do NOT get stuck or retry indefinitely. Simply log status as `error` / `server_processing_error` in `src/application_progress/naukri/naukri_progress.json`, close the tab immediately, and skip to the next job in the queue.
   - Take snapshot or read DOM confirmation state.

## 3. Submit Authority & Guardrails

- Check for `src/submit_permisssions/naukri_submit_authority.json`.
- If permission is present and valid for this posting: Click final Apply/Submit in the drawer.
- If permission is NOT present: Stop on the review/drawer step with all fields filled, set status to `READY FOR HUMAN SUBMISSION`, and do NOT click final submit.

## 4. Answers Hierarchy & Facts

- Candidate: Jay Singh
- Email: `singhjay7100@gmail.com`
- Total Experience: `1.5` Years (18 months)
- Current Location: Gurgaon / Delhi NCR (Relocation: Yes, Open to Bangalore, Mumbai, Hyderabad, Pune, Remote)
- Notice Period: `Immediate` (0 days)
- Current CTC: `18` LPA (Updated per user instruction)
- Expected CTC: `22` LPA (Range 20–25 LPA)
- Degree: B.Tech / Bachelor's in Engineering
- Primary Stack: Python, PyTorch, LangGraph, RAG, GenAI, Machine Learning, Fast-API
- Projects & Work: Pascal DFR-Tracer (LangGraph RAG), Pibit, Symx, Innovaccer. Strictly follow `work_ex_details.md` and `submission_pitch.md`.

## 5. Ledger & Checkpoint Recording

- Progress checkpoint: `src/application_progress/naukri/naukri_progress.json`
- Applied ledger: `src/applied/naukri.json` with timestamp, jobId, title, company, and verification string.
- Close the tab immediately upon completion.
