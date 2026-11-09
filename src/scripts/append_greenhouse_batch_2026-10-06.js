const fs = require('fs');
const P = 'src/application_progress/ats_progress.json';
function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }
(async () => {
  for (let i = 0; i < 20; i++) {
    const txt = fs.readFileSync(P, 'utf8');
    let doc;
    try { doc = JSON.parse(txt); } catch (e) { console.log('try' + i + ' invalid (' + e.message + ') wait...'); await sleep(3000); continue; }
    if (doc['greenhouse_fill_2026-10-06']) { console.log('ALREADY_PRESENT keys=' + Object.keys(doc).length); process.exit(0); }
    const run = JSON.parse(fs.readFileSync('runs/fresher_100_fill_greenhouse_2026-10-06.json', 'utf8'));
    doc['greenhouse_fill_2026-10-06'] = run;
    const out = JSON.stringify(doc, null, 2);
    fs.writeFileSync(P, out);
    const verify = JSON.parse(fs.readFileSync(P, 'utf8'));
    console.log('APPENDED_OK keys=' + Object.keys(verify).length + ' batch_n=' + verify['greenhouse_fill_2026-10-06'].jobs.length);
    process.exit(0);
  }
  console.log('NEVER_STABLE_ABORT');
  process.exit(2);
})();
