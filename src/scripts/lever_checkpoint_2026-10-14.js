const fs = require('fs');
const path = require('path');
const root = 'D:\\Projects\\PRACTICE\\firecrawl_test';

// 1. Copy Epifi 404 screenshot into accessability_snapshot (best-effort)
try {
  const src = path.join(root, '.playwright-mcp', 'page-2026-10-14T07-45-52-970Z.png');
  const dstDir = path.join(root, 'src', 'accessability_snapshot');
  if (!fs.existsSync(dstDir)) fs.mkdirSync(dstDir, { recursive: true });
  const dst = path.join(dstDir, 'Epifi-AI-Video-Intern-404.png');
  if (fs.existsSync(src)) { fs.copyFileSync(src, dst); console.log('screenshot copied: ' + dst); }
  else console.log('screenshot src missing, skipped copy');
} catch (e) { console.log('screenshot copy failed: ' + e.message); }

// 2. ats_progress.json checkpoint
const ap = path.join(root, 'src', 'application_progress', 'ats_progress.json');
const j = JSON.parse(fs.readFileSync(ap, 'utf8'));
const has = (arr, url) => arr.some(e => e.url === url);
const blockedAdd = [
  {
    company: 'Epifi/Workloom',
    role: 'AI Video Architect Intern',
    url: 'https://jobs.lever.co/epifi/8ec7ec3f-c24f-49b6-9984-14df7006fe7f',
    platform: 'lever',
    status: 'blocked_dead_req',
    reason: "BLOCKED-dead_req: jobs.lever.co returns Lever 404 page (heading Sorry-we-couldnt-find-anything-here, 404-removed text, title Page not found). Verified live 2026-10-14 via Playwright MCP new-tab navigate + snapshot with Page URL echoed. 4th Epifi dead ID in sweep pattern. No form to fill.",
    resume: 'GenAI_DS (not uploaded - no form)',
    date: '2026-10-14'
  },
  {
    company: 'Jobgether MLE',
    role: 'Machine Learning Engineer India Remote',
    url: 'https://jobs.lever.co/jobgether/ded47afc-192d-4c46-863d-41397012116a',
    platform: 'lever',
    status: 'blocked_dead_req',
    reason: "BLOCKED-dead_req: jobs.lever.co returns Lever 404 page (heading Sorry-we-couldnt-find-anything-here, 404-removed text, title Jobgether-Page-not-found). Verified live 2026-10-14 via Playwright MCP new-tab navigate + snapshot with Page URL echoed. 3rd Jobgether dead ID in sweep pattern. Screenshot attempt misfired onto a foreign agent tab under contention - discarded, snapshot is the evidence. No form to fill.",
    resume: 'GenAI_DS (not uploaded - no form)',
    date: '2026-10-14'
  }
];
blockedAdd.forEach(e => { if (!has(j.blocked, e.url)) j.blocked.push(e); });
const skippedAdd = [
  {
    company: 'Jobgether Classical ML',
    role: 'ML/AI Engineer Classical ML India Remote',
    url: 'https://jobs.lever.co/jobgether/0aec7f97-7358-4643-b5ad-c186165b5d4f',
    platform: 'lever',
    reason: 'LEVEL_MISMATCH 5Y_GAP: JD requires 5y data-eng (last 3y data processing) + 5y production Python + 3y production ML + MLOps Azure-Vertex-Databricks vs 18mo; senior bar, not fresher-3yr scope. Apply NOT clicked per skip rule.',
    lane: 'lever-fill-2026-10-14'
  }
];
skippedAdd.forEach(e => { if (!has(j.skipped, e.url)) j.skipped.push(e); });
j['lever_fill_2026-10-14'] = {
  batch: 'lever-fill 2026-10-14 apply-queue (8 jobs), driver playwright-mcp, submit authority allow_submit true (unused - 0 live in-scope forms)',
  date: '2026-10-14',
  resume: 'GenAI_DS %PDF 130007 bytes verified via node (not uploaded - no live in-scope form)',
  counts: { total: 8, applied: 0, blocked_dead: 2, skipped_relevance: 4, partial_prior_human_decision: 1, skipped_jd_gate: 1 },
  jobs: [
    { url: 'https://jobs.lever.co/merklescience/e663b69b-264a-4bd7-b04d-fb3c0a824a28', disposition: 'SKIP (prior 2026-10-06, no navigate)', reason: 'LEVEL eligibility: 2027-grad CSE-IT IIT-NIT-IIIT only vs 2026 Metallurgical + 2yr lock-in' },
    { url: 'https://jobs.lever.co/epifi/8ec7ec3f-c24f-49b6-9984-14df7006fe7f', disposition: 'BLOCKED-dead_req (navigated + snapshot 404, tab closed)', screenshot: 'src/accessability_snapshot/Epifi-AI-Video-Intern-404.png' },
    { url: 'https://jobs.lever.co/outcomesai/7bbc10a3-805c-441a-8c58-44ab9be9c73c/apply', disposition: 'NO-ACTION (prior partial 2026-10-06, human decides submit vs abandon)', reason: '4-6y MLOps-Triton-speech + CS vs 18mo Metallurgical; resume owed' },
    { url: 'https://jobs.lever.co/lingarogroup/5b9bd5a9-5953-43cf-a7e5-fe9161ac0f21/apply', disposition: 'SKIP (prior 2026-10-06, no navigate)', reason: '5Y_GAP MS-stack Copilot-Azure vs 18mo Python GenAI' },
    { url: 'https://jobs.lever.co/lingarogroup/6adf8593-2a35-44d0-9400-0ced651fd403/apply', disposition: 'SKIP (prior 2026-10-06, no navigate)', reason: '6Y_GAP MS-stack vs 18mo' },
    { url: 'https://jobs.lever.co/lingarogroup/18f8d2c5-b52a-4d9f-b4ff-3f71e0fee53d/apply', disposition: 'SKIP (prior 2026-10-06, no navigate)', reason: '6Y_GAP MS-stack vs 18mo' },
    { url: 'https://jobs.lever.co/jobgether/0aec7f97-7358-4643-b5ad-c186165b5d4f', disposition: 'SKIP 5Y_GAP (JD recon live 2026-10-14, Apply NOT clicked, tab closed)', reason: '5y data-eng-Python + 3y prod ML + MLOps vs 18mo' },
    { url: 'https://jobs.lever.co/jobgether/ded47afc-192d-4c46-863d-41397012116a', disposition: 'BLOCKED-dead_req (navigated + snapshot 404; screenshot misfired foreign-discarded)' }
  ],
  queued: 'none - 0 live in-scope forms this run',
  submitted_by: 'no submits (0 eligible live forms)'
};
fs.writeFileSync(ap, JSON.stringify(j, null, 2));
console.log('ats_progress updated: blocked=' + j.blocked.length + ' skipped=' + j.skipped.length);

// 3. job_links.json additions
const lp = path.join(root, 'src', 'job_search_results', 'job_links.json');
const l = JSON.parse(fs.readFileSync(lp, 'utf8'));
l['Epifi-AI-Video-Intern-8ec7ec3f'] = 'https://jobs.lever.co/epifi/8ec7ec3f-c24f-49b6-9984-14df7006fe7f';
l['Jobgether-Classical-ML-0aec7f97'] = 'https://jobs.lever.co/jobgether/0aec7f97-7358-4643-b5ad-c186165b5d4f';
l['Jobgether-MLE-ded47afc'] = 'https://jobs.lever.co/jobgether/ded47afc-192d-4c46-863d-41397012116a';
fs.writeFileSync(lp, JSON.stringify(l));
console.log('job_links updated: keys=' + Object.keys(l).length);
