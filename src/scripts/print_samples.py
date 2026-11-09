import json
from pathlib import Path

for name in ['ashby', 'lever', 'greenhouse']:
    f = Path(f'src/job_search_results/ashby_lever_greenhouse/2026-11-07-{name}-100.json')
    data = json.loads(f.read_text(encoding='utf-8'))
    print(f"\n=== {name.upper()} SAMPLES (Total: {data['count']}) ===")
    for j in data['jobs'][:5]:
        print(f"  • {j['title']} @ {j['org']} ({j['location']}) [{j['category']}]")
        print(f"    {j['url']}")
