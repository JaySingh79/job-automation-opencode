import json, pathlib
queue=[
{"platform":"greenhouse","company":"Enterpret","role":"Machine Learning Intern","url":"https://job-boards.greenhouse.io/enterpret/jobs/7723230003","resume":"GenAI_DS","location":"Bengaluru, India"},
{"platform":"greenhouse","company":"Enterpret","role":"Software Engineering Intern Backend","url":"https://job-boards.greenhouse.io/enterpret/jobs/7847134003","resume":"GenAI_DS","location":"Bengaluru, India"},
{"platform":"greenhouse","company":"Rzr","role":"Machine Learning Engineer L3 1-3yr","url":"https://job-boards.greenhouse.io/rzr/jobs/4241380009","resume":"GenAI_DS","location":"Bengaluru, India"},
{"platform":"greenhouse","company":"Anteriad","role":"AI Engineer 1-2yr RAG LangChain","url":"https://job-boards.greenhouse.io/anteriad/jobs/5386350004","resume":"GenAI_DS","location":"Bangalore, India"},
{"platform":"greenhouse","company":"DoorDash India","role":"Software Engineer Backend founding","url":"http://job-boards.greenhouse.io/doordashindia/jobs/5856393","resume":"GenAI_DS","location":"India"},
{"platform":"ashby","company":"Wisdom AI","role":"Software Engineer NLP/ML","url":"https://jobs.ashbyhq.com/Wisdom-AI/93441adc-4cd9-4253-a335-c20a5aa4ada6","resume":"GenAI_DS","location":"Bengaluru, India"},
{"platform":"ashby","company":"Deductive AI","role":"AI Engineer FDE","url":"https://jobs.ashbyhq.com/deductive/124b540e-f84f-46d5-9752-f151361b8223/application","resume":"GenAI_DS","location":"India Remote"},
{"platform":"ashby","company":"Outmarket AI","role":"Full Stack AI Engineer","url":"https://jobs.ashbyhq.com/outmarket/716e3319-1d72-4f8d-b5d9-efb9de1cf72f/application","resume":"GenAI_DS","location":"Remote India"},
{"platform":"ashby","company":"DehazeLabs","role":"Junior Python Developer Rs2-4L","url":"https://jobs.ashbyhq.com/DehazeLabs/3fc045c8-c43d-4523-b258-80e35b2930ed/application","resume":"GenAI_DS","location":"India Remote"},
{"platform":"ashby","company":"Ema","role":"AI/Data Resident final-year remote","url":"https://jobs.ashbyhq.com/ema/e0511c0c-998f-4079-b62c-d2f164bf2c86","resume":"GenAI_DS","location":"India Remote"},
{"platform":"ashby","company":"AHL-SaafAI","role":"Junior Data Engineer 0-2yr","url":"https://jobs.ashbyhq.com/ahl-saafai/ed53ed8f-00aa-4fe6-b177-e1679143e32c","resume":"GenAI_DS","location":"India Remote"},
{"platform":"ashby","company":"Bjak","role":"Applied AI Engineer India Remote","url":"https://jobs.ashbyhq.com/bjakcareer/416c3505-bc04-4b6e-8c60-fae0ea8b947e","resume":"GenAI_DS","location":"India Remote"},
{"platform":"ashby","company":"Proximal","role":"Software Engineer Bengaluru/India LLM infra","url":"https://jobs.ashbyhq.com/Proximal/7f947847-ea9f-41f6-a6c8-147413b9dd6e","resume":"GenAI_DS","location":"Bengaluru/India"},
{"platform":"ashby","company":"Handshake","role":"Member Technical Staff AI Eng India 2-10yr stretch","url":"https://jobs.ashbyhq.com/handshake/4870c024-f6b8-4c2d-a5cb-e94f6c8f94a9","resume":"GenAI_DS","location":"Bangalore, India"},
{"platform":"lever","company":"Merkle Science","role":"SWE Intern Backend","url":"https://jobs.lever.co/merklescience/e663b69b-264a-4bd7-b04d-fb3c0a824a28","resume":"GenAI_DS","location":"Bangalore Hybrid"},
{"platform":"lever","company":"Epifi/Workloom","role":"AI Video Architect Intern","url":"https://jobs.lever.co/epifi/8ec7ec3f-c24f-49b6-9984-14df7006fe7f","resume":"GenAI_DS","location":"Bengaluru In-office"},
{"platform":"lever","company":"OutcomesAI","role":"Backend MLOps Speech Deployment","url":"https://jobs.lever.co/outcomesai/7bbc10a3-805c-441a-8c58-44ab9be9c73c/apply","resume":"GenAI_DS","location":"Bengaluru Onsite"},
{"platform":"lever","company":"Lingaro","role":"ML/AI Engineer India Remote","url":"https://jobs.lever.co/lingarogroup/5b9bd5a9-5953-43cf-a7e5-fe9161ac0f21/apply","resume":"GenAI_DS","location":"India Remote"},
{"platform":"lever","company":"Lingaro Peepal","role":"ML/AI Engineer India Remote","url":"https://jobs.lever.co/lingarogroup/6adf8593-2a35-44d0-9400-0ced651fd403/apply","resume":"GenAI_DS","location":"India Remote"},
{"platform":"lever","company":"Lingaro Adecco","role":"ML/AI Engineer India Remote","url":"https://jobs.lever.co/lingarogroup/18f8d2c5-b52a-4d9f-b4ff-3f71e0fee53d/apply","resume":"GenAI_DS","location":"India Remote"},
{"platform":"lever","company":"Jobgether Classical ML","role":"ML/AI Engineer Classical ML India Remote","url":"https://jobs.lever.co/jobgether/0aec7f97-7358-4643-b5ad-c186165b5d4f","resume":"GenAI_DS","location":"India Remote"},
{"platform":"lever","company":"Jobgether MLE","role":"Machine Learning Engineer India Remote","url":"https://jobs.lever.co/jobgether/ded47afc-192d-4c46-863d-41397012116a","resume":"GenAI_DS","location":"India Remote"},
]
pathlib.Path('src/job_search_results/2026-10-14-apply-queue.json').write_text(json.dumps({"date":"2026-10-14","count":len(queue),"filters":{"exp":"0-3yr inclusive","geo":"India/remote","ats":["ashby","lever","greenhouse"]},"jobs":queue},indent=2),encoding='utf-8')
print(f"wrote {len(queue)}")
