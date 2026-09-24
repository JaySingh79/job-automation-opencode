import Firecrawl from '@mendable/firecrawl-js';
import fs from 'fs';
import dotenv from 'dotenv';
dotenv.config();
const apiKey = process.env.FIRECRAWL_API_KEY;
const app = new Firecrawl({ apiKey });

const QUERIES = [
  { id: 'ashby-1', q: 'site:jobs.ashbyhq.com India fresher software engineer', limit: 10 },
  { id: 'ashby-2', q: 'site:jobs.ashbyhq.com India entry level machine learning', limit: 10 },
  { id: 'ashby-3', q: 'site:jobs.ashbyhq.com India 0-1 year AI data scientist', limit: 10 },
  { id: 'ashby-4', q: 'site:jobs.ashbyhq.com India junior SDE', limit: 10 },
  { id: 'sr-1', q: 'site:jobs.smartrecruiters.com India fresher software engineer', limit: 10 },
  { id: 'sr-2', q: 'site:jobs.smartrecruiters.com India entry level data scientist', limit: 10 },
  { id: 'sr-3', q: 'site:jobs.smartrecruiters.com India AI ML engineer fresher', limit: 10 },
  { id: 'sr-4', q: 'site:jobs.smartrecruiters.com India junior SDE', limit: 10 },
  { id: 'gh-1', q: 'site:job-boards.greenhouse.io India fresher software engineer', limit: 10 },
  { id: 'gh-2', q: 'site:job-boards.greenhouse.io India entry level data scientist', limit: 10 },
  { id: 'gh-3', q: 'site:boards.greenhouse.io India machine learning fresher', limit: 10 },
  { id: 'gh-4', q: 'site:job-boards.greenhouse.io India junior AI engineer', limit: 10 },
  { id: 'lever-1', q: 'site:jobs.lever.co India fresher software engineer', limit: 10 },
  { id: 'lever-2', q: 'site:jobs.lever.co India entry level data scientist', limit: 10 },
  { id: 'lever-3', q: 'site:jobs.lever.co India AI ML fresher', limit: 10 },
  { id: 'lever-4', q: 'site:jobs.lever.co India junior SDE', limit: 10 },
  { id: 'zoho-1', q: 'site:careers.zohorecruit.com India fresher', limit: 10 },
  { id: 'zoho-2', q: 'Zoho Recruit India fresher software engineer', limit: 10 },
  { id: 'zoho-3', q: 'Zoho Recruit India data scientist AI', limit: 10 },
  { id: 'broad-1', q: 'India fresher data scientist Greenhouse Lever Ashby', limit: 10 },
  { id: 'broad-2', q: 'India entry level AI engineer 0-1 year', limit: 10 },
];

fs.mkdirSync('runs/fresher_search', { recursive: true });
let all = [];
let totalCredits = 0;

for (const qq of QUERIES) {
  console.log(`\n=== ${qq.id}: ${qq.q} ===`);
  try {
    const start = Date.now();
    // no scrapeOptions to keep credit low, just search
    const res = await app.search(qq.q, { limit: qq.limit });
    const elapsed = ((Date.now()-start)/1000).toFixed(1);
    // res shape: { web: [...], creditsUsed?, ... }
    const web = res.web || res.data?.web || [];
    const credits = res.creditsUsed || 0;
    totalCredits += credits;
    console.log(` -> web=${web.length} credits=${credits} ${elapsed}s`);
    if (res.error) console.log('  error field:', res.error);
    fs.writeFileSync(`runs/fresher_search/${qq.id}.json`, JSON.stringify({ query: qq.q, credits, count: web.length, web: web.slice(0,3), full: res }, null, 2));
    for (const w of web) {
      all.push({ query_id: qq.id, title: w.title?.slice(0,180)||'', url: w.url||'', description: (w.description||'').slice(0,400) });
    }
  } catch (e) {
    const msg = String(e.message||e).slice(0,800);
    console.log(` CATCH ${qq.id}: ${msg}`);
    fs.writeFileSync(`runs/fresher_search/${qq.id}.error.json`, JSON.stringify({ query: qq.q, error: msg }, null, 2));
    if (msg.includes('Rate limit') || msg.includes('429')) {
      console.log('  waiting 30s for rate limit...');
      await new Promise(r=>setTimeout(r, 30000));
      // retry once
      try {
        const res2 = await app.search(qq.q, { limit: qq.limit });
        const web2 = res2.web || [];
        console.log(`  retry -> web=${web2.length}`);
        for (const w of web2) all.push({ query_id: qq.id, title: w.title?.slice(0,180)||'', url: w.url||'', description: (w.description||'').slice(0,400) });
        fs.writeFileSync(`runs/fresher_search/${qq.id}.retry.json`, JSON.stringify(res2,null,2));
      } catch(e2){ console.log('  retry failed', String(e2.message).slice(0,300)); }
    }
  }
  await new Promise(r=>setTimeout(r, 7000));
}

fs.writeFileSync('runs/fresher_search/_all_sdk.json', JSON.stringify({ total: all.length, credits: totalCredits, results: all }, null, 2));
console.log(`\nDONE total=${all.length} credits=${totalCredits}`);
