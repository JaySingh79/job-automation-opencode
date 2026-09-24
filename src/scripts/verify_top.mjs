import fs from 'fs';
import dotenv from 'dotenv';
dotenv.config();
const apiKey=process.env.FIRECRAWL_API_KEY;
const scored=JSON.parse(fs.readFileSync('runs/fresher_search/_scored.json','utf8'));
// pick top 60
const top=scored.slice(0,60);
console.log('verifying top', top.length);

async function scrape(url){
  const res=await fetch('https://api.firecrawl.dev/v1/scrape', {
    method:'POST',
    headers:{ 'Content-Type':'application/json', 'Authorization': `Bearer ${apiKey}` },
    body: JSON.stringify({ url, onlyMainContent:true, formats:['markdown'] })
  });
  const j=await res.json();
  return { status:res.status, j };
}

let results=[];
for(let i=0;i<top.length;i++){
  const r=top[i];
  console.log(`\n[${i+1}/${top.length}] ${r.ats} ${r.clean.slice(0,80)}`);
  try{
    const {status, j}=await scrape(r.clean);
    const success=j.success;
    const markdown=(j.data?.markdown||'').slice(0,2000);
    const html=(j.data?.html||'').slice(0,500);
    const hasIndia=/india|bengaluru|bangalore|hyderabad|pune|gurgaon|mumbai|chennai|remote/i.test(markdown);
    const isExpired=/job not found|position has been filled|expired|not accepting applications|404|no longer available/i.test(markdown);
    const hasApply=/apply/i.test(markdown);
    console.log(` status=${status} success=${success} india=${hasIndia} expired=${isExpired} apply=${hasApply} mdLen=${markdown.length}`);
    results.push({...r, verify:{status, success, hasIndia, isExpired, hasApply, mdSnippet: markdown.slice(0,600)}});
    fs.writeFileSync(`runs/fresher_search/verify_${String(i+1).padStart(2,'0')}_${r.ats}.json`, JSON.stringify({url:r.clean, status, j},null,2));
  }catch(e){
    console.log(' error', String(e).slice(0,400));
    results.push({...r, verify:{error:String(e).slice(0,400)}});
  }
  await new Promise(res=>setTimeout(res, 4000));
}
fs.writeFileSync('runs/fresher_search/_verify_top60.json', JSON.stringify(results,null,2));
console.log('done', results.filter(r=>r.verify.isExpired).length, 'expired', results.filter(r=>!r.verify.isExpired && r.verify.success).length, 'ok');
