# Rippling ATS observation_importance.md — 2026-09-29 (Playwright MCP, driver playwright-mcp)

## Fingerprint (confirmed single posting: Alaan AI Engineer, Bengaluru)
- Rippling recruiting board: JD page (`/jobs/<id>?jobSite=...`) with `Apply now` buttons → apply page (`/apply?...&step=application`).
- Apply step is ONE long single-page form (no wizard Next/Continue seen); terminal state is a single `Apply` button, `disabled` until required fields pass. No login/OTP/CAPTCHA encountered; resume upload unauthenticated.
- Résumé dropzone (`Drop or select (.doc / .docx / .pdf)`) parses to autofill details (per helper text). Upload via Upload-trigger click → native file chooser → `browser_file_upload` with absolute path.

## Observed field inventory (Alaan AI Engineer)
- **Textboxes**: First name*, Last name*, Email*, Current company, Phone number* (+ country-code combobox default `+1 US`), Location*, fit-prose textbox (counter `0/500`), current/last salary* (`0/50`), expected salary* (`0/50`).
- **Comboboxes**: Pronouns (optional), Availability* (`Select`), Years of work experience* (`Select`) — options only visible after opening; enumerate before picking.
- **Radiogroups (Strong No / No / Yes / Strong Yes scale)**: B2B SaaS experience (optional, no *), startups* (required), work-from-office*.
- **SMS consent radiogroup**: Yes-consent / No-consent — default to No (matches standing SMS opt-out).
- **Cover letter**: optional second dropzone — skip (no cover letter in profile).

## Quirks / validation traps
- Refs are renumbered on every load (JD→apply navigation re-renders); always re-snapshot after navigation, never reuse refs across loads.
- `Apply` stays `disabled` while any required field is empty — use it as the ready signal.
- Salary fields carry `0/50` counters → keep values under 50 chars; fit-prose under 500 chars.
- Country-code combobox defaults to `+1 US` — must switch to India (+91) for Indian numbers.
- Current/last salary is required but NOT in user_profile.json → QUEUE for human (never invent numbers).

## Next run advice
- Upload résumé FIRST (parse may autofill name/email/company), then batch textboxes in one `browser_fill_form`, then comboboxes (open→enumerate→pick), then radios via click.
- Fit-prose (~380c): DFR-Tracer LangGraph RAG + pgvector HNSW + citation loop; Pibit 850-template doc pipeline 94.2%; Innovaccer RAG over GPT-4o/Milvus.
- Driver cost: recon is cheap (snapshot→file + disk read); fills need current-tab focus — do NOT run parallel with another filler session in the same browser (see 2026-09-29 incident below).

## 2026-09-29 incident — shared-browser contention
- A concurrent filler session (OpenAI Ashby + Greenhouse Conga tabs) shared the same Playwright browser; all MCP actions target the *current* tab, so ~50% of actions landed on the wrong tab, one stray click hit the other session's OpenAI form (`DepartmentGo To Market`), and my Rippling tab was closed twice (likely the other session's tab cleanup).
- Result: Job2 (Alaan) reached full RECON + PLAN but zero fills. Lesson: one filler session per browser at a time; coordinate via tabs or separate browser profiles.
