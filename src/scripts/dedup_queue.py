import json, pathlib
src=pathlib.Path('src/job_search_results/2026-10-13-ashby-lever-greenhouse-3yr-india-remote.json')
data=json.loads(src.read_text(encoding='utf-8'))
print(f"total={len(data['jobs'])}")
from collections import Counter
print(Counter(j['platform'] for j in data['jobs']))
applied=json.loads(pathlib.Path('src/application_progress/ats_progress.json').read_text(encoding='utf-8'))
applied_urls={a.get('url','') for a in applied.get('applied',[])}
applied_urls.update([a.get('url','') for a in applied.get('ashby_fill_2026-09-29',[])])
blocked_urls={b.get('url','') for b in applied.get('blocked',[])}
print(f"applied_n={len(applied_urls)} blocked_n={len(blocked_urls)}")
pending=[j for j in data['jobs'] if j['url'] not in applied_urls and all(j['url'] not in u and u not in j['url'] for u in applied_urls|blocked_urls)]
# also normalize trailing /apply /application
def norm(u): return u.rstrip('/').replace('/apply','').replace('/application','')
applied_norm={norm(u) for u in applied_urls|blocked_urls}
pending2=[j for j in data['jobs'] if norm(j['url']) not in applied_norm]
print(f"pending_norm={len(pending2)}")
for j in pending2:
    print(j['platform']+' | '+j['company']+' | '+j['role'][:70]+' | '+j['url'])
