import json
from pathlib import Path

path = Path("src/knowledge_source/ats_workday_oracle_deep_recon.json")
data = json.loads(path.read_text(encoding="utf-8"))

print(f"Total entries: {len(data)}")
for d in data:
    print(f"\n[{d['id']}] {d['company']} ({d['platform']})")
    print(f"  Title: {d['page_title']}")
    print(f"  Load Time: {d['load_time_ms']}ms")
    print(f"  Frameworks: {d['frameworks_detected']}")
    print(f"  Apply Found: {d['apply_button_found']} (Text: '{d['apply_button_text']}')")
    print(f"  Auth Gate: {d['auth_gate_type']}")
    print(f"  Inputs Found: {len(d['input_controls_sample'])}")
    if d['platform'] == 'workday':
        print(f"  WD Automation IDs: {d['dom_metrics'].get('wd_automation_ids', [])[:8]}")
    else:
        print(f"  Custom Elements: {d['dom_metrics'].get('custom_elements', [])[:8]}")
        print(f"  Sample Controls: {[c.get('id') or c.get('name') for c in d['input_controls_sample']]}")
