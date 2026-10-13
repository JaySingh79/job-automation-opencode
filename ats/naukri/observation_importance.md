# Naukri profile — observation_importance.md (driver: Playwright MCP, 2026-09-26)

## Flow shape
- Campus profile at `https://www.naukri.com/mnjuser/profile` (logged-in). Sections: Resume, Resume headline, Key skills, Employment, Education, Internships, Projects, Profile summary, Accomplishments, Career profile, Personal details, Languages.
- Completeness meter 55% ("Add 8 missing details") + "Share profile with recruiters" tick. No Submit/Apply on profile — Save-only page (Save per dialog). Safe for G1.
- Login: email `singhjay7100@gmail.com` (verified tick) + password typed by user in live tab. Known email entered by agent; passwords/OTPs never typed by agent. Never navigate away mid-login.

## Widget quirks (recipe that works)
- Tag/combobox recipe: type into `#id` → `evaluate` list `li[data-pick]` → REAL `browser_click` on the tag → repeat. Save enables ONLY after real-click (JS-set values don't enable Save). Guard modal closes via X.
- Refs churn after every dialog open/close → ref-free `evaluate` for reads; depth-limited targeted snapshots for new blocks only. One snapshot per dialog max.
- `evaluate` for reading values (inputs don't appear in innerText — query `input/textarea/select` values via JS). `find` single-term (e.g. `Save`, `Employer Name`) over full snapshots.
- File upload: click Update/Upload trigger → `file_upload` absolute path. Verify `%PDF` + bytes vs `user_profile.json → resume_files` before upload.

## Validation traps
- Employment add risks Fresher-flag flip (profile shows "My total work experience is 1 year 6 months" vs earlier "Fresher" header). USER APPROVED Employment ×2 (Symx, Cambridge) despite risk — record approval, never auto-add Employment without approval.
- Education XII/X show "Add Class XII/XII Details" placeholders even when task memo says SAVED — do NOT re-fill on assumption; verify via evaluate, QUEUE conflict (profile 92% both vs memo "63%").
- Languages present (English+Hindi, full proficiency) but NO facts in profile truth → leave QUEUED, never invent, never delete user's own entries.
- Photo SKIP per instruction. Email LEAVE `singhjay7100@gmail.com` unchanged (destructive change declined by default).
- IT skills section absent on campus profile (quicklinks have no IT skills) — covered by Key skills (18 present). Do not force-create.
- Internship/Project view shows title+dates only; descriptions (if any) hidden until edit dialog. Verify via edit dialog, not view text.

## Contention notes (shared live browser, 2026-09-26)
- Other agents (Instahyre apply-all, Wellfound) retarget current tab constantly. `select` then `evaluate` in SEPARATE turns always races (tab flips to Instahyre/Wellfound/Naukri-jobs between calls).
- Survival pattern (from Instahyre obs + confirmed here): same-turn `select`+`evaluate` pairs, `href` guards (`location.href` must contain `mnjuser/profile`), short single-purpose evaluate-only loops (~400 tok). Full snapshots cost ~30k tok and lose races — avoid.
- Never `navigate` without verifying current tab is Naukri (navigate acts on current tab — would hijack another agent's tab). Prefer atomic `tabs new {url}` if a fresh tab is needed.
- Read-only ops safe anytime; writes (click/fill) require URL/title guard in returned snapshot.

## Cost
- RECON once + screenshot; VERIFY via evaluate re-read. One closing snapshot max. Token-cheap closer: staged handoff preferred over repeated contested writes.

## Run 2026-09-26b (profile-only: Cambridge + BTP as Employment)
- Employment dialog controls: `#organisation1`, `#designation1` (search inputs), `#workDuration1_start_month/_start_year/_end_month/_end_year` (text.ddInput custom dropdowns + hidden Id inputs), `#currentExp` checkbox, `#details1` textarea (0/4000), `#submit-btn` Save/Cancel.
- NEW: evaluate native-setter + `li.click()` DOES commit ddInput month state — typed "May" + clicked suggestion verified via re-read (`mval=May`), Company full string + Designation committed same way. Month suggestion `li` carries NO `data-pick` (active class only) — filter by exact text match, not `data-pick`.
- Employment save still starts DISABLED; enables only when all required (company/designation/dates) committed.
- Sustained tab-steal storm (~15 min, current yanked to Instahyre tabs 2/3 every inter-turn gap; same-turn pairs also raced) made multi-turn completion impossible → terminal state STAGED: Cambridge Add-dialog left OPEN on tab 1 with org/des/May committed (unsaved — reload wipes). Handoff pattern: exact human click-path + paste texts, no reload.
