import Firecrawl from '@mendable/firecrawl-js';
import fs from 'fs';
import dotenv from 'dotenv';
dotenv.config();

const apiKey = process.env.FIRECRAWL_API_KEY;
if (!apiKey) { console.error('Missing FIRECRAWL_API_KEY'); process.exit(1); }
const app = new Firecrawl({ apiKey });

const QUERIES = [
  // Ashby
  { id: 'ashby-1', q: 'site:jobs.ashbyhq.com India fresher software engineer', limit: 12 },
  { id: 'ashby-2', q: 'site:jobs.ashbyhq.com India entry level machine learning', limit: 12 },
  { id: 'ashby-3', q: 'site:jobs.ashbyhq.com India 0-1 year AI data scientist', limit: 12 },
  { id: 'ashby-4', q: 'site:jobs.ashbyhq.com India junior SDE fresher', limit: 12 },
  // SmartRecruiters
  { id: 'sr-1', q: 'site:jobs.smartrecruiters.com India fresher software engineer', limit: 12 },
  { id: 'sr-2', q: 'site:jobs.smartrecruiters.com India entry level data scientist', limit: 12 },
  { id: 'sr-3', q: 'site:jobs.smartrecruiters.com India 0-1 year AI ML engineer', limit: 12 },
  { id: 'sr-4', q: 'site:jobs.smartrecruiters.com India junior SDE India', limit: 12 },
  // Greenhouse
  { id: 'gh-1', q: 'site:job-boards.greenhouse.io India fresher software engineer', limit: 12 },
  { id: 'gh-2', q: 'site:job-boards.greenhouse.io India entry level data scientist', limit: 12 },
  { id: 'gh-3', q: 'site:boards.greenhouse.io India 0-1 year machine learning', limit: 12 },
  { id: 'gh-4', q: 'site:job-boards.greenhouse.io India junior AI engineer', limit: 12 },
  // Lever
  { id: 'lever-1', q: 'site:jobs.lever.co India fresher software engineer', limit: 12 },
  { id: 'lever-2', q: 'site:jobs.lever.co India entry level data scientist', limit: 12 },
  { id: 'lever-3', q: 'site:jobs.lever.co India 0-1 year AI ML', limit: 12 },
  { id: 'lever-4', q: 'site:jobs.lever.co India junior SDE', limit: 12 },
  // Zoho Recruit
  { id: 'zoho-1', q: 'site:careers.zohorecruit.com India fresher software engineer', limit: 12 },
  { id: 'zoho-2', q: 'site:careers.zohorecruit.eu India entry level data scientist', limit: 12 },
  { id: 'zoho-3', q: 'Zoho Recruit India fresher SDE AI ML data scientist', limit: 12 },
  { id: 'zoho-4', q: 'site:zohorecruit.com India fresher machine learning', limit: 12 },
  // Broad backup for Zoho + extras
  { id: 'broad-1', q: 'India fresher data scientist site:jobs.smartrecruiters.com OR site:jobs.lever.co OR site:jobs.ashbyhq.com', limit: 12 },
  { id: 'broad-2', q: 'India fresher AI engineer \"0-1 years\" OR \"entry level\" Greenhouse Lever Ashby', limit: 12 },
];

function sleep(ms){ return new Promise(r=>setTimeout(r, ms)); }

let allResults = [];
let creditsUsed = 0;

for (const qq of QUERIES) {
  console.log(`\n=== ${qq.id}: ${qq.q} ===`);
  try {
    const start = Date.now();
    const res = await app.search(qq.q, {
      limit: qq.limit,
      scrapeOptions: { onlyMainContent: true, formats: ['markdown'] },
    });
    const elapsed = ((Date.now()-start)/1000).toFixed(1);
    // Firecrawl JS search returns { success, data: { web: [...] } } or similar
    // Firecrawl v4 search returns { web: [...], news: [...], creditsUsed } OR { data: { web: [...] } }
    const web = res.web || (res.data && res.data.web) || res.results || [];
    const credits = res.creditsUsed || (res.data && res.data.creditsUsed) || 0;
    creditsUsed += credits;
    console.log(` -> ${web.length} results, credits ${credits}, ${elapsed}s`);
    if (web.length === 0) console.log(' RAW KEYS:', Object.keys(res).join(','), JSON.stringify(res).slice(0,400));
    for (const w of web) {
      allResults.push({
        query_id: qq.id,
        query: qq.q,
        title: (w.title || '').slice(0,180),
        url: w.url || w.link || '',
        description: (w.description || w.markdown || '').slice(0,500),
        // keep raw
      });
    }
    // dump per-query
    fs.mkdirSync('runs/fresher_search', { recursive: true });
    fs.mkdirSync('runs/fresher_search', { recursive: true });
    fs.writeFileSync(`runs/fresher_search/${qq.id}.json`, JSON.stringify({ query: qq.q, credits, count: web.length, results: web, raw: res }, null, 2));
  } catch (e) {
    console.error(` ERROR ${qq.id}:`, e.message?.slice(0,500) || e);
    fs.writeFileSync(`runs/fresher_search/${qq.id}.error.json`, JSON.stringify({ query: qq.q, error: String(e).slice(0,2000) }, null, 2));
  }
  await sleep(1200);
}

fs.writeFileSync('runs/fresher_search/_all_raw.json', JSON.stringify({ total: allResults.length, creditsUsed, results: allResults }, null, 2));
console.log(`\nDONE total raw=${allResults.length} credits~${creditsUsed}`);
