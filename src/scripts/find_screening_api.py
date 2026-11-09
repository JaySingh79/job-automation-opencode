import urllib.request

url = 'https://js-static.hirist.tech/production/25.0.0/_next/static/chunks/2958.c6062e37d8d21d4e.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8')
        idx = content.find('jobseeker-screening-container')
        if idx != -1:
            snippet = content[max(0, idx - 2500) : max(0, idx - 1500)]
            print("--- SNIPPET COMPONENT PROPS ---")
            print(snippet)
except Exception as e:
    print("Error:", e)
