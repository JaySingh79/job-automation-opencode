import json, pathlib
base = pathlib.Path(r"D:\Projects\PRACTICE\firecrawl_test\src\applied\hirist_2026-10-08.json")
data = json.loads(base.read_text())
new_applied = [
  {"jobId": 1676039, "applicationId": None, "title": "Robotics Applied AI Engineer - Python", "company": "TELUS Digital", "url": "https://www.hirist.tech/j/telus-digital-robotics-applied-ai-engineer-python-1676039", "applied_at": "2026-10-08T14:10Z", "mode": "1-click", "resume": "ML_Vision"},
  {"jobId": 1675617, "applicationId": None, "title": "Senior AI/ML Engineer LangChain LangGraph", "company": "Unknown", "url": "https://www.hirist.tech/j/senior-ai-ml-engineer-langchain-langgraph-1675617", "applied_at": "2026-10-08T14:10Z", "mode": "1-click", "resume": "GenAI_DS"},
  {"jobId": 1677325, "applicationId": None, "title": "AI Platform Engineer", "company": "KreditBee", "url": "https://www.hirist.tech/j/kreditbee-ai-platform-engineer-1677325", "applied_at": "2026-10-08T14:10Z", "mode": "1-click", "resume": "GenAI_DS"},
  {"jobId": 1676496, "applicationId": None, "title": "AI/ML Engineer", "company": "OZI", "url": "https://www.hirist.tech/j/ozi-ai-ml-engineer-1676496", "applied_at": "2026-10-08T14:10Z", "mode": "screening", "resume": "GenAI_DS"},
  {"jobId": 1670198, "applicationId": None, "title": "Senior AI/ML Engineer", "company": "Freecharge", "url": "https://www.hirist.tech/j/freecharge-payment-technologies-senior-ai-ml-engineer-1670198", "applied_at": "2026-10-08T14:10Z", "mode": "screening", "resume": "GenAI_DS"},
  {"jobId": 1670016, "applicationId": None, "title": "Senior AI Engineer LLM", "company": "Brillio", "url": "https://www.hirist.tech/j/brillio-technologies-senior-ai-engineer-llm-1670016", "applied_at": "2026-10-08T14:10Z", "mode": "1-click", "resume": "GenAI_DS"},
  {"jobId": 1674763, "applicationId": None, "title": "Applied Computer Vision Engineer", "company": "Syook", "url": "https://www.hirist.tech/j/syook-applied-computer-vision-engineer-1674763", "applied_at": "2026-10-08T14:10Z", "mode": "screening", "resume": "ML_Vision"},
  {"jobId": 1674280, "applicationId": None, "title": "Data Scientist II", "company": "Setu", "url": "https://www.hirist.tech/j/setu-data-scientist-ii-1674280", "applied_at": "2026-10-08T14:10Z", "mode": "1-click", "resume": "GenAI_DS"},
  {"jobId": 1672857, "applicationId": None, "title": "SDE II Voicebot", "company": "Exotel", "url": "https://www.hirist.tech/j/exotel-software-development-engineer-ii-voicebot-1672857", "applied_at": "2026-10-08T14:10Z", "mode": "1-click", "resume": "GenAI_DS"},
]
existing_ids = {x.get("jobId") for x in data.get("applied", [])}
for j in new_applied:
    if j["jobId"] not in existing_ids:
        data["applied"].append(j)
base.write_text(json.dumps(data, indent=1))
print(f"merged total applied={len(data['applied'])}")
