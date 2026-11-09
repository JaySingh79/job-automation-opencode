const fs = require('fs');
const path = require('path');
const root = 'D:\\Projects\\PRACTICE\\firecrawl_test';
const date = '2026-10-06';

const entries = [
  { n: 1, company: 'Epifi', role: 'AI Engg Intern', url: 'https://jobs.lever.co/epifi/08c743e8-2b29-4f78-827e-5bd90476ed86', platform: 'lever', status: 'blocked_dead_req', reason: 'BLOCKED-dead_req: browser tab navigate returns 404 status + Lever 404 page (heading 404, This job does not exist, Find similar jobs). No form. Matches Oct-04 Epifi dead sweep pattern.', resume: 'GenAI_DS (not uploaded - no form)' },
  { n: 2, company: 'Epifi', role: 'GenAI Product Builder Intern', url: 'https://jobs.lever.co/epifi/4f5b7548-ea0a-4be0-816b-11d712853169', platform: 'lever', status: 'blocked_dead_req', reason: 'BLOCKED-dead_req: browser new-tab navigate returns 404 status + 404 error title. No form.', resume: 'GenAI_DS (not uploaded - no form)' },
  { n: 3, company: 'Merkle Science', role: 'Software Engineer (Intern) - Backend', url: 'https://jobs.lever.co/merklescience/e663b69b-264a-4bd7-b04d-fb3c0a824a28', platform: 'lever', location: 'Bangalore Hybrid', status: 'skipped', reason: 'LEVEL_MISMATCH eligibility: JD requires final-year graduating 2027, IIT/NIT/IIIT only, CSE/IT branches only; user B.Tech Apr 2026 Metallurgical. Plus 1yr duration + 2yr service lock-in. Python/Django stack matches but eligibility excludes.', resume: 'GenAI_DS (not uploaded per skip rule)' },
  { n: 4, company: 'Weekday', role: 'Software Engineer Intern (client role)', url: 'https://jobs.lever.co/weekdayworks/a86efff4-1c2e-43fc-8ecb-dc8f873db2f1', platform: 'lever', location: 'Bengaluru Remote', status: 'skipped', reason: 'SALARY_FLOOR: 3-6 LPA band (top 6L << 22L floor), generic SWE not AI/ML-exact. Min exp 0y fits but pay+domain fail.', resume: 'GenAI_DS (not uploaded per skip rule)' },
  { n: 5, company: 'Jobgether', role: 'AI Engineer SaaS LLMs', url: 'https://jobs.lever.co/jobgether/d82c04af-d553-4b47-8faf-108525cf48d2', platform: 'lever', status: 'blocked_dead_req', reason: 'BLOCKED-dead_req: browser new-tab navigate returns 404 status + 404 error title. No form.', resume: 'GenAI_DS (not uploaded - no form)' },
  { n: 6, company: 'Jobgether', role: 'Associate Engineer', url: 'https://jobs.lever.co/jobgether/e8d2c4aa-e042-44a9-9db1-57ece49ca68a', platform: 'lever', status: 'blocked_dead_req', reason: 'BLOCKED-dead_req: browser new-tab navigate returns 404 status + 404 error title. No form.', resume: 'GenAI_DS (not uploaded - no form)' },
  { n: 7, company: 'Veeva', role: 'Associate Software Engineer - Test Automation', url: 'https://jobs.lever.co/veeva/d0704c83-8c0f-4545-8a40-eb48bcfec299', platform: 'lever', location: 'Hyderabad On-site', status: 'skipped', reason: 'DOMAIN_OR_INFRA_MISMATCH: QA/Test Automation (Selenium/Cucumber/CI), Java-strong, 1+ y test-automation; no AI/ML, no Python. As predicted.', resume: 'GenAI_DS (not uploaded per skip rule)' },
  { n: 8, company: 'OutcomesAI', role: 'Backend / ML-Ops Engineer - Speech Model Deployment & Inference Optimization', url: 'https://jobs.lever.co/outcomesai/7bbc10a3-805c-441a-8c58-44ab9be9c73c/apply', platform: 'lever', location: 'Bengaluru On-site, Gen AI', status: 'partial_texts_filled_upload_queued', reason: 'STRETCH FLAGS (human decides submit vs abandon): JD wants 4-6y backend/MLOps + 1-2y GPU inference (Triton/TensorRT/K8s/speech) vs 18mo; B.Tech CS vs Metallurgical; MLOps/infra-leaning vs RAG/agents profile. 8 text fields filled via fill_form (URL-verified); resume upload + location re-verify NOT done (shared-browser contention); Submit NOT clicked.', resume: 'GenAI_DS (130007 bytes %PDF verified, upload QUEUED)', filled: ['Full name Jay Singh', 'Email jays.iitkgp@gmail.com', 'Phone +91-8651274328', 'Current location Gaya, Bihar', 'Current company Pibit AI (YC W21)', 'LinkedIn', 'GitHub', 'Portfolio'], queued: 'Attach GenAI_DS resume; re-verify Current location (Lever clear-bug); optional OutcomesAI/Twitter textboxes left blank; confirm stretch flags then human Submit' },
  { n: 9, company: 'Lingaro', role: 'ML/AI Engineer (India Remote)', url: 'https://jobs.lever.co/lingarogroup/5b9bd5a9-5953-43cf-a7e5-fe9161ac0f21/apply', platform: 'lever', location: 'India Remote', status: 'skipped', reason: 'LEVEL_MISMATCH 5Y_GAP + DOMAIN: 5+ y Microsoft Copilot Studio/Azure AI Foundry/Power Platform vs 18mo Python GenAI; MS-stack, no Python.', resume: 'GenAI_DS (not uploaded per skip rule)' },
  { n: 10, company: 'Lingaro', role: 'unknown (ID 7d57cc12)', url: 'https://jobs.lever.co/lingarogroup/7d57cc12-70c0-40a9-97be-cc9d275371fd/apply', platform: 'lever', status: 'blocked_dead_req', reason: 'BLOCKED-dead_req: GET returns non-2xx 404 (verified via fetch). No form.', resume: 'GenAI_DS (not uploaded - no form)' },
  { n: 11, company: 'Lingaro', role: 'unknown (ID a2aaf267)', url: 'https://jobs.lever.co/lingarogroup/a2aaf267-efdc-4ea2-8660-b06cb0b0f9b3/apply', platform: 'lever', status: 'blocked_dead_req', reason: 'BLOCKED-dead_req: GET returns non-2xx 404 (verified via fetch). No form.', resume: 'GenAI_DS (not uploaded - no form)' },
  { n: 12, company: 'Lingaro', role: 'ML/AI Engineer - Peepal Consulting (India Remote)', url: 'https://jobs.lever.co/lingarogroup/6adf8593-2a35-44d0-9400-0ced651fd403/apply', platform: 'lever', location: 'India Remote', status: 'skipped', reason: 'LEVEL_MISMATCH 6Y_GAP + DOMAIN: 6+ y Copilot Studio/Azure AI Foundry vs 18mo; MS-stack.', resume: 'GenAI_DS (not uploaded per skip rule)' },
  { n: 13, company: 'Lingaro', role: 'ML/AI Engineer - Adecco (India Remote)', url: 'https://jobs.lever.co/lingarogroup/18f8d2c5-b52a-4d9f-b4ff-3f71e0fee53d/apply', platform: 'lever', location: 'India Remote', status: 'skipped', reason: 'LEVEL_MISMATCH 6Y_GAP + DOMAIN: 6+ y Copilot Studio/Azure AI Foundry vs 18mo; MS-stack.', resume: 'GenAI_DS (not uploaded per skip rule)' }
];

const run = { run: 'fresher_100_fill_lever_2026-10-06', date, driver: 'playwright-mcp (browser fills) + fetch (JD recon under contention)', counts: { total: 13, blocked_dead_req: 6, skipped: 6, partial_texts_filled: 1, ready_for_human_submission: 0, submitted: 0 }, resume_bytes_verified: { GenAI_DS: 130007, ML_Vision: 123104, ML_Vision_RL: 122836, magic: '%PDF' }, entries };

// 1. runs checkpoint
fs.mkdirSync(path.join(root, 'runs'), { recursive: true });
fs.writeFileSync(path.join(root, 'runs', 'fresher_100_fill_lever_2026-10-06.json'), JSON.stringify(run, null, 2));
console.log('runs checkpoint written');

// 2. snapshots
const snaps = [
  ['page-2026-10-06T08-02-01-863Z.yml', 'MerkleScience', 'recon'],
  ['page-2026-10-06T08-02-39-419Z.yml', 'Weekday', 'recon'],
  ['page-2026-10-06T08-04-21-555Z.yml', 'Veeva', 'recon'],
  ['page-2026-10-06T08-05-09-268Z.yml', 'OutcomesAI', 'apply-form-prefill']
];
for (const [f, co, kind] of snaps) {
  const src = path.join(root, '.playwright-mcp', f);
  const dir = path.join(root, 'src', 'accessability_snapshot', co);
  fs.mkdirSync(dir, { recursive: true });
  if (fs.existsSync(src)) { fs.copyFileSync(src, path.join(dir, kind + '-2026-10-06.yml')); console.log('copied', co); }
  else console.log('MISSING src snapshot', f);
}

// 3. ats_progress.json
const apPath = path.join(root, 'src', 'application_progress', 'ats_progress.json');
const ap = JSON.parse(fs.readFileSync(apPath, 'utf8'));
ap['lever_fill_2026-10-06'] = entries.map(e => ({ company: e.company, role: e.role, url: e.url, platform: e.platform, location: e.location || '', status: e.status, reason: e.reason, resume: e.resume, ...(e.filled ? { filled: e.filled } : {}), ...(e.queued ? { queued: e.queued } : {}), date }));
for (const e of entries) {
  if (e.status === 'blocked_dead_req') ap.blocked.push({ company: e.company, role: e.role, url: e.url, platform: e.platform, status: e.status, reason: e.reason, resume: e.resume, date });
  else if (e.status === 'skipped') ap.skipped.push({ company: e.company, role: e.role, url: e.url, platform: e.platform, reason: e.reason, lane: 'lever-fresher-100-2026-10-06' });
}
fs.writeFileSync(apPath, JSON.stringify(ap, null, 2));
console.log('ats_progress updated');

// 4. job_links.json
const jlPath = path.join(root, 'src', 'job_search_results', 'job_links.json');
const jl = JSON.parse(fs.readFileSync(jlPath, 'utf8'));
Object.assign(jl, {
  'Epifi-AI-Engg-Intern': 'https://jobs.lever.co/epifi/08c743e8-2b29-4f78-827e-5bd90476ed86',
  'Epifi-GenAI-Product-Builder-Intern': 'https://jobs.lever.co/epifi/4f5b7548-ea0a-4be0-816b-11d712853169',
  'MerkleScience-SWE-Intern-Backend': 'https://jobs.lever.co/merklescience/e663b69b-264a-4bd7-b04d-fb3c0a824a28',
  'Weekday-SWE-Intern': 'https://jobs.lever.co/weekdayworks/a86efff4-1c2e-43fc-8ecb-dc8f873db2f1',
  'Jobgether-AI-Engineer-SaaS-LLMs': 'https://jobs.lever.co/jobgether/d82c04af-d553-4b47-8faf-108525cf48d2',
  'Jobgether-Associate-Engineer': 'https://jobs.lever.co/jobgether/e8d2c4aa-e042-44a9-9db1-57ece49ca68a',
  'Veeva-Assoc-SWE-Test-Automation': 'https://jobs.lever.co/veeva/d0704c83-8c0f-4545-8a40-eb48bcfec299',
  'OutcomesAI-Backend-MLOps-Speech': 'https://jobs.lever.co/outcomesai/7bbc10a3-805c-441a-8c58-44ab9be9c73c/apply',
  'Lingaro-ML-AI-Engineer-India-Remote': 'https://jobs.lever.co/lingarogroup/5b9bd5a9-5953-43cf-a7e5-fe9161ac0f21/apply',
  'Lingaro-7d57cc12': 'https://jobs.lever.co/lingarogroup/7d57cc12-70c0-40a9-97be-cc9d275371fd/apply',
  'Lingaro-a2aaf267': 'https://jobs.lever.co/lingarogroup/a2aaf267-efdc-4ea2-8660-b06cb0b0f9b3/apply',
  'Lingaro-Peepal-Consulting': 'https://jobs.lever.co/lingarogroup/6adf8593-2a35-44d0-9400-0ced651fd403/apply',
  'Lingaro-Adecco': 'https://jobs.lever.co/lingarogroup/18f8d2c5-b52a-4d9f-b4ff-3f71e0fee53d/apply'
});
fs.writeFileSync(jlPath, JSON.stringify(jl, null, 2));
console.log('job_links updated');
