import json, re
d=json.load(open('src/job_search_results/fresher_100_2026-10-06.json',encoding='utf-8'))
# applied set
applied=set()
for fp in ['src/applied/jobs_applied.json','src/application_progress/ats_progress.json','runs/2026-10-06-applied-confirm.json']:
    try:
        o=json.load(open(fp,encoding='utf-8'))
        def walk(x):
            if isinstance(x,dict):
                for k,v in x.items():
                    if k=='url' and isinstance(v,str): applied.add(v.lower().split('?')[0].rstrip('/'))
                    else: walk(v)
            elif isinstance(x,list):
                for i in x: walk(i)
        walk(o)
    except Exception as e: print(fp,e)

UUID=re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}',re.I)
def direct(q):
    u=q['url']; p=q['platform']; ul=u.lower()
    if p=='ashby': return 'jobs.ashbyhq.com/' in ul and bool(UUID.search(u))
    if p=='greenhouse': return '/jobs/' in ul and re.search(r'/jobs/\d+',u) is not None
    if p=='lever': return 'jobs.lever.co/' in ul and len(u.rstrip('/').split('/'))>=5
    if p=='wellfound': return re.search(r'/jobs/\d+-',u) is not None
    if p=='workday': return '/job/' in ul
    if p=='keka': return '/jobdetails/' in ul
    if p=='smartrecruiters': return bool(re.search(r'jobs\.smartrecruiters\.com/.+/\d+',u)) or bool(re.search(r'jobs\.smartrecruiters\.com/.+/[a-z0-9\-]{10,}',u))
    if p=='workable': return '/j/' in ul
    if 'recruitee.com/o/' in ul: return True
    return False

queues={'ashby':[],'greenhouse':[],'lever':[],'wellfound':[],'workday':[],'keka_recon':[],'smartrecruiters_recon':[],'workable_recon':[],'recruitee_recon':[],'skipped':[]}
for j in d['jobs']:
    key=j['url'].lower().split('?')[0].rstrip('/')
    reason=None
    if key in applied: reason='already-applied'
    elif not direct(j): reason='not-direct-board-root-or-aggregator'
    elif 'sr. software' in j['role'].lower() and 'sr ' in j['role'].lower(): reason='senior-title'
    if reason:
        queues['skipped'].append({'url':j['url'],'role':j['role'],'platform':j['platform'],'reason':reason})
        continue
    p=j['platform']
    item={'company':j['company'],'role':j['role'],'url':j['url'],'location':j['location'],'exp_tag':j['exp_tag']}
    if p=='ashby': queues['ashby'].append(item)
    elif p=='greenhouse': queues['greenhouse'].append(item)
    elif p=='lever': queues['lever'].append(item)
    elif p=='wellfound': queues['wellfound'].append(item)
    elif p=='workday': queues['workday'].append(item)
    elif p=='keka': queues['keka_recon'].append(item)
    elif p=='smartrecruiters': queues['smartrecruiters_recon'].append(item)
    elif p=='workable': queues['workable_recon'].append(item)
    else:
        # recruitee or other with direct o/ link
        if 'recruitee.com/o/' in j['url']: queues['recruitee_recon'].append(item)
        else: queues['skipped'].append({'url':j['url'],'role':j['role'],'platform':j['platform'],'reason':'no-fill-agent-and-not-direct-ats'})
print({k:len(v) for k,v in queues.items()})
json.dump(queues,open('runs/fresher_100_fill_queues_2026-10-06.json','w',encoding='utf-8'),indent=2)
print('wrote queues')
