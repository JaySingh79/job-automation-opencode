import json, io

s = io.open(r"D:\Projects\PRACTICE\firecrawl_test\src\applied\jobs_applied.json", encoding="utf-8").read()
scan = json.JSONDecoder()
st = []
mode = 0
stack = []  # ('{',lineno) or ('[',lineno)
i = 0
line = 1
toksym = set("[]{}")
instr = False
esc = False
while i < len(s):
    c = s[i]
    if instr:
        if esc:
            esc = False
        elif c == "\\":
            esc = True
        elif c == '"':
            instr = False
    else:
        if c == '"':
            instr = True
        elif c in "{[":
            stack.append((c, line))
        elif c in "}]":
            if stack:
                o, ol = stack.pop()
                if (o == "{" and c != "}") or (o == "[" and c != "]"):
                    print("MISMATCH at line", line, "opened", o, "at line", ol, "closing", c)
                    print("CTX:", repr(s[max(0, i-80):i+40]))
                    break
            else:
                print("EXTRA CLOSE at line", line, c)
                print("CTX:", repr(s[max(0, i-80):i+40]))
                break
    if c == "\n":
        line += 1
    i += 1
if not instr:
    if stack and s[i:].strip() == "":
        pass
print("END stack:", stack[-5:] if stack else "CLEAN")
