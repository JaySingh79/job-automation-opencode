# Phenom People (TXM) — observation_importance.md

Employer seen on: HPE (`careers.hpe.com`). Driver: playwright-mcp (shared-browser session).
Date: 2026-10-05. Job: Data Scientist 1209922, Bengaluru Karnataka 560048 (note: `/us/en/` locale path does NOT mean US-only — verify city in JD).

## Flow shape
- Job page: `/us/en/job/<reqId>/<slug>` — location + category + "Job Level TCP_xx" + full JD on one page.
- `Apply Now` → `/us/en/apply?jobSeqNo=HPE1US<reqId>EXTERNALENUS&step=<N>&stepname=<camelCase>`.
- 5 steps, linear, progress bar: 1 My information (`personalInformation`) → 2 My experience (`workAndEducation`) → 3 Application questions → 4 Voluntary Disclosures → 5 Review. Next/Previous per step; terminal step is Review. NEVER Submit (human's click).

## Widget quirks
- Resume upload FIRST: "Upload Resume" button → native file chooser → `browser_file_upload`. Constraints shown: DOC/DOCX/HTML/PDF/TXT, **1 MB max** (GenAI_DS 130007 bytes OK). Success fires a native **alert** ("You have Uploaded Resume Successfully") — dismiss via dialog handler; it may auto-dismiss on re-render.
- Parser pre-fills name/email/phone + experience rows + skills; phone may include country trunk (parser put `918651274328` while code already `+91` → corrected to national `8651274328`).
- Country/Phone-Code selects pre-selected from geo (India / India (+91)) — leave unless wrong.
- "Phone Device Type" is a NATIVE `<select id="deviceType">` with options: Dormitory, Home, Main, Other, Pager 1, Pager 2, **Personal Mobile** (= profile `phoneType`). Set via native value setter + input/change events (evaluate) — plain assignment did not stick; needs `Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set`.
- Text inputs are React-controlled: use native input-proto setter + input/change events, not direct `.value=`.
- Consents: privacy-consent checkbox is REQUIRED (`aria-required`, label "I agree to the processing of my personal data"); AI-tools / SMS / email comms checkboxes optional → leave unchecked.
- "How did you hear about us" / "Source" pre-selected (HPE Career site / HPE Careers webpage) — kept as system defaults.
- Cookie banner ("Decline optional cookies") overlays the form — dismiss first.
- Step 2: experience repeater rows (title/company/from-MM/YYYY/to-MM/YYYY + "I currently work here" checkbox), skills combobox (parser-filled: OCR, API, Preprocessing, Promp…), LinkedIn textbox (empty → fill from profile). Parser kept only 4 of 6 profile roles, in correct descending end-date order; did NOT add missing rows (Symx AI, CSE project) to avoid reordering risk — QUEUED for human.
- Preferred name select defaults "No" — kept.

## Validation traps
- Step verify: count `[aria-required=true],[required]` visible empties; require 0 before Next. Date textboxes accept MM/YYYY text.
- React-state desync (steps 3–4): DOM value set via proto-setter + input/change does NOT always register (step-3 fields `a`, `g` and step-4 `gender` kept "This field is required" despite correct DOM values). Remedies that worked: (1) `browser_select_option` with a fresh ref for selects; (2) `browser_fill_form` replace for textarea; (3) `selectedIndex=o.index` + change + `blur()`; (4) focus+blur then Next (stale errors clear on re-validation). Always re-click Next after fixing — old error nodes are stale.
- Step 3 (Application questions, `jobSpecificQuestions`): 9 required — 8 native single-selects (options Yes/No; b uses YES/NO; h,i add Not Applicable) + 1 textarea (sponsorship locations → "N/A"). Answers live in `user_profile.json` → `hpe_screening_answers`, in order a–i.
- Step 4 (`voluntaryInformation`): Gender select required (Female/Male/Undeclared → Male per profile) + agreementCheck checkbox required. Veteran/disability sections absent on this posting.
- Step 5 Review (`applicationReview`): sections My Information / My Experience / Skills / Attachments with Edit links; Previous + Submit. STOP here — Submit is the human's.
- Seniority trap (this posting): JD demands Master's/PhD + 5–7+ yrs; candidate B.Tech + 18 mo → SENIOR-MISMATCH, filled only because user explicitly requested; never submit without user review.

## Cost
- Shared-browser tab contention with parallel fill agents is the dominant cost: snapshot refs expire on re-render and current-tab races misroute actions. Mitigations that worked: URL-guarded single-shot `browser_evaluate` (no-op off-target), idempotent fills, 3x bursts per turn, Next-click only after verify-pass.
