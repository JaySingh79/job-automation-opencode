import json

workers = {
    'Worker 2': '18d0b21f-737b-4d0e-9184-26762f325107',
    'Worker 3': 'b09047d3-fe80-4dc2-ac08-3af20e4cb16b',
    'Worker 4': '4075bc31-174e-4d0c-96fe-d67240043fe2',
    'Worker 5': '1685cdd9-93b9-4bb0-a744-14f0a099005b'
}

for name, cid in workers.items():
    path = f'C:/Users/binit/.gemini/antigravity-cli/brain/{cid}/.system_generated/logs/transcript.jsonl'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"{name} ({cid[:8]}): {len(lines)} steps")
            for line in reversed(lines):
                d = json.loads(line)
                if d.get('type') == 'PLANNER_RESPONSE' and d.get('thinking'):
                    t = d['thinking'].replace('\n', ' ')
                    print(f"   last thought: {t[:120]}...")
                    break
    except Exception as e:
        print(f"{name}: {e}")
