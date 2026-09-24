import fs from 'fs';
import dotenv from 'dotenv';
dotenv.config();

const apiKey = process.env.FIRECRAWL_API_KEY;
const QUERIES = [
  { id: 'ashby-1', q: 'site:jobs.ashbyhq.com India fresher software engineer', limit: 12 },
  { id: 'ashby-2', q: 'site:jobs.ashbyhq.com India entry level machine learning', limit: 12 },
  { id: 'ashby-3', q: 'site:jobs.ashbyhq.com India 0-1 year AI data scientist', limit: 12 },
  { id: 'ashby-4', q: 'site:jobs.ashbyhq.com India junior SDE fresher', limit: 12 },
  { id: 'sr-1', q: 'site:jobs.smartrecruiters.com India fresher software engineer', limit: 12 },
  { id: 'sr-2', q: 'site:jobs.smartrecruiters.com India entry level data scientist', limit: 12 },
  { id: 'sr-3', q: 'site:jobs.smartrecruiters.com India 0-1 year AI ML engineer', limit: 12 },
  { id: 'sr-4', q: 'site:jobs.smartrecruiters.com India junior SDE India', limit: 12 },
  { id: 'gh-1', q: 'site:job-boards.greenhouse.io India fresher software engineer', limit: 12 },
  { id: 'gh-2', q: 'site:job-boards.greenhouse.io India entry level data scientist', limit: 12 },
  { id: 'gh-3', q: 'site:boards.greenhouse.io India 0-1 year machine learning', limit: 12 },
  { id: 'gh-4', q: 'site:job-boards.greenhouse.io India junior AI engineer', limit: 12 },
  { id: 'lever-1', q: 'site:jobs.lever.co India fresher software engineer', limit: 12 },
  { id: 'lever-2', q: 'site:jobs.lever.co India entry level data scientist', limit: 12 },
  { id: 'lever-3', q: 'site:jobs.lever.co India 0-1 year AI ML', limit: 12 },
  { id: 'lever-4', q: 'site:jobs.lever.co India junior SDE', limit: 12 },
  { id: 'zoho-1', q: 'site:careers.zohorecruit.com India fresher software engineer', limit: 12 },
  { id: 'zoho-2', q: 'site:careers.zohorecruit.eu India entry level data scientist', limit: 12 },
  { id: 'zoho-3', q: 'Zoho Recruit India fresher SDE AI ML data scientist', limit: 12 },
  { id: 'zoho-4', q: 'site:zohorecruit.com India fresher machine learning', limit: 12 },
  { id: 'broad-1', q: 'India fresher data scientist site:jobs.smartrecruiters.com OR site:jobs.lever.co OR site:jobs.ashbyhq.com', limit: 12 },
  { id: 'broad-2', q: 'India fresher AI engineer entry level Greenhouse Lever Ashby', limit: 12 },
];

async function search(query, limit) {
  const res = await fetch('https://api.firecrawl.dev/v1/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiKey}` },
    body: JSON.stringify({ query, limit, scrapeOptions: { onlyMainContent: true, formats: ['markdown'] } })
  });
  const json = await res.json();
  return { status: res.status, json };
}

let allResults = [];
fs.mkdirSync('runs/fresher_search', { recursive: true });

for (const qq of QUERIES) {
  console.log(`\n=== ${qq.id}: ${qq.q} ===`);
  let attempt = 0;
  while (attempt < 3) {
    attempt++;
    const { status, json } = await search(qq.q, qq.limit);
    if (status === 429 || (json && json.error && String(json.error).includes('Rate limit'))) {
      const wait = 25000;
      console.log(` Rate limited (attempt ${attempt}), waiting ${wait/1000}s...`);
      await new Promise(r=>setTimeout(r, wait));
      continue;
    }
    if (!json.success && json.error) {
      console.log(` ERROR ${status}: ${JSON.stringify(json).slice(0,500)}`);
      fs.writeFileSync(`runs/fresher_search/${qq.id}.error.json`, JSON.stringify({ query: qq.q, status, json }, null, 2));
      break;
    }
    const web = json.data?.web || json.web || [];
    const credits = json.creditsUsed || 0;
    console.log(` -> ${web.length} results, status ${status}, credits ${credits}`);
    fs.writeFileSync(`runs/fresher_search/${qq.id}.json`, JSON.stringify({ query: qq.q, status, credits, count: web.length, raw: json }, null, 2));
    for (const w of web) {
      allResults.push({ query_id: qq.id, query: qq.q, title: (w.title||'').slice(0,180), url: w.url||w.link||'', description: (w.description||'').slice(0,500) });
    }
    break;
  }
  await new Promise(r=>setTimeout(r, 6000));
}

fs.writeFileSync('runs/fresher_search/_all_raw.json', JSON.stringify({ total: allResults.length, results: allResults }, null, 2));
console.log(`\nDONE total raw=${allResults.length}`);
