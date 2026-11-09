# Deep Research & 10-Plan Master Architecture: 100% Universal ATS Form-Filling Engine (Ashby, Greenhouse, Lever, SmartRecruiters)

**Created**: 2026-10-20
**Reference Video Analyzed**: `https://youtu.be/R9HNsnbYh8o` (*"Undetectable Automation: 5th Edition [Ultimate Web Scraping & CAPTCHA Bypass Tutorial]"* by Michael Mintz / SeleniumBase CDP Mode)
**Target Goal**: Achieve **100% (120/120)** verified form-fill coverage across **30 unseen Ashby**, **30 unseen Greenhouse**, **30 unseen Lever**, and **30 unseen SmartRecruiters** job applications after iterative training and debugging on a completely disjoint training corpus.

---

## Part 1: Deep Technical Synthesis

### 1.1 Insights from Reference (`https://youtu.be/R9HNsnbYh8o`) & CDP Anti-Bot Evasion
1. **Why Vanilla Playwright/WebDriver Fails**:
   - Standard Playwright sends `Runtime.enable` over the Chrome DevTools Protocol (CDP), allowing Cloudflare Turnstile, DataDome, hCaptcha, and reCAPTCHA Enterprise to detect active debugger hooks via `Runtime.consoleAPICalled` / stack-trace serialization side-effects.
   - Standard automation flags (`--enable-automation`, `navigator.webdriver = true`, headless font/WebGL mismatches, zero mouse/scroll event history prior to form submission) tank reCAPTCHA Enterprise and hCaptcha passive trust scores to `0.1`.
2. **CDP & Stealth Bypass Layer**:
   - **Isolated World Execution / `patchright` / Stealth CDP Injection**: Avoid leaking automation globals in the main world; strip `--enable-automation`; pass `--disable-blink-features=AutomationControlled`; maintain OS-consistent User-Agent, `navigator.platform` (`Win32`), WebGL ANGLE renderer, and hardware concurrency.
   - **Pre-Fill Behavioral Telemetry (`human_scroll_4x` + Bézier Mouse Moves + Keystroke Cadence)**:
     - Every page must execute 4 smooth scroll steps (`25% -> 50% -> 75% -> 100% -> 0%`) with `wheel` events and 400–800ms pauses to satisfy `IntersectionObserver`s and populate `reCAPTCHA Enterprise` / `hCaptcha` motion buffers.
     - Fields must be filled strictly **top-to-bottom** with 800–2200ms inter-field pauses and 60–150ms keystroke cadence on interactive inputs.

---

### 1.2 Complete Edge-Case Taxonomy by ATS

#### A. Ashby (`jobs.ashbyhq.com/<org>/<uuid>/application`)
1. **Direct `/application` Routing**: Appending `/application` mounts the React 18 form directly.
2. **Dual File Input Trap**: Some tenants place a "Resume Autofill" dropzone (`input[type="file"]`) above the actual resume field (`input#_systemfield_resume`). Selecting `.first` uploads to the wrong control. Always target `input#_systemfield_resume` specifically, or if absent, inspect parent label text (`Resume` vs `Autofill`).
3. **Resume Upload Race Wiping Email**: Uploading triggers `S3 204` -> `ApiSetFormValueToFile`. If `Email` is filled before or during this mutation, Ashby resets the internal React state of `Email` while leaving the text visually in the input! **Fix**: Upload resume FIRST, wait 2.5s for the filename pill + `Replace`/`Delete` buttons to render, and only then fill/verify `Email` + `Tab` blur.
4. **React 18 `_valueTracker` Two-Phase Setter**: Calling the native prototype setter with the same value is ignored by React 18. Always set `'x'` -> dispatch `input` -> set `targetValue` -> dispatch `input`, `change`, `blur`.
5. **Yes/No Button Groups (`_yesno`)**: Ashby renders Yes/No questions as `<button>` pairs inside a question container (`aria-pressed="true|false"` or `_selected` class), **not** `<input type="radio">`.
6. **Location Combobox (`_combobox`)**: Requires clicking `input[placeholder="Start typing..."]`, typing with keystroke delay (`India` or `Bengaluru, Karnataka, India`), waiting 800ms for `[role="listbox"] [role="option"]`, and clicking the first option.
7. **Multi-Checkbox Groups (`FIELDSET > LABEL`)**: Custom multi-select checkboxes must be clicked via their `<label>` element with 300ms pause between selections, and **never** checked blindly (only select matching answers or required consent checkboxes).
8. **Blank-Label Required Consent Checkbox**: Marketing/GDPR checkboxes can have `isRequired: true` and `title: ""`. Any isolated single checkbox at the bottom of the form or inside a consent block must be checked.
9. **Date Pickers & Spinbuttons**: `input[placeholder="Pick date..."]` or `input[type="date"]` (fill with `MM/DD/YYYY` or `YYYY-MM-DD` / click today+7 days), `input[type="number"]` (fill numeric value based on label: YoE=`1`, CTC=`18`, Expected=`22`, Notice=`7`).

#### B. Greenhouse (`job-boards.greenhouse.io` & `boards.greenhouse.io` / Embedded `#grnhse_iframe`)
1. **3 Layout Variants**:
   - **Variant 1 (Modern Remix)**: `job-boards.greenhouse.io/<org>/jobs/<id>` (`#application-form`, React-Select v5 `.select__control`).
   - **Variant 2 (Classic Boards)**: `boards.greenhouse.io/<org>/jobs/<id>` (`#application_form`, Select2 `.select2-container` or native `<select>`).
   - **Variant 3 (Embedded Iframe / Custom Domain)**: `?gh_jid=<id>` with `iframe#grnhse_iframe` or custom page containing dual forms (Job Alerts form vs Application form containing `input[type="file"]`).
2. **React-Select v5 Hidden Required Input Trap**:
   - Every dropdown on Modern Greenhouse consists of `.select__control` containing `<input class="select__input" id="question_...">` AND a sibling `<input class="remix-css-...-requiredInput" required>`.
   - After an option is clicked, `input.select__input.value` resets to `""`, while the selected text appears inside `.select__single-value` (or `.select__multi-value__label`) and the hidden `requiredInput` becomes valid (`checkValidity() === true`).
   - **Unnamed Country Combobox**: Some boards have a main `Country*` React-Select whose underlying `input[required]` has no `id` or `name`. Scanning by `.select__control` container and resolving label text via `label[for]`, `aria-labelledby`, or ancestor `.select__container` / `.field` captures 100% of dropdowns.
3. **Phone Country (`#country` / `intl-tel-input`) Ordering Trap**:
   - Selecting `Country` (`India +91`) *after* typing `#phone` reformats/corrupts `#phone` (`086512 74328`). Always select Phone Country **BEFORE** filling `#phone` (`8651274328`).
4. **Education & Employment Repeaters**:
   - Modern Greenhouse renders `School*`, `Degree*`, `Discipline*`, and Start/End Month/Year as async React-Select comboboxes (`#school--0`, `#degree--0`, `#discipline--0`, `#start-month--0`, `#start-year--0`, `#end-month--0`, `#end-year--0`). Typing `"Indian Institute of Technology"` / `"Bachelor"` / `"Computer Science"` and waiting 800ms loads the async `[role="option"]` list.
5. **Multi-Checkbox Questions vs Required Consents**:
   - Never check all checkboxes blindly (which selects contradictory answers like both `"Yes"` and `"No"` or all office locations). Group checkboxes by question container (`fieldset` or `.field`) and pick only the matching option(s) based on label semantics.

#### C. Lever (`jobs.lever.co/<org>/<uuid>/apply`)
1. **Resume Parse XHR Overwrite & `Current location` Clear Bug**:
   - Attaching a file to `input[name="resume"]` triggers an async `POST /parseResume` XHR (takes 2–4s) that overwrites `name`, `email`, `phone`, `org`, `urls[...]` and **wipes `input[name="location"]` to `""`**.
   - **Mandatory Sequence**: Upload resume FIRST -> wait up to 5s for `.resume-upload-success` (`"Success!"`) -> fill/overwrite all personal fields -> fill `input[name="location"]` -> type & select from `.dropdown-container` if location autocomplete is active -> re-verify `input[name="location"]` right before submit.
2. **Card-Scoped Custom Screening Questions (`cards[<uuid>][fieldN]`)**:
   - Every custom question lives inside `li.application-question` or `.application-question`.
   - Must handle all 6 Lever question widget types inside each card:
     1. `input[type="text"]` / `input[type="number"]` / `input[type="tel"]`
     2. `textarea`
     3. `select` (native `<select>`)
     4. `input[type="radio"]` (grouped by `name="cards[...][fieldN]"`)
     5. `input[type="checkbox"]` (grouped by `name="cards[...][fieldN]"`, selecting 1 semantically matched option per required card, plus `"He/him"` for `name="pronouns"`, plus EEO consent checkboxes)
     6. Additional file uploads (`input[type="file"]` for Cover Letter / Portfolio)
3. **Conditional Field Reveal**:
   - Selecting a radio option on Lever can reveal follow-up inputs inside the same card. Re-scan visible inputs after completing radio selections.
4. **Honeypot Protection**:
   - Strictly skip any input matching `[name="trap"]`, `[hp="true"]`, `.lever-trap`, or `!el.offsetParent`.

#### D. SmartRecruiters (`jobs.smartrecruiters.com/<Company>/<id>` -> `/oneclick-ui/...`)
1. **Entry CTA & 2-Step Wizard**:
   - Landing page has `a#st-apply` / `a:has-text("I'm interested")` -> navigates to `/oneclick-ui/company/<Company>/publication/<uuid>` (Step 1: Profile, Experience/Education repeaters, Resume, Message) -> `button:has-text("Next")` -> `/screening` (Step 2: Preliminary questions + Consent + `Submit`).
   - Also handle `oneclick-ui` when embedded inside an iframe or using open Shadow DOM web components (`spl-`, `oc-`).
2. **Resume Dropzone Auto-Parse Repair**:
   - Uploading the resume on Step 1 leaves `Confirm your email*` blank, `City*` blank, and often opens an incomplete Experience repeater form (`Title*` empty and `[invalid]`).
   - **Fix**: Either skip the top "Easy Apply" autofill dropzone and upload directly to the bottom `Resume *` input (so no broken repeater rows are auto-created!), OR if the autofill dropzone is used, explicitly click `Delete` / `Cancel` on any open unsaved repeater edit form (or fill `Title*`, `Company*`, `From*` and click `Save`), then fill `Confirm your email*` and `City*`.
3. **Sticky Topbar Combobox Interception**:
   - Never mouse-click floating combobox options on SmartRecruiters (`div[data-test="topbar"]` intercepts pointer events).
   - Use the **Keyboard Commit Protocol**:
     - For typed autocomplete (`City*`, `Company*`, `Major*`): Click -> type text -> wait 700ms -> press `ArrowDown` -> press `Enter`.
     - For clicked-open static dropdowns (Step 2 screening dropdowns): Click -> wait 400ms -> press `Enter` (for 1st option) or `ArrowDown` $(k-1)$ times -> `Enter`.
4. **Shadow DOM & Prose Textarea Setter**:
   - Traverse open shadow roots when inspecting `[invalid]` or required fields, and use `HTMLTextAreaElement.prototype.value` setter + `input`/`change` events for `Description` and `Message to the Hiring Team`.

---

## Part 2: The 10 Architectural Plans for 100% Universal Edge Coverage

To guarantee **120/120 (30 per ATS)** on completely unseen postings across global and Indian tech roles, we will engineer and iteratively refine a modular unified engine (`src/scripts/universal_ats_filler.py`) built on **10 concrete architectural plans**:

### Plan 1: Deep DOM & Shadow-Piercing Form Inspector (`FormGraphExtractor`)
- Build an injected JS inspection engine (`extract_form_schema(page_or_frame)`) that traverses standard DOM, `iframe#grnhse_iframe`, and open Shadow DOM roots (`spl-*`, `oc-*`).
- For every interactive control (`input`, `textarea`, `select`, `[role="combobox"]`, `.select__control`, `button[data-option]`, `fieldset`), extract:
  - `uid`, `tag`, `type`, `name`, `id`, `placeholder`, `required` (including `aria-required`, `*` in label, sibling `.requiredInput`, or Lever `.required` span), `label_text` (resolved via `label[for]`, `aria-labelledby`, `aria-label`, closest `.field` / `.application-question` / `fieldset legend` / Ashby question wrapper), `options` (for `<select>`, radios, checkboxes), `current_value`, and `is_valid`.

### Plan 2: Deterministic + Semantic Question Answering Brain (`SemanticQuestionEngine`)
- Replace naive fallback fills (`"Jay Singh"` or `"1.5"` into unknown fields) with a 120-pattern semantic classifier over `(label_text, placeholder, name, options, field_type)`:
  - **Identity & Contact**: Full Name, First/Last/Preferred Name, Email, Confirm Email, Phone (formatted per country requirement: 10-digit `8651274328` when country code is separate, `+918651274328` when combined).
  - **Location & Address**: City (`Bengaluru` / `Gaya`), State (`Karnataka` / `Bihar`), Country (`India`), Postal/Zip (`560001` / `823001`), Street Address (`Bengaluru, Karnataka, India`).
  - **Links & Portfolio**: LinkedIn, GitHub, Portfolio/Website, Other URL.
  - **Work Authorization & Sponsorship**: Authorized to work (`Yes` for India/Remote; context-aware for abroad), Visa Sponsorship (`No` if domestic/India, or matched to available option), Relocation (`Yes`), Hybrid/Onsite willingness (`Yes`).
  - **Compensation & Notice**: Current CTC (`18` or `1800000` depending on LPA vs absolute currency prompt), Expected CTC (`22` or `2200000` / `$80000` if USD prompt), Notice Period (`7` days / `Immediate` / `< 15 days` / `2 weeks`), Start Date (`YYYY-MM-DD` 7 days from today).
  - **Education & Academics**: University (`Indian Institute of Technology (IIT) Kharagpur`), Degree (`Bachelor's Degree` / `B.Tech` / `BS`), Major (`Computer Science` / `Artificial Intelligence`), GPA (`8.5` or `3.7/4.0`), Graduation Year (`2024`).
  - **Experience & Tech Stack**: YoE (`2` or `1.5`), Company (`AI-First Product Studio`), Title (`Software & ML Engineer`), Python/SQL/AWS/React/LLM years (`2`).
  - **Demographics / EEO**: Gender (`Male`), Ethnicity/Race (`Asian` / `South Asian` / `Decline to self-identify`), Hispanic/Latino (`No`), Veteran (`I am not a protected veteran` / `No`), Disability (`No, I do not have a disability` / `No`), Pronouns (`He/him`).
  - **Open-Ended Essays**: Dynamic template composer combining role title, company name, and `MASTER_PITCH` (DFR-Tracer on LangGraph, sub-second RAG, IIT Kharagpur).
  - **Option Scoring Matcher**: For any dropdown/radio/checkbox group with arbitrary tenant options, score every available option string against our semantic target preferences and pick the highest-scoring non-empty option (never blindly picking an invalid placeholder like `"Select..."` or `"--"`).

### Plan 3: Upload-First & Async Parser Synchronization Protocol (`UploadSyncManager`)
- Standardize file upload timing across all 4 platforms:
  - **Lever**: Upload resume first -> poll for `.resume-upload-success` or 3.5s settle -> fill all text/location fields after parser finishes.
  - **Ashby**: Locate `input#_systemfield_resume` (ignoring autofill dropzones) -> `set_input_files` -> wait 2.5s for `Replace`/`Delete` buttons -> fill `Email` and other fields after mutation completes.
  - **Greenhouse**: Remove any pre-attached wrong resume (`button[aria-label="Remove file"]`) -> `set_input_files` on `#resume` -> handle optional `#cover_letter` if required.
  - **SmartRecruiters**: Bypass the broken top autofill dropzone when possible by uploading directly to the bottom `Resume *` slot, OR if auto-parsed, programmatically close/repair any open `[invalid]` Experience/Education repeater edit form before filling `Confirm your email*` and `City*`.

### Plan 4: Universal Custom Combobox & Autocomplete Controller (`ComboboxController`)
- Handle all 5 distinct combobox implementations without pointer-interception or React state loss:
  1. **Greenhouse React-Select v5 (`.select__control`)**: Scroll into view -> click `.select__control` -> check `[role="option"]` list in portal/menu -> score all visible option texts via `SemanticQuestionEngine` -> if async/empty (like `Location*` or `School*`), type search token (`"India"`, `"Bengaluru"`, `"Indian Institute of Technology"`) with `delay=60` -> wait 800ms -> click best `[role="option"]` (or `ArrowDown` + `Enter`) -> verify `.select__single-value` or `.select__multi-value` is populated.
  2. **Greenhouse Classic Select2 (`.select2-container`)**: Click `.select2-choice` / `.select2-selection` -> type in `.select2-search__field` -> click `.select2-results__option` / press `Enter`.
  3. **Ashby `_combobox`**: Click `input[placeholder="Start typing..."]` -> type token slowly -> wait 800ms for `[role="option"]` -> click first match (with fallback from city `"Bengaluru, India"` to country `"India"` or `"United States"` if location-restricted).
  4. **Lever Location Autocomplete**: Click `input[name="location"]` -> type `"Bengaluru, Karnataka, India"` (`delay=70`) -> wait 800ms -> click `.dropdown-container li` / `.location-results div` if visible.
  5. **SmartRecruiters Sticky-Header Combobox**: Use strict keyboard commit (`Click -> Type -> Wait 700ms -> ArrowDown -> Enter` for searchable inputs; `Click -> Wait 400ms -> ArrowDown*(k-1) -> Enter` for static dropdowns).

### Plan 5: React 18 / Angular / Web-Component Native Value Setter & Event Dispatcher
- Implement a universal `safe_fill_text(locator, value)` that combines:
  - Focus + clear + human-paced typing for short fields (`< 60` chars).
  - Two-phase native prototype value setter (`'x'` -> `targetValue`) with `input`, `change`, and `blur` event synthesis for long prose (`>= 60` chars) and React 18 / SmartRecruiters Stencil textareas.

### Plan 6: Group-Scoped Radio, Yes/No Button & Multi-Checkbox Resolver
- **Never** iterate over raw `input[type="checkbox"]` or `input[type="radio"]` globally.
- Group by question container (`fieldset`, `.application-question`, `.field`, Ashby field entry wrapper):
  - **Ashby Yes/No Buttons**: Detect pairs of `<button>` inside a question block (`Yes` / `No` or `data-option`) -> click the semantically appropriate button -> verify `aria-pressed="true"` or active class.
  - **Radio Groups**: Group by `name` attribute -> read all option labels -> pick best semantic match -> click its `<label>` or `.check(force=True)`.
  - **Checkbox Groups**:
    - If single consent/privacy/acknowledgment checkbox -> check it.
    - If multi-option screening question (`"Which languages..."`, `"Pronouns"`, `"Race/Ethnicity"`) -> check **only** the 1–2 options that match the candidate profile (e.g. `Python`, `He/him`, `Asian`, `Yes`, `I agree`), never conflicting boxes.

### Plan 7: Multi-Step Wizard & Conditional Field Reveal Loop (`StateMachineLoop`)
- After the initial top-to-bottom fill pass:
  - Run a **Second Reveal Pass** to catch conditional fields that appeared after clicking `"Yes"` radios or selecting dropdown options (common on Lever, Greenhouse, and Ashby).
  - On **SmartRecruiters**, execute Step 1 fill -> verify zero `[invalid]` elements on Step 1 -> click `Next` -> wait for `/screening` Step 2 -> execute full fill & combobox pass on Step 2.

### Plan 8: Pre-Submit `:invalid` & Missing-Required Self-Healing Auditor (`ValidationHealer`)
- Before (or without) clicking final Submit, run a comprehensive DOM + HTML5 + ATS-specific validation audit:
  1. Check `form.checkValidity()` and enumerate all `:invalid` elements, `[aria-invalid="true"]`, `.select__control--error`, `.field-error`, and Ashby/Lever required containers lacking values.
  2. For every flagged control, run targeted remediation (e.g., if a React-Select requiredInput is still invalid, re-open `.select__control`, read all options, and click the first valid option; if a SmartRecruiters repeater is stuck open in edit mode, fill its missing required child inputs or click Cancel/Save; if a date input rejected `MM/DD/YYYY`, retry with `YYYY-MM-DD`).
  3. Assert **100% required fields filled (`empty_required == 0` and `invalid_count == 0`)**.

### Plan 9: Anti-Bot Stealth, Behavioral Telemetry & CAPTCHA/OTP Handling
- Enforce the mandatory anti-bot protocol on every application:
  - Stealth Chromium args + isolated CDP init scripts masking `navigator.webdriver`.
  - `human_scroll_4x` on every page load (`25% -> 50% -> 75% -> 100% -> 0%`).
  - Sequential top-to-bottom interaction with randomized delays.
  - Automatic `otp_listener.py` integration when Greenhouse email security codes are triggered.

### Plan 10: Strict Train / Test Dataset Separation & 120-Application Evaluation Harness
- **Dataset Construction**:
  - Discover and verify **live, active** URLs for all 4 platforms:
    - **Training & Debugging Pool**: 15–20 diverse jobs per platform (60–80 jobs total) used iteratively to expose edge cases, inspect DOM snapshots, and refine Plans 1–9.
    - **Hold-Out Evaluation Pool (120 Unseen Applications)**: Strictly **30 Ashby + 30 Greenhouse + 30 Lever + 30 SmartRecruiters** completely new, unseen live postings that are never touched during training/debugging.
- **Verification Criteria**:
  - For every job in the 120-job evaluation set, verify that:
    1. Every required field (text, email, phone, location, resume, custom dropdowns, radios, checkboxes, repeaters, essays, Step 2 screening questions) is filled.
    2. Pre-submit validation audit passes with **0 empty required fields and 0 `:invalid` controls** (or full form submission reaches confirmation / final review step with zero validation errors).
    3. Every run is logged with full field-by-field telemetry and screenshots in `src/knowledge_source/ats_mastery_log.md` and `src/application_progress/120_eval_results.json`.
