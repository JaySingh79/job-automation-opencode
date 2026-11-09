import urllib.request
import json

urls = [
    ("cloudsek", "https://job-boards.greenhouse.io/cloudsek/jobs/6222340004"),
    ("coherehealth", "https://job-boards.greenhouse.io/coherehealth/jobs/7693298003"),
    ("doordashindia_de", "https://job-boards.greenhouse.io/doordashindia/jobs/8200625"),
    ("coinbase", "https://job-boards.greenhouse.io/coinbase/jobs/8165441"),
    ("databricks_fde", "https://job-boards.greenhouse.io/databricks/jobs/8771566002")
]

req_headers = {'User-Agent': 'Mozilla/5.0'}

for name, u in urls:
    try:
        req = urllib.request.Request(u, headers=req_headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"[{name}] HTTP {resp.status} - final URL: {resp.url}")
    except Exception as e:
        print(f"[{name}] ERROR: {e}")
