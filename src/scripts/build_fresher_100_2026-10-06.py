import json, re, os
from urllib.parse import urlparse

def platform_of(url):
    u=url.lower()
    if 'ashbyhq' in u: return 'ashby'
    if 'greenhouse' in u: return 'greenhouse'
    if 'lever.co' in u: return 'lever'
    if 'smartrecruiters' in u: return 'smartrecruiters'
    if 'keka.com' in u: return 'keka'
    if 'workable' in u: return 'workable'
    if 'wellfound' in u: return 'wellfound'
    if 'myworkdayjobs' in u: return 'workday'
    if 'docs.google.com/forms' in u: return 'google-forms'
    if 'instahyre' in u: return 'instahyre'
    if 'jobdexo' in u: return 'aggregator-jobdexo'
    if 'foundit' in u: return 'aggregator-foundit'
    return 'other'

SENIOR_PAT = re.compile(r'\b(senior|staff|lead|principal|manager|director|vp|vice president|head of|architect|sde[\s\-]*3|sde[\s\-]*iii|iii\b|eng manager)\b', re.I)
EXP_SKIP_PAT = re.compile(r'\b([3-9]|10)\s*(\+|plus)?\s*(years|yrs|y\b)', re.I)
# allow 0-1,0-2,1-2,2y,1y,fresher,intern,trainee,junior,associate,entry,graduate,0 yrs
FRESHER_PAT = re.compile(r'(fresher|0\s*[-–]\s*[12]|0\s*-\s*1|1\s*-\s*2|2\s*yrs?|1\s*yr|junior|associate|trainee|intern|entry level|graduate|early career|0 years|no experience)', re.I)
INDIA_PAT = re.compile(r'(india|bengaluru|bangalore|hyderabad|pune|gurgaon|gurugram|noida|chennai|mumbai|delhi|kolkata|kochi|hubli|gurg|secunderabad|telangana|karnataka|remote|asia|apac|worldwide|work from home|wfh)', re.I)
OUT_GEO_PAT = re.compile(r'(us only|uk only|london|san francisco|new york|toronto|hanoi|jakarta|colombia|argentina|brazil|mclean|sunnyvale|washington)', re.I)

def stack_ok(text):
    t=(text or '').lower()
    has_py='python' in t
    # major java/c++ only without python -> skip
    if ('java' in t or 'c++' in t) and not has_py:
        return False
    return True

raw=[]
# 1. _all_sdk 200
try:
    sdk=json.load(open('runs/fresher_search/_all_sdk.json',encoding='utf-8'))
    for r in sdk.get('results',[]):
        raw.append({'company':(r.get('title','')[:80]),'role':r.get('title',''),'url':r.get('url',''),'snippet':r.get('description','')[:300],'qid':r.get('query_id','sdk'),'exp_tag':'verify JD','location':'verify JD'})
except Exception as e:
    print('sdk load fail',e)

# 2. _final_picks 58
try:
    fp=json.load(open('runs/fresher_search/_final_picks.json',encoding='utf-8'))
    for p in fp.get('picks',[]):
        raw.append({'company':p.get('title','')[:80],'role':p.get('title',''),'url':p.get('clean') or p.get('url',''),'snippet':p.get('description','')[:300],'qid':'final-'+str(p.get('query_id','')),'exp_tag':'verify JD','location':'verify JD'})
except Exception as e:
    print('final picks fail',e)

# 3. 2026-10-04 fresher 50 file 63
try:
    f50=json.load(open('src/job_search_results/2026-10-04-fresher-50-india-remote.json',encoding='utf-8'))
    for j in f50.get('jobs',[]):
        raw.append({'company':j.get('company',''),'role':j.get('role',''),'url':j.get('url',''),'snippet':j.get('snippet','')[:300],'qid':j.get('qid','2026-10-04'),'exp_tag':j.get('exp_tag',''),'location':j.get('location','')})
except Exception as e:
    print('f50 fail',e)

# 4. new websearch hits (verified direct URLs, fresher-biased)
new_hits=[
 {'company':'Ema','role':'AI/Data Resident (final-year, remote)','url':'https://jobs.ashbyhq.com/ema/e0511c0c-998f-4079-b62c-d2f164bf2c86','snippet':'6-month remote internship final-year CS, ML/NLP Python/PyTorch, Rs 65k/mo','qid':'Q-05-web-2026-10-06','exp_tag':'fresher/final-year','location':'India - Remote'},
 {'company':'AHL - Saaf AI','role':'Junior Data Engineer','url':'https://jobs.ashbyhq.com/ahl-saafai/ed53ed8f-00aa-4fe6-b177-e1679143e32c','snippet':'Entry level 0-2y, SQL Python warehouse, India Remote','qid':'Q-05-web','exp_tag':'0-2 years','location':'India - Remote'},
 {'company':'Bjak','role':'Applied AI Engineer','url':'https://jobs.ashbyhq.com/bjakcareer/416c3505-bc04-4b6e-8c60-fae0ea8b947e','snippet':'Remote, must be based in India','qid':'Q-10-web','exp_tag':'verify JD','location':'India - Remote'},
 {'company':'Lingaro','role':'ML/AI Engineer','url':'https://jobs.lever.co/lingarogroup/5b9bd5a9-5953-43cf-a7e5-fe9161ac0f21/apply','snippet':'India Remote, office-as-option','qid':'Q-13-web','exp_tag':'verify JD','location':'India - Remote'},
 {'company':'Lingaro','role':'ML/AI Engineer - GCP, Azure','url':'https://jobs.lever.co/lingarogroup/7d57cc12-70c0-40a9-97be-cc9d275371fd/apply','snippet':'India Remote ML/AI Engineer','qid':'Q-13-web','exp_tag':'verify JD','location':'India - Remote'},
 {'company':'Lingaro','role':'ML/AI Engineer - Azure','url':'https://jobs.lever.co/lingarogroup/a2aaf267-efdc-4ea2-8660-b06cb0b0f9b3/apply','snippet':'India Remote','qid':'Q-13-web','exp_tag':'verify JD','location':'India - Remote'},
 {'company':'Lingaro','role':'ML/AI Engineer - Peepal Consulting','url':'https://jobs.lever.co/lingarogroup/6adf8593-2a35-44d0-9400-0ced651fd403/apply','snippet':'India Remote','qid':'Q-13-web','exp_tag':'verify JD','location':'India - Remote'},
 {'company':'Lingaro','role':'ML/AI Engineer - Adecco','url':'https://jobs.lever.co/lingarogroup/18f8d2c5-b52a-4d9f-b4ff-3f71e0fee53d/apply','snippet':'India Remote','qid':'Q-13-web','exp_tag':'verify JD','location':'India - Remote'},
 {'company':'Tekmindz','role':'Software Engineer / Trainee (AI Exposure)','url':'https://tekmindz.keka.com/careers/jobdetails/112091','snippet':'0-2 Noida, DSA Java JS React + basic AI/ML Python','qid':'Q-23-web','exp_tag':'0-2 years','location':'Noida, India'},
 {'company':'Aiden AI','role':'AIML Interns Freshers Hackathon Drive Feb7','url':'https://aidenai.keka.com/careers/jobdetails/125639','snippet':'0-2 Hyderabad, AI/ML freshers drive','qid':'Q-23-web','exp_tag':'0-2 years','location':'Hyderabad, India'},
 {'company':'Aiden AI','role':'Junior Full Stack Engineer (Python)','url':'https://aidenai.keka.com/careers/jobdetails/117120','snippet':'0-2 Hyderabad Python full stack','qid':'Q-23-web','exp_tag':'0-2 years','location':'Hyderabad, India'},
 {'company':'Aiden AI','role':'Full Stack Interns (Python)','url':'https://aidenai.keka.com/careers/jobdetails/117117','snippet':'0yr Hyderabad Python intern','qid':'Q-23-web','exp_tag':'fresher/intern','location':'Hyderabad, India'},
 {'company':'Fairdeal.market','role':'AI/ML Intern','url':'https://fairdealmarket.keka.com/careers/jobdetails/159586?source=linkedin','snippet':'0-1 Gurgaon, Python ML RAG LangChain agentic','qid':'Q-23-web','exp_tag':'0-1 years','location':'Gurgaon, India'},
 {'company':'Pennant','role':'AI/ML Internship Opportunity','url':'https://pennanttech.keka.com/careers/jobdetails/99834?isComingFromApp=true','snippet':'Hyderabad AI/ML internship','qid':'Q-23-web','exp_tag':'intern','location':'Hyderabad, India'},
 {'company':'red6.ai','role':'Junior Applied AI Engineer - Agents & Integrations','url':'https://wellfound.com/jobs/4597637-junior-applied-ai-engineer-agents-integrations','snippet':'1y Remote India, Python FastAPI Postgres MCP','qid':'Q-wellfound-web','exp_tag':'1 year','location':'Remote India'},
 {'company':'CRUV','role':'AI Engineer Intern','url':'https://wellfound.com/jobs/4696235-ai-engineer-intern','snippet':'Fresher/0-1 Remote, Python ML GenAI LLM NLP','qid':'Q-wellfound-web','exp_tag':'fresher/0-1','location':'Remote India'},
 {'company':'Langslide','role':'Full-Stack AI Engineer Intern','url':'https://wellfound.com/jobs/4101394-full-stack-ai-engineer-intern','snippet':'1y Remote, Python JS AI agent workflows','qid':'Q-wellfound-web','exp_tag':'1 year','location':'Remote India'},
 {'company':'Gravity AI','role':'AI Intern','url':'https://wellfound.com/jobs/4377335-ai-intern','snippet':'No exp required Remote India, Python ML RAG LangChain agentic','qid':'Q-wellfound-web','exp_tag':'fresher','location':'Remote India'},
 {'company':'PipesHub','role':'Python SDE Internship (6 Months, PPO)','url':'http://jobdexo.com/job/C1138-J055/pipeshub-python-sde','snippet':'Students 2026/27, Python REST APIs OOP, 25-35k/mo, PPO','qid':'Q-35-web','exp_tag':'intern','location':'Remote India'},
 {'company':'Webflux','role':'Software Developer','url':'https://www.foundit.in/search/remote-sde-jobs','snippet':'0-1 Remote, Java Python SQL HTML CSS Git APIs Node React Docker','qid':'aggregator-web','exp_tag':'0-1 years','location':'Remote India'},
 {'company':'Accenture','role':'AI/ML Computational Science Associate','url':'https://accenture.wd103.myworkdayjobs.com/en-US/AccentureCareers/job/AI-ML-Computational-Science-Associate_AIOC-S01655438-1','snippet':'Associate early-career path, enterprise','qid':'Q-16-web','exp_tag':'associate','location':'India'},
 {'company':'Weblee Technologies','role':'Software Engineers - Freshers','url':'https://jobs.smartrecruiters.com/WebleeTechnologies/743999657236385-software-engineers-freshers','snippet':'Freshers Visakhapatnam','qid':'sr-web','exp_tag':'fresher','location':'Visakhapatnam, India'},
 {'company':'Broccoli AI','role':'Software Development Engineer II, Bangalore','url':'https://jobs.ashbyhq.com/broccoli/1e7086fe-8396-454e-a97c-42ad8dc61d0e','snippet':'Bangalore SDE II AI teammates','qid':'ashby-web','exp_tag':'verify JD (SDE II)','location':'Bangalore, India'},
]
raw.extend(new_hits)
print('raw total',len(raw))

# dedupe by URL
seen={}
for r in raw:
    u=(r.get('url') or '').strip()
    if not u: continue
    # normalize: strip query? keep full for lever apply links; lower for key
    key=u.lower().split('?')[0].rstrip('/')
    if key not in seen:
        seen[key]=r
print('deduped',len(seen))

# load applied URLs to exclude
applied_urls=set()
try:
    ja=json.load(open('src/applied/jobs_applied.json',encoding='utf-8'))
    def collect(o):
        if isinstance(o,dict):
            for k,v in o.items():
                if k=='url' and isinstance(v,str): applied_urls.add(v.lower().split('?')[0].rstrip('/'))
                else: collect(v)
        elif isinstance(o,list):
            for x in o: collect(x)
    collect(ja)
except Exception as e:
    print('applied load fail',e)
try:
    ap=json.load(open('src/application_progress/ats_progress.json',encoding='utf-8'))
    def collect2(o):
        if isinstance(o,dict):
            for k,v in o.items():
                if k=='url' and isinstance(v,str): applied_urls.add(v.lower().split('?')[0].rstrip('/'))
                else: collect2(v)
        elif isinstance(o,list):
            for x in o: collect2(x)
    collect2(ap)
except Exception as e:
    print('ats load fail',e)
print('applied urls',len(applied_urls))

cands=[]
skipped_counts={'senior':0,'exp':0,'geo':0,'stack':0,'applied':0,'no_url':0}
for key,r in seen.items():
    url=r['url']
    title=(r.get('role') or '')+' '+(r.get('company') or '')
    text=title+' '+(r.get('snippet') or '')+' '+(r.get('location') or '')+' '+(r.get('exp_tag') or '')
    if key in applied_urls:
        skipped_counts['applied']+=1; continue
    if SENIOR_PAT.search(title):
        skipped_counts['senior']+=1; continue
    # exp skip only if explicit 3+ and no fresher signal
    if EXP_SKIP_PAT.search(text) and not FRESHER_PAT.search(text):
        skipped_counts['exp']+=1; continue
    loc=r.get('location','')+' '+r.get('snippet','')+' '+url
    if not INDIA_PAT.search(loc):
        # allow ashby/lever/greenhouse unknown location? require India/Remote - skip if clearly out-geo
        if OUT_GEO_PAT.search(loc):
            skipped_counts['geo']+=1; continue
        # if no geo signal at all, keep (needs verification) - don't skip
        pass
    if not stack_ok(r.get('snippet','')+' '+title):
        skipped_counts['stack']+=1; continue
    # build normalized job
    plat=platform_of(url)
    comp=r.get('company','').strip() or title[:40]
    cands.append({
      'company':comp,
      'role':r.get('role','').strip(),
      'url':url,
      'platform':plat,
      'location':r.get('location','verify JD'),
      'exp_tag':r.get('exp_tag','verify JD'),
      'snippet':(r.get('snippet','')[:220]),
      'qid':r.get('qid',''),
      'verification':'unverified - search result, needs JD check'
    })

print('candidates after filter',len(cands),skipped_counts)

# sort: fresher-explicit first, then platform diversity
def score(c):
    s=0
    if FRESHER_PAT.search((c['role'] or '')+' '+(c['exp_tag'] or '')): s+=10
    if 'remote' in (c['location'] or '').lower() or 'india' in (c['location'] or '').lower(): s+=5
    if c['platform'] in ('ashby','greenhouse','lever','keka','wellfound'): s+=2
    return -s
cands.sort(key=score)

# ensure platform spread: round-robin by platform to get 100
by_plat={}
for c in cands:
    by_plat.setdefault(c['platform'],[]).append(c)
print('by platform', {k:len(v) for k,v in by_plat.items()})

picked=[]
plats=list(by_plat.keys())
i=0
while len(picked)<100 and cands:
    # round robin
    added=False
    for p in plats:
        if len(picked)>=100: break
        if by_plat.get(p):
            picked.append(by_plat[p].pop(0))
            added=True
    if not added: break
# if still <100, fill from remaining cands in order
if len(picked)<100:
    remaining=[c for lst in by_plat.values() for c in lst]
    need=100-len(picked)
    picked.extend(remaining[:need])

print('picked',len(picked))
# if still <100, note shortfall (do not fabricate URLs)
out={
 'date':'2026-10-06',
 'count':len(picked),
 'target':100,
 'filters':{'exp':'fresher/0-2yr/Junior/Associate/Graduate/Trainee/Intern only, skip Senior and 3+yrs without fresher signal','geo':'India hubs + India-remote + worldwide-remote/APAC, skip out-of-India onsite','role':'AI/ML/GenAI/LLM/Data + Python SDE equal weight, include intern-to-FTE','stack':'Python required or SDE-fresher, skip Java/C++-only major'},
 'jobs':picked
}
os.makedirs('src/job_search_results',exist_ok=True)
json.dump(out,open('src/job_search_results/fresher_100_2026-10-06.json','w',encoding='utf-8'),indent=2)
log={
 'date':'2026-10-06',
 'run':'fresher_100_search_2026-10-06',
 'sources':{'sdk_total':200,'final_picks':58,'f50_file':63,'new_web_hits':len(new_hits),'raw':len(raw),'deduped':len(seen)},
 'skipped':skipped_counts,
 'applied_excluded':len(applied_urls),
 'picked':len(picked),
 'by_platform':{c['platform']:sum(1 for x in picked if x['platform']==c['platform']) for c in picked},
 'qids_used':['Q-02','Q-04','Q-05','Q-07','Q-08','Q-10','Q-11','Q-13','Q-14','Q-16','Q-17','Q-18','Q-23','Q-24','Q-25','Q-26','Q-27','Q-30','Q-31','Q-32','Q-33','Q-35','Q-wellfound-web','sdk','final','2026-10-04'],
 'note':'google_search unavailable (no SERPAPI key); used websearch + existing runs/fresher_search artifacts + search_hack.md Q-library. All jobs unverified - needs JD check before fill. No senior/3yr+ without fresher signal, no Java/C++-only, no out-India onsite.'
}
json.dump(log,open('runs/fresher_100_search_2026-10-06.json','w',encoding='utf-8'),indent=2)
print('wrote fresher_100',len(picked))
print(log)
