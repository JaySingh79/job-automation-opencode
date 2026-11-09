# Amazon Jobs ATS Platform Bottlenecks & Hard Limits

## 1. 10 Active Applications Hard Cap
- **Observed**: 2026-10-21 on candidate account `jays.iitkgp@gmail.com`.
- **Error Trigger**: Navigating to `https://www.amazon.jobs/applicant/jobs/<jobId>/apply` when 10 applications are active.
- **Server Redirect**: Redirects immediately to:
  `https://www.amazon.jobs/en-US/applicant/jobs/<jobId>/summary?result=application_limit_reach`
- **Banner Message**:
  > "You've reached the maximum number of job applications. Looks like you've hit the limit of 10 job applications. If you want to apply for another job, withdraw an existing one from your Application Dashboard."
- **Mitigation / Next Step**:
  Candidates must inspect their active application dashboard (`/applicant/dashboard/applications`) and withdraw older or closed applications (e.g. roles marked "We’re not taking new applications for this job right now") to free up capacity for fresh target roles.

## 2. Authentication & SSO Flow
- Entry URL: `https://www.amazon.jobs/applicant/jobs/<id>/apply` redirects to `https://passport.amazon.jobs/` and then to Amazon IdPrism (`https://atozpublic.idprism-auth.amazon.com/`).
- IdPrism requires either user password or Email OTP verification code sent to candidate's registered email (`j******gp@gmail.com`).
- Once authenticated in a session, cookies persist across direct applicant URLs (`/en-US/applicant/jobs/<id>/apply`).

## 3. Custom Radio Interception Trap
- Amazon application wizard uses Bootstrap custom radio components where `<label class="custom-control-label" for="...">` visually intercepts pointer events over `<input type="radio">`.
- Attempting direct Playwright `click()` on the `<input>` element triggers 5000ms timeout due to pointer-events interception.
- Reliable solution: Click the associated `<label>` element or invoke `.click()` via DOM execution.
