# Zoho Recruit ATS Automation Notes & Observations

## Flow Shape
- **Architecture**: Single-page application using Zoho's custom Web Components framework (`lyte-*` and `crux-*` custom elements).
- **Embedded vs Direct**: Mostly direct web component forms on company subdomains (`*.zohorecruit.in/jobs/Careers/*`), though legacy portals or external embeds may use `#recruit_iframe`.
- **Step count**: Typically 1 step (all sections rendered on a single scrolling page: Basic Info, Address Info, Professional Details, Attachments, Consent/Captcha).
- **Terminal step**: Direct "Submit Application" or "I'm interested" / Captcha confirmation.

## Widget Quirks & Selectors
- **Deterministic Selectors**: All standard and custom form inputs have `data-zcqa` attributes:
  - Text fields: `[data-zcqa="manual_First_Name"] input`, `[data-zcqa="manual_Last_Name"] input`, `[data-zcqa="manual_Email"] input`, `[data-zcqa="manual_Mobile"] input`.
  - Dropdowns: `lyte-dropdown` triggered by `[data-zcqa="manual_<field>"]` (e.g. `[data-zcqa="manual_Branch_of_Study"]`, `[data-zcqa="manual_Current_Job_Title"]`).
  - Dropdown options: Rendered as `lyte-drop-item` elements upon click.
  - File upload: File input inside `rec-file-upload-component` (e.g. `[data-zcqa="rec_RESUME"] input[type="file"]`). Can be directly targeted via Playwright's `.setInputFiles()`.
  - Captcha: Handled via `[data-zcqa="rec_$Captcha"]` (`rec-captcha-component`). When present, requires human solving.

## Validation & Freeze Layers
- **Cookie Consent**: An overlay `<div class="cw-cookie-freeze-layer">` intercepts pointer events until "Accept all" (`button:has-text("Accept all")`) is clicked. Must be dismissed before clicking "Apply Now" or "I'm interested".
- **Bot Emulation Rules**:
  - Smooth viewport scrolling across 4 depth levels (25%, 50%, 75%, 100%).
  - Sequential top-to-bottom field entry with 800ms-2200ms randomized pauses.
  - Never trigger final submission without human review.

## Driver
- `playwright-mcp` (Playwright v1.x)
