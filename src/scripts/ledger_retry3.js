const fs = require('fs');
let p = 'D:/Projects/PRACTICE/firecrawl_test/src/application_progress/wellfound_progress.json';
let d = JSON.parse(fs.readFileSync(p, 'utf8'));
for (const s of ['4354439 Wajeeh-CLOSED_410', '4754610 Steps-SDE-MUSTHAVE_2-4Y_FULLSTACK_GAP']) if (!d.skipped.includes(s)) d.skipped.push(s);
d.done = d.applied.length;
fs.writeFileSync(p, JSON.stringify(d, null, 2));
console.log('progress done=' + d.done + ' skipped=' + d.skipped.length);
let rp = 'D:/Projects/PRACTICE/firecrawl_test/runs/wellfound_retry_2026-09-26.json';
let r = JSON.parse(fs.readFileSync(rp, 'utf8'));
r.verified = [{company: 'Scribie', role: 'Data Ops Engineer', url: 'https://wellfound.com/jobs/3544397-data-ops-engineer', evidence: 'buttons [Applied|dis=true] x2', n: 33}];
r.applies = [
  {company: 'Bydek', role: 'ETL Engineer (Python Airflow)', url: 'https://wellfound.com/jobs/4152820-etl-engineer-python-airflow', evidence: 'buttons [Applied|dis=true] x2', variant: 'B', n: 34},
  {company: 'Spheresmith', role: 'AI Engineer', url: 'https://wellfound.com/jobs/4670227-ai-engineer', evidence: 'buttons [Applied|dis=true] x2', variant: 'A', n: 35}
];
r.skipped = [
  {id: '3757034', company: 'AuxoAI', reason: 'SENIOR_TITLE + 6-9y (5Y_GAP) + INFRA_MISMATCH'},
  {id: '4391339', company: 'TRAKO', reason: 'CLOSED (listing no longer available)'},
  {id: '4354439', company: 'Wajeeh', reason: 'CLOSED_410'},
  {id: '4754610', company: 'Steps AI', reason: 'MUSTHAVE_2-4Y_FULLSTACK_GAP: Only-apply-if 1-2y prod full-stack + must-have 2-4y; 18mo ML/DS, no prod RBAC/TS claim'}
];
r.external_deferred = [{id: '4246035', company: 'Teal India', reason: 'EXTERNAL_FLOW: Apply Here ATS link in JD'}];
r.done_after = 35;
fs.writeFileSync(rp, JSON.stringify(r, null, 2));
console.log('run file updated');
