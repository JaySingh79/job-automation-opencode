## iCIMS Platform Observations (MSCI Services Tenant)

1. **Architecture & Iframe**: The primary job post and application form reside inside an iframe (`#icims_content_iframe` / `iframe[name="icims_content_iframe"]`). Sub-actions and snapshots must target this iframe.
2. **Initial Entry Point**: The job description page displays an "Apply" button inside the iframe linking to `.../job?mode=apply&apply=yes&in_iframe=1`.
3. **GDPR / Login Screen**: The first gate asks for candidate email (`#email`, name `css_loginName`) and a mandatory privacy notice consent checkbox ("I consent"). Submitting this triggers the first interactive **hCaptcha** image challenge modal.
4. **Step 1 - Candidate Profile & Resume Upload**:
   - Resume upload is triggered via `<input type="file" id="PortalProfileFields.Resume_File">`. Its `onchange` handler posts the form with `uploadResume=1` which parses the PDF and prefills candidate fields (name, email, login).
   - Custom iCIMS dropdowns are managed by the global `ICIMS.dropdowns` registry (e.g. `ICIMS.dropdowns['-1_PersonProfileFields.AddressCountry']`). Selecting an option requires matching the AJAX/value pair (`13228` for India, `13233` for Bihar, `36891` for SMS consent Yes).
5. **Step 1 Submit / Second Anti-Bot Interception**:
   - Clicking "Submit Profile" (`#cp_form_submit_i`) invokes a secondary invisible/interactive **hCaptcha** challenge ("Tap on buildings that commonly have the feature shown").
   - Automated fill pauses here as the human must solve the second CAPTCHA challenge before advancing to Step 2 (Candidate Questions).
