import json
q=json.load(open('runs/fresher_100_fill_queues_2026-10-06.json',encoding='utf-8'))
DROP_ASHBY={'https://jobs.ashbyhq.com/playpowerlabs/6087e852-9d62-4103-aa77-c3773974549a','https://jobs.ashbyhq.com/aiprise/3763c791-a387-4078-9ca4-00cbfbf9b1a6','https://jobs.ashbyhq.com/careway/f7bc5fce-abe3-490e-ab6b-d3eb1e7be423'}
q['ashby']=[j for j in q['ashby'] if j['url'].split('?')[0].rstrip('/') not in DROP_ASHBY and 'mistral' not in j['url'].lower()]
DROP_LEVER={'https://jobs.lever.co/gotogroup/dff2a165-d111-4542-bfec-ec3856892275','https://jobs.lever.co/shyftlabs/1a665cf5-1f3f-4610-be00-b46ffa13a675','https://jobs.lever.co/drivetrain/7266784e-530b-4eb5-a61b-b09557f6e98d'}
q['lever']=[j for j in q['lever'] if j['url'].lower().split('?')[0].rstrip('/').replace('/apply','') not in {d.replace('/apply','') for d in DROP_LEVER}]
for j in [j for j in q['ashby']+q['lever'] if False]: pass
json.dump(q,open('runs/fresher_100_fill_queues_2026-10-06.json','w',encoding='utf-8'),indent=2)
print({k:len(v) for k,v in q.items()})
