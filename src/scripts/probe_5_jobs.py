import urllib.request
import ssl
import re
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

urls = [
    'https://careers.avantorsciences.com/machine-learning-engineer-data-scientist/job/R-175863',
    'https://careers.amgen.com/en/job/-/-/87/102633661840?src=Linkedin',
    'https://careers.qualcomm.com/careers/job/446721093420?hl=en-US&domain=qualcomm.com&source=APPLICANT_SOURCE-6-2',
    'https://jobs.siemens.com/en_US/externaljobs/JobDetail/527567?source=LinkedIn&sourceType=PREMIUM_POST_SITE',
    'https://jobs.bureau.id/bureau/2b7f3dda-fba7-499c-934d-b0fdfb21fe08/?Src=LI+Inbound',
    'https://jobs.ashbyhq.com/bureau/2b7f3dda-fba7-499c-934d-b0fdfb21fe08'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers=req_headers)
        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
            final_url = resp.geturl()
            html = resp.read().decode('utf-8', errors='ignore')
            print(f"=== {u} ===")
            print(f"Final URL: {final_url}")
            
            # Find title
            title_m = re.search(r'<title>(.*?)</title>', html, re.I | re.S)
            print("Title:", title_m.group(1).strip() if title_m else "N/A")
            
            # Find apply or external redirect links
            apply_links = re.findall(r'href=["\']([^"\']*(?:apply|workday|eightfold|avature|successfactors|ashby)[^"\']*)["\']', html, re.I)
            unique_apply = list(dict.fromkeys(apply_links))[:8]
            print("Apply links found:", unique_apply)
            
            # Check for WD / Phenom / Eightfold tokens
            if "myworkdayjobs.com" in html:
                wd = re.findall(r'https://[^"\']*myworkdayjobs\.com[^"\']*', html)
                print("Workday link in HTML:", wd[:3])
            if "eightfold.ai" in html or "pcs" in html:
                ef = re.findall(r'https://[^"\']*eightfold\.ai[^"\']*', html)
                print("Eightfold link in HTML:", ef[:3])
            print()
    except Exception as e:
        print(f"=== {u} === ERROR: {e}\n")
