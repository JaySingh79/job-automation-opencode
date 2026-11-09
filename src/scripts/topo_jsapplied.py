import io

s = io.open(r"D:\Projects\PRACTICE\firecrawl_test\src\applied\jobs_applied.json", encoding="utf-8").read()
lines = s.split("\n")
for i, l in enumerate(lines[3980:4100], start=3981):
    ls = l.strip()
    if ls.endswith("],") or ls == "]" or ls.endswith("[") or ls == "[" or (i % 20 == 0):
        print(i, repr(ls[:70]))
