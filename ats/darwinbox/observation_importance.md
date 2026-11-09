# Darwinbox Candidate Experience Platform Observation & Notes

## Platform Overview
- **Domain Pattern**: `<company>.darwinbox.in` (e.g., `codingninjas.darwinbox.in`, `hrmsashoka.darwinbox.in`, `upstox.darwinbox.in`)
- **Portal URL Pattern**: `/ms/candidatev2/main/careers/jobDetails/<job_hash>`
- **Driver**: `playwright-mcp`

## Flow & Architecture
1. **Public Job Landing**:
   - The job description page is publicly visible with job details, department, experience requirements, and an `Apply Now` button (`data-testid="job-details-apply-now-btn"`).
2. **Mandatory Candidate Authentication Gate**:
   - Clicking `Apply Now` immediately redirects to tenant-level auth: `/ms/candidatev2/main/auth/login`.
   - Darwinbox accounts appear to be tenant-scoped (e.g. `This account does not exist` on Coding Ninjas even if registered on another Darwinbox instance).
   - Auth options:
     - `Sign In with Google` / `Sign In with LinkedIn` (OAuth SSO)
     - Email ID + Password
     - `Sign Up` link (`data-testid="auth-login-signup-link-btn"`) pointing to `/ms/candidatev2/main/auth/register`
3. **Bot Mitigation & Challenges**:
   - Repeated login attempts or standard automation triggers a `"Perform Captcha"` challenge on the login form.
   - Registration requires password confirmation and terms acceptance.

## Traps & Quirks
- **Tenant Isolation**: Unlike Greenhouse or Ashby where a candidate can submit directly on a job form without an account, Darwinbox v2 candidate portal mandates creating a tenant-specific account before exposing the application form fields.
- **Direct Email Submissions**: Some academic/research postings (e.g., Ashoka University) explicitly instruct candidates to email CVs directly to PIs with specific subject headers and deadlines, bypassing the portal.
