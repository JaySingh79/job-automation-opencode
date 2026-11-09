import base64

with open(r'C:\Users\binit\.gemini\antigravity-cli\brain\a992e2a2-20f2-4626-9dfa-fbf68a1e2345\.system_generated\steps\1447\output.txt', 'r', encoding='utf-8') as f:
    text = f.read()

prefix = 'data:image/png;base64,'
idx = text.find(prefix)
if idx != -1:
    b64_str = text[idx + len(prefix):].split('"')[0].split('\n')[0].strip()
    data = base64.b64decode(b64_str)
    with open('src/accessability_snapshot/galaxeye_captcha.png', 'wb') as out:
        out.write(data)
    print('Saved captcha successfully')
else:
    print('Prefix not found')
