# Zoho Recruit — WebFormServeServlet (rid) — Observations 2026-09-24

## Fingerprint
- Host: `careers.zohorecruit.com/recruit/WebFormServeServlet?rid=<hex>gid<hex>`
- Not a standard ATS (not Greenhouse/Lever/Workday/SuccessFactors). Single-page Zoho CRM WebForm, 1 step, no wizard, Submit directly creates Lead.
- Legacy forms: vintage 2021 (Year of Passing 2016-2019, Source list 40+ internal codes like "ZB - TSE - 7 July 2021", "AP - Arun"). Still live (200 OK) but **EXPIRED** for 2026 grads.
- 5 rids from `runs/fresher_50_lanes/zoho.json` all return 200 with form, no 403/bot wall.

## Flow shape
- 1 page only (Page 1 of 1). No pagination, no review step. Submit = final. Per G1 never click Submit.
- Fields are native `<input type=text>` + `<select>` (native) + one file `<input type=file>` hidden behind `<a>Browse</a>` trigger. No combobox autocomplete — use `browser_select_option`.
- Honeypots: 12 hidden inputs (`depid`, `xnQsjsdp`, `xmIwtLD` containing rid fragments, `depmodule=Leads`, etc.) — must NOT fill (flag honeypot true).

## Required fields per form (verified via webfetch + Playwright snapshot + reconFn)

1) rid=5e90d838... (Software Developer) — **SDE-aligned but EXPIRED**
   - Name* textbox maxlength 125, Phone* 30, Email* 255, How do you know* select [None/Facebook/Instagram/Employee Referral], Year of Passing* select [None/2016-2019] ← no 2025/2026 option → BLOCKED, Relevant Experience* select [None/Fresher/1/2/3+], Resume* file.
   - Gaps: YOP cannot be answered truthfully (graduation 2026). QUEUE YOP. Source hidden. How-know has no LinkedIn option; profile source=LinkedIn not mappable → QUEUE or leave None. Relevant Experience maps to "Fresher" (profile 18mo but role fresher-tagged).
   - Driver: playwright-extention (stable) + playwright-mcp (polluted by parallel Lever tabs — isolate Zoho).
   - Screenshot: `src/accessability_snapshot/Zoho_Software_Developer/fullPage.png`

2) rid=de2dbddf... (Technical Support Engineer Tenkasi, 0-2y)
   - JD: Zoho Desk support, night shift, Tenkasi. Not SDE/AI/ML → SKIPPED per fresher filter (DOMAIN).
   - Fields: Name*, Phone*, Email*, Years of Experience* [None/Fresher/1-2/2-3...10+], Willingness Night Shift* [Yes/No], Resume*.
   - Snapshot: `Zoho_TSE_Tenkasi/snapshot.yml`

3) rid=655c1479... (Registration Form — TSE CCNA)
   - JD: voice/email/chat support, demos, RFI, POC. Skills Eg CCNA/ITIL/CCNP. TSE → SKIPPED.
   - Fields: Name*, Email*, Phone*, Current Company*, Years of Experience* [Fresher/1-2], Skills (optional), International Calling Experience* [None/Fresher/0-1...15+], Night Shift* [Yes/No], Resume*.
   - Snapshot: `Zoho_TSE_CCNA_Form/snapshot.yml`

4) rid=30c916b3... (Registration Form — TSE multi-field)
   - JD: calls/emails, screen-share, C/C++/Java asset. TSE → SKIPPED.
   - Fields: Name*, Email*, Phone*, Official DOB* (mm/dd/yyyy), Gender* [Male/Female], Current/Previous Company*, Years of Experience*, Current Location*, Current/Previous CTC* [None/Not Applicable/1-2 LPA...Above 10], Expected CTC* [None/Open/1-2...], Preferred Work Location* [Tenkasi/Chennai...Any], Attend Zoho interview last 6M?* , Notice Period* [Immediate...90 Days], Resume*.
   - Snapshot: `Zoho_TSE_MultiField/snapshot.yml`

5) rid=c70d85cd... (Zoho | Content Writer, Chennai 0-4y)
   - JD: marketing/content, 2021 instructions, 2022 graduates not eligible. Marketing → SKIPPED.
   - Fields: Name*, Email*, Mobile*, Experience* [None/0-1..7-8], Current/Last Company, College*, Department/Specialization*, Year of passing* (textbox), Native Location*, Attended Zoho interview 6M?* [Yes/No], Resume*.
   - Snapshot: `Zoho_Content_Writer/snapshot.yml`

## Widget quirks
- Year of Passing (Form1) only 2016-2019 → any 2024+ candidate blocked. Do not invent 2019.
- All selects include "None" placeholder which is technically a value but semantically empty — recon counts empty_required only when value=="" ; leaves "None" as filled.
- Resume trigger is `<a href="javascript:void(0)">Browse</a>` → must click then `browser_file_upload` with absolute path. Hidden file input `name=theFile_property(Resume)`.
- No OTP/CAPTCHA, no auth wall, no GEO block, no bot protection observed.
- Page is static; after fill no conditional reveals. Verify via reconFn empty_required + screenshot slice for hidden validation (none found).

## Cost / time
- Scout 5 URLs via webfetch <5s. Browser recon 5 pages ~30s total (extension driver). Tab pollution from parallel Lever/Greenhouse runs can hijack MCP driver — use extension for Zoho isolation.

## Recommendation
- Only Form1 is SDE-relevant but expired → mark BLOCKED EXPIRED, do not submit. Others SKIPPED DOMAIN per fresher SDE/AI/ML filter. If Zoho re-issues SDE form with YOP 2024-2026, resume GenAI_DS (130007 bytes, %PDF) is ready, plan: Name=Jay Singh, Phone=8651274328, Email=jays.iitkgp@gmail.com, How-know→QUEUED, YOP→QUEUED, Relevant Experience=Fresher, Resume upload via Browse.
