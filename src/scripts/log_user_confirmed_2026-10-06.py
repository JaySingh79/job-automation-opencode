import json, os
confirm = {
  "date": "2026-10-06",
  "run": "applied-confirm-2026-10-06",
  "verification_mode": "user-confirmed (no screenshots, per user 'log as user-confirmed')",
  "pending_count_before": 11,
  "pending_count_after": 0,
  "jobs": [
    {
      "company": "Scalio",
      "role": "AI Engineer, Agents & Intelligence",
      "url": "https://docs.google.com/forms/d/e/1FAIpQLSfwGInRwRVxoMUzsFKTjLSOdJbFyeV2y21liQgALugUMIBhUw/viewform",
      "platform": "google-forms",
      "location": "Remote (Bengaluru on-site Yes)",
      "exp": "fresher/early-career",
      "prev_status": "STAGED-READY 12/12",
      "status": "applied",
      "applied_date": "2026-10-06",
      "verification": "user-confirmed applied 2026-10-06",
      "source_run": "runs/2026-10-05-direct8-go.json:scalio_ai_engineer_form"
    },
    {
      "company": "IDFC FIRST Bank",
      "role": "Data Scientist, AI Labs",
      "url": "https://www.idfcfirstbank.com/careers (Phenom TXM Step2; exact JD URL from agent ses_ef356b6c3ffeelbDBhB1rSxaI6 to verify)",
      "platform": "phenom",
      "location": "India",
      "exp": "3+yr gap flagged, user override",
      "prev_status": "STAGED Phenom TXM Step2",
      "status": "applied",
      "applied_date": "2026-10-06",
      "verification": "user-confirmed applied 2026-10-06",
      "source_run": "runs/2026-10-05-direct8-go.json:idfc_first_data_scientist_ai_labs"
    },
    {
      "company": "HPE",
      "role": "Data Scientist 1209922",
      "url": "https://careers.hpe.com/us/en/job/1209922/Data-Scientist",
      "platform": "phenom",
      "location": "Bengaluru, Karnataka, India",
      "exp": "5-7yr gap flagged, user override",
      "prev_status": "STAGED Phenom 5/5 Review",
      "status": "applied",
      "applied_date": "2026-10-06",
      "verification": "user-confirmed applied 2026-10-06",
      "source_run": "runs/2026-10-05-direct8-go.json:hpe_data_scientist_1209922"
    },
    {
      "company": "Brillio",
      "role": "Data Scientist - R01571772",
      "url": "https://jobs.lever.co/brillio-2/7a4957bd-c6b9-4f8b-8382-e1bf3e095a7a/apply?lever-source=Job%20postings%20feed",
      "platform": "lever",
      "location": "Bangalore, Hybrid",
      "exp": "YoE not listed; 18mo GenAI/RAG exact",
      "prev_status": "READY FOR HUMAN SUBMISSION",
      "status": "applied",
      "applied_date": "2026-10-06",
      "verification": "user-confirmed applied 2026-10-06",
      "source_run": "runs/2026-10-05-direct8-go.json:brillio_lever_ds"
    },
    {
      "company": "MakeMyTrip",
      "role": "Data Scientist (Darwinbox)",
      "url": "https://careers.makemytrip.com (Darwinbox; exact req URL from agent ses_ef420640bffeoVdQ56cKonGPsO to verify)",
      "platform": "darwinbox",
      "location": "India",
      "exp": "fresher/early-career",
      "prev_status": "STAGED-READY empty_required=0",
      "status": "applied",
      "applied_date": "2026-10-06",
      "verification": "user-confirmed applied 2026-10-06",
      "source_run": "runs/2026-10-05-direct8-go.json:mmt_darwinbox_data_scientist"
    },
    {
      "company": "SymphonyAI",
      "role": "Req 3024 (iCIMS)",
      "url": "https://www.symphonyai.com/careers (iCIMS req 3024; exact URL from agent ses_ef4128eb3ffeN6CcmQD0i8SppP to verify)",
      "platform": "icims",
      "location": "India",
      "exp": "fresher/early-career",
      "prev_status": "BLOCKED human-CAPTCHA",
      "status": "applied",
      "applied_date": "2026-10-06",
      "verification": "user-confirmed applied 2026-10-06",
      "source_run": "runs/2026-10-05-direct8-go.json:symphonyai_3024"
    },
    {
      "company": "Oracle",
      "role": "Cloud Req 15097",
      "url": "https://careers.oracle.com (req 15097; exact URL on retry, agent was cancelled)",
      "platform": "oracle-cloud",
      "location": "India",
      "exp": "fresher/early-career",
      "prev_status": "NOT RUN",
      "status": "applied",
      "applied_date": "2026-10-06",
      "verification": "user-confirmed applied 2026-10-06",
      "source_run": "runs/2026-10-05-direct8-go.json:oracle_cloud_15097"
    },
    {
      "company": "ONE81 (via Instahyre)",
      "role": "AI Engineer",
      "url": "https://www.instahyre.com/candidate/opportunities/job-469519-ai-engineer-at-oneshot-bangalore",
      "platform": "instahyre",
      "location": "Bangalore/Gurgaon, 1-4y",
      "exp": "1-4y Python/LangChain/OpenAI/OCR-Textract/AWS",
      "prev_status": "READY-QUEUED",
      "status": "applied",
      "applied_date": "2026-10-06",
      "verification": "user-confirmed applied 2026-10-06",
      "source_run": "runs/2026-10-05-fillonly-go.json:job_469519"
    },
    {
      "company": "Instahyre job 469517",
      "role": "JD verified in modal (title to verify from modal e384-e616)",
      "url": "https://www.instahyre.com/candidate/opportunities/job-469517 (exact slug to verify)",
      "platform": "instahyre",
      "location": "India",
      "exp": "fresher/early-career",
      "prev_status": "READY-QUEUED",
      "status": "applied",
      "applied_date": "2026-10-06",
      "verification": "user-confirmed applied 2026-10-06",
      "source_run": "runs/2026-10-05-fillonly-go.json:job_469517"
    },
    {
      "company": "Reacher",
      "role": "Backend Software Engineer - India",
      "url": "https://jobs.ashbyhq.com/reacher/86a866da-dc3b-4d5d-ba94-599b642904ec",
      "platform": "ashby",
      "location": "Remote India",
      "exp": "2-6y listed vs 18mo stretch",
      "prev_status": "BLOCKED_QUEUED (Typeform)",
      "status": "applied",
      "applied_date": "2026-10-06",
      "verification": "user-confirmed applied 2026-10-06",
      "source_run": "runs/fresher_50_progress_ashby_b.json + runs/2026-10-05-fillonly-go.json:reacher_ashby"
    },
    {
      "company": "Unknown (Google Form poster)",
      "role": "Data Science Intern | 6-Month Internship + PPO",
      "url": "https://docs.google.com/forms/d/e/1FAIpQLSc8NkkvKJ4b1rb-kpZpUkUhKCKhf6WnrFDHUhCiz6vRjjmu8g/viewform",
      "platform": "google-forms",
      "location": "India",
      "exp": "fresher/intern",
      "prev_status": "READY FOR HUMAN SUBMISSION",
      "status": "applied",
      "applied_date": "2026-10-06",
      "verification": "user-confirmed applied 2026-10-06",
      "source_run": "runs/2026-09-28-google-form-ds-intern.json"
    }
  ]
}
with open('runs/2026-10-06-applied-confirm.json','w',encoding='utf-8') as f:
    json.dump(confirm,f,indent=2)
print('wrote runs/2026-10-06-applied-confirm.json', len(confirm['jobs']))

# append to jobs_applied.json
jp='src/applied/jobs_applied.json'
d=json.load(open(jp,encoding='utf-8'))
d.setdefault('user_confirmed_2026-10-06',[]).extend(confirm['jobs'])
d['total']=d.get('total',0)+len(confirm['jobs'])
d['applied_date']='2026-10-06'
json.dump(d,open(jp,'w',encoding='utf-8'),indent=2)
print('updated',jp,'total',d['total'])

# patch ats_progress.json with new key
ap='src/application_progress/ats_progress.json'
a=json.load(open(ap,encoding='utf-8'))
a['user_confirmed_2026-10-06']=confirm
# flip known READY statuses to applied-user-confirmed where present
for k in ['google-forms_fill_2026-10-05','lever_fill_2026-10-05']:
    arr=a.get(k,[])
    for it in arr:
        if isinstance(it,dict) and it.get('status','').startswith('READY'):
            it['prev_status']=it.get('status')
            it['status']='applied-user-confirmed-2026-10-06'
json.dump(a,open(ap,'w',encoding='utf-8'),indent=2)
print('updated',ap)

# patch ashby-b lane: blocked->applied
ab='runs/fresher_50_progress_ashby_b.json'
b=json.load(open(ab,encoding='utf-8'))
for j in b.get('jobs',[]):
    if j.get('company')=='Reacher' and 'BLOCKED' in j.get('status',''):
        j['prev_status']=j['status']
        j['status']='applied'
        j['applied_date']='2026-10-06'
        j['verification']='user-confirmed applied 2026-10-06'
s=b.get('summary',{})
s['applied_submitted']=s.get('applied_submitted',1)+1
s['blocked_external_queued']=0
b['summary']=s
b['counts']={**b.get('counts',{}),'applied_submitted':s['applied_submitted'],'blocked_queued':0}
json.dump(b,open(ab,'w',encoding='utf-8'),indent=2)
print('updated',ab)
