import pathlib
base = pathlib.Path('D:/Projects/PRACTICE/firecrawl_test/.opencode/agents')
old_single = "- SINGLE-JOB TAB RULE: Only after filling and submitting the current job application can a different tab with a different application be opened. One job at a time \u2014 fill \u2192 verify \u2192 submit \u2192 close \u2014 then next. Never parallel-fill across tabs."
new_single = "- SINGLE-JOB TAB RULE (per-agent sequential, multi-agent parallel): All agents may work in parallel, but each agent must finish the current job (fill \u2192 verify \u2192 submit \u2192 close) before opening a different tab with a different application. One job at a time per agent \u2014 never parallel-fill across tabs within the same agent."
count = 0
for p in base.glob('*/AGENTS.md'):
    t = p.read_text(encoding='utf-8')
    if old_single in t:
        t = t.replace(old_single, new_single)
        p.write_text(t, encoding='utf-8')
        count += 1
        print(f"patched {p.parent.name}")
print(f"total patched={count}")
