const fs = require('fs');
const AP = 'src/application_progress/ats_progress.json';
const JL = 'src/job_search_results/job_links.json';
const a = JSON.parse(fs.readFileSync(AP, 'utf8'));
a.applied.push({
  company: 'Rzr',
  role: 'Rzr posting 4241380009 (title not captured during fill; URL is evidence)',
  url: 'https://job-boards.greenhouse.io/rzr/jobs/4241380009',
  platform: 'greenhouse',
  location: 'Unspecified (form Country combobox set; phone country India +91)',
  resume: 'GenAI_DS (Jay Resume GenAI+DS 5th Aug.pdf, filename + Remove button visible pre-submit)',
  status: 'applied',
  exp: '18mo (2026-10-14 fresher bulk per auto-submit authority)',
  salary: 'Expected 22-26 LPA (negotiable); Current CTC 0; Joining Immediate; Relocate Yes (all per profile, verified pre-submit)',
  verification: "SUBMITTED 2026-10-14: URL https://job-boards.greenhouse.io/rzr/jobs/4241380009/confirmation + title 'Thank you for applying' + body 'your application has landed safely with us. Our team will review it shortly.'",
  applied_date: '2026-10-14',
  submitted_by: 'greenhouse-fill finisher per src/submit_permisssions/ashby_greenhouse_lever_submit_authority.json (allow_submit true)'
});
a.applied.push({
  company: 'Enterpret',
  role: 'Posting 7847134003 (per prior agent)',
  url: 'https://job-boards.greenhouse.io/enterpret/jobs/7847134003',
  platform: 'greenhouse',
  location: 'Unspecified',
  resume: 'GenAI_DS',
  status: 'applied',
  exp: '18mo (per prior agent)',
  salary: 'Per profile (per prior agent)',
  verification: 'Per prior agent: confirmation URL + received text, tab closed. NOT independently re-verified by finisher.',
  applied_date: '2026-10-14',
  submitted_by: 'prior agent (finisher ensured ledger entry only)'
});
a.blocked.push({
  company: 'DoorDash India',
  role: 'Software Engineer, Backend (Pune)',
  url: 'https://job-boards.greenhouse.io/doordashindia/jobs/5856393',
  platform: 'greenhouse',
  location: 'Pune, India',
  status: 'blocked_parallel_agent_contention',
  reason: 'STAND_DOWN by finisher: (1) standing 2026-10-06 recon verdict SKIP LEVEL 3Y_GAP + DOMAIN (3+y Backend, Go/Java/Spark data-infra) still applies vs 18mo profile; (2) a parallel agent is filling the SAME tab (attached Resume ML_Vision_RL_PPO + set Degree=Bachelor while finisher filled text batch + phone +91) -> double-submit risk; (3) shared-browser contention beat every select+act pair, guarded submit unsafe. Filled before stand-down: First/Last/Email/Phone(+91)/LinkedIn/Location-Gaya+relocate-Pune/Comp 22-26/Notice Immediate; fixed First Name JayJay->Jay. Needs orchestrator call before any submit.',
  resume: 'CONTESTED: finisher tasked GenAI_DS; tab currently holds ML_Vision_RL_PPO 7th Aug.pdf (parallel agent)',
  date: '2026-10-14'
});
fs.writeFileSync(AP, JSON.stringify(a, null, 2));
const j = JSON.parse(fs.readFileSync(JL, 'utf8'));
j['Rzr'] = 'https://job-boards.greenhouse.io/rzr/jobs/4241380009';
j['Enterpret'] = 'https://job-boards.greenhouse.io/enterpret/jobs/7847134003';
j['DoorDash India Backend'] = 'https://job-boards.greenhouse.io/doordashindia/jobs/5856393';
fs.writeFileSync(JL, JSON.stringify(j));
console.log('checkpoint ok: applied=' + a.applied.length + ' blocked=' + a.blocked.length + ' links=' + Object.keys(j).length);
