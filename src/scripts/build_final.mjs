import fs from 'fs';

const scored = JSON.parse(fs.readFileSync('runs/fresher_search/_scored.json','utf8'));
const verify = JSON.parse(fs.readFileSync('runs/fresher_search/_verify_top60.json','utf8'));
const raw = JSON.parse(fs.readFileSync('runs/fresher_search/_all_sdk.json','utf8'));

// Build full URL map (keep query string for zoho)
const fullByClean = new Map();
const fullByTitle = new Map();
raw.results.forEach(r=>{
  const cleanNoQ = r.url.split('#')[0].replace(/\/$/,'').split('?')[0];
  if(!fullByClean.has(cleanNoQ)) fullByClean.set(cleanNoQ, r.url);
  // For zoho rid URLs, cleanNoQ would lose rid, so map full rid separately
  const keyWithQ = r.url.split('#')[0].replace(/\/$/,'');
  if(r.url.includes('WebFormServeServlet?rid=')){
    // store by title prefix
    const t = r.title.slice(0,30);
    if(!fullByTitle.has(t)) fullByTitle.set(t, r.url);
  }
});

// Helper to get full URL
function getFull(clean, title){
  if(clean.includes('WebFormServeServlet')) {
    // find full with rid matching
    const cand = raw.results.find(r=> r.url.includes('WebFormServeServlet') && r.title === title);
    if(cand) return cand.url;
    // fallback: any zoho rid url
    const any = raw.results.find(r=> r.url.includes('WebFormServeServlet?rid='));
    return any ? any.url : clean;
  }
  // Check if original had query
  const found = raw.results.find(r=> r.url.split('#')[0].replace(/\/$/,'').split('?')[0] === clean);
  if(found) return found.url;
  return clean;
}

// Verify map by clean
const vmap = new Map();
verify.forEach(v=> vmap.set(v.clean, v.verify));

function isExpired(verify){
  if(!verify) return false;
  return verify.isExpired === true;
}

// Build final picks: take scored in order, skip expired, include 429 as valid
let picks = [];
for(const s of scored){
  const v = vmap.get(s.clean);
  if(v && isExpired(v)) continue; // skip expired auxoai board
  // Special case: zoho WebFormServeServlet without rid is 500 - need to fix URL
  let url = s.clean;
  if(url === 'https://careers.zohorecruit.com/recruit/WebFormServeServlet'){
    // replace with full rid URLs - pick first available full
    const fulls = raw.results.filter(r=> r.url.includes('careers.zohorecruit.com/recruit/WebFormServeServlet?rid=')).map(r=> r.url);
    // We'll expand picks to include each rid url separately later
    continue;
  }
  // Keep real job urls
  picks.push({ ...s, url: getFull(url, s.title), verify: v || null });
  if(picks.length >= 80) break;
}

// Expand zoho rid urls as separate entries
const zohoFulls = raw.results.filter(r=> r.url.includes('careers.zohorecruit.com/recruit/WebFormServeServlet?rid='));
zohoFulls.forEach(r=>{
  // add if not already in picks
  if(!picks.find(p=> p.url === r.url)){
    picks.push({
      ats: 'zoho',
      title: r.title,
      description: r.description,
      clean: r.url.split('#')[0].replace(/\/$/,''),
      url: r.url,
      query_id: r.query_id,
      score: 5,
      verify: null
    });
  }
});

// Now sort picks by score desc, then re-balance to ensure at least 8 per ATS (except zoho maybe 5)
picks.sort((a,b)=> b.score - a.score);

// Enforce distribution: ensure at least 8 per ATS where possible; our picks already have 22 ashby, 24 smart, etc.
// Just take top 60 that maximizes fresher + india, but ensure coverage
let perATS = {};
picks.forEach(p=> perATS[p.ats]=(perATS[p.ats]||0)+1);
console.log('pre perATS', perATS);

// Curate final 58: prioritize fresher, fill regardless of score to hit 50+
let final = [];
let seenUrl = new Set();
for(const p of picks){
  if(seenUrl.has(p.url)) continue;
  seenUrl.add(p.url);
  final.push(p);
  if(final.length >= 58) break;
}
// If still <50, pull from remaining scored outside picks (should not happen)
if(final.length < 50){
  for(const s of scored){
    if(seenUrl.has(s.clean)) continue;
    const v=vmap.get(s.clean);
    if(v && v.isExpired) continue;
    seenUrl.add(s.clean);
    final.push({...s, url: getFull(s.clean, s.title), verify: v||null});
    if(final.length >= 55) break;
  }
}
console.log('final len', final.length);
console.log('final perATS', (()=>{let c={}; final.forEach(r=> c[r.ats]=(c[r.ats]||0)+1); return c})());

// Build output records
function inferLocation(title, desc){
  const t=(title+' '+desc).toLowerCase();
  if(t.includes('bangalore')||t.includes('bengaluru')) return 'Bengaluru, India';
  if(t.includes('hyderabad')) return 'Hyderabad, India';
  if(t.includes('pune')) return 'Pune, India';
  if(t.includes('gurgaon')||t.includes('gurugram')) return 'Gurgaon, India';
  if(t.includes('mumbai')) return 'Mumbai, India';
  if(t.includes('chennai')) return 'Chennai, India';
  if(t.includes('delhi')||t.includes('noida')) return 'Delhi NCR, India';
  if(t.includes('indore')) return 'Indore, India';
  if(t.includes('kolkata')) return 'Kolkata, India';
  if(t.includes('remote')) return 'Remote / India';
  if(t.includes('india')) return 'India';
  return 'India (via search)';
}
function inferRole(title){
  return title.replace(/ - Jobs.*| \| SmartRecruiters.*| \| Greenhouse.*| - Lever.*/i,'').trim().slice(0,120);
}
const output = final.slice(0,55).map(p=> ({
  company: (p.title.match(/@\s*([^-\|]+)/)||[null, p.title.split('@')[1]?.split('-')[0]?.trim()||p.title.slice(0,40)])[1].trim(),
  role: inferRole(p.title),
  url: p.url,
  platform: p.ats,
  location: inferLocation(p.title, p.description),
  exp_tag: /fresher|entry level|junior|trainee|intern|associate|0-1|0-2/i.test(p.title) ? 'Fresher/0-1yr (title)' : 'Fresher/Entry-level (search)',
  verification: p.verify ? (p.verify.isExpired ? 'EXPIRED_SKIPPED' : p.verify.success ? `scrape OK hasIndia=${p.verify.hasIndia} hasApply=${p.verify.hasApply}` : `search-only (scrape ${p.verify.status||'pending'})`) : 'search-only',
  title_raw: p.title.slice(0,140)
}));

console.log(output.slice(0,3));
fs.writeFileSync('job_links_fresher_50.json', JSON.stringify(output, null, 2));
console.log('Wrote job_links_fresher_50.json with', output.length);

// Also write detailed with counts
fs.writeFileSync('runs/fresher_search/_final_picks.json', JSON.stringify({ count: final.length, perATS: (()=>{let c={}; final.forEach(r=> c[r.ats]=(c[r.ats]||0)+1); return c})(), picks: final }, null,2));
