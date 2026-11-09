# Ripplehire ATS Application Observations

- **Platform**: Ripplehire (*.ripplehire.com)
- **Architecture**: Single Page Application (Backbone.js + Marionette + RequireJS + Bootstrap / Metronic)
- **Driver Used**: Playwright MCP (`microsoft/playwright-mcp`)
- **Flow Shape & Step Count**:
  1. Job Details page (`#detail/job/<jobId>`) -> click "Apply Now"
  2. Privacy Policy / Notice modal -> click "I Agree"
  3. Single-page comprehensive application form (`#apply/job/<jobId>`) with 4 visual sections:
     - Resume
     - Personal Details
     - Professional Details
     - Self disclosure
  4. Terminal action: "Submit Application" button (`#btn-submit-app`)
- **Widget Quirks & Validation Traps**:
  - **Resume Upload**: Uses a Backbone modal (`ResumePopup`) that stores the uploaded file in `window.globalResumeFile` and attaches it to `view.model.set('resume', file)`. Files must be valid PDF (`%PDF` magic bytes) and under 3MB.
  - **Location (`indiaLocation`)**: Attached to a Bootstrap 3 Typeahead. Value requires a 3-part or known string (e.g., `Gaya, Bihar, India`) and must be set on both the input element and the Backbone model directly to clear `indiaLocation` pre-validation.
  - **Conditional Fields**:
    - `custom1` ("Have you worked with us before?"): If "No", employee ID field `custom2` is given `.hide` class and excluded from validation.
    - `noticePeriodSelect`: If set to `0` ("Can join immediately"), `noticePeriodEndDate` is automatically hidden and excluded from validation.
  - **CTC Fields**:
    - `currentCTC` & `expectedCTC`: Plain numeric fields in INR format (e.g. `1800000`, `2200000`).
  - **Anti-bot compliance**:
    - 4 smooth viewport scrolls (25%, 50%, 75%, 100%) and 800ms-2200ms human-like delays must be used between fields.
    - Terminal step stops right before final submission, staged as `READY FOR HUMAN SUBMISSION`.
