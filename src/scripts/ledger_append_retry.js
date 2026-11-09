const fs = require('fs');
const p = 'D:/Projects/PRACTICE/firecrawl_test/src/applied/jobs_applied.json';
const d = JSON.parse(fs.readFileSync(p, 'utf8'));
d.wellfound.push(
  {company: 'Scribie', role: 'Data Ops Engineer', location: 'Bangalore Urban (Hybrid)', salary: 'listing stipend', url: 'https://wellfound.com/jobs/3544397-data-ops-engineer', status: 'applied', date: '2026-09-26', note: 'RETRY: prior Send, verify now; disabled Applied x2; 1-2y'},
  {company: 'Bydek', role: 'ETL Engineer (Python Airflow)', location: 'Bangalore Urban (In office)', salary: 'Rs.5L-8L', url: 'https://wellfound.com/jobs/4152820-etl-engineer-python-airflow', status: 'applied', date: '2026-09-26', note: 'RETRY queue: 3y soft YoE, floor waived; Variant B; disabled Applied x2'}
);
fs.writeFileSync(p, JSON.stringify(d, null, 2));
console.log('wellfound len now ' + d.wellfound.length);
const q = 'D:/Projects/PRACTICE/firecrawl_test/src/job_search_results/job_links.json';
const j = JSON.parse(fs.readFileSync(q, 'utf8'));
j['Scribie'] = 'https://wellfound.com/jobs/3544397-data-ops-engineer';
j['Bydek-ETL'] = 'https://wellfound.com/jobs/4152820-etl-engineer-python-airflow';
j['Teal India'] = 'https://wellfound.com/jobs/4246035-data-engineer-yoe-0-2';
fs.writeFileSync(q, JSON.stringify(j, null, 2));
console.log('job_links updated');
const r = {
  run: 'wellfound_retry_2026-09-26',
  date: '2026-09-26',
  authority: 'src/submit_permisssions/wellfound_submit_authority.json allow_submit:true',
  mode: 'RETRY STUCK + relaxed aggressive queue',
  verified: [{company: 'Scribie', role: 'Data Ops Engineer', url: 'https://wellfound.com/jobs/3544397-data-ops-engineer', evidence: 'buttons [Applied|dis=true] x2', n: 33}],
  applies: [{company: 'Bydek', role: 'ETL Engineer (Python Airflow)', url: 'https://wellfound.com/jobs/4152820-etl-engineer-python-airflow', evidence: 'buttons [Applied|dis=true] x2', variant: 'B', n: 34}],
  skipped: [{id: '3757034', company: 'AuxoAI', role: 'Senior Data Engineer AWS', reason: 'SENIOR_TITLE + 5Y_GAP (6-9y) + INFRA_MISMATCH'}],
  external_deferred: [{id: '4246035', company: 'Teal India', role: 'Data Engineer YOE 0-2', reason: 'EXTERNAL_FLOW: Apply Here ATS link in JD'}],
  done_after: 34
};
fs.writeFileSync('D:/Projects/PRACTICE/firecrawl_test/runs/wellfound_retry_2026-09-26.json', JSON.stringify(r, null, 2));
console.log('run file written');
