import json

# Worker 5's 43 applied jobs from report
jobs_raw = [
  (1680802, "BrandMyHR", "Product Manager - AI/ML Marketplace"),
  (1677315, "Walt AI", "Senior Software Engineer - AI Native/Data Platform"),
  (1677366, "Natalie Consultants", "Data Engineer - Scala/Spark"),
  (1677187, "Scaling Theory Technologies", "Full Stack Engineer - React.js/Python"),
  (1676564, "Tidyhire", "Software Developer - Python/Java/AngularJS"),
  (1676459, "Onsite Construction Management Software", "Onsite - Flutter Developer - iOS/Android Apps"),
  (1676275, "Innovapptive", "Innovapptive - Site Reliability Engineer - Cloud Infrastructure"),
  (1676209, "CDM Smith", "CDM Smith - Data Analytics Engineer"),
  (1676394, "Evnek", "Evnek - Data Quality Engineer"),
  (1676398, "Terralogic Software Solutions Private Limited.", "Linux System & Python Automation Engineer"),
  (1675989, "Ascendion", "Ascendion - Junior Quality Engineer - Automation Testing"),
  (1674076, "Blueberry Unicorn Services", "Test Engineer - LiveOps"),
  (1679163, "Unico Talent", "Senior AI/ML Engineer - LLM/Generative AI"),
  (1679624, "GrowthsphereAI", "Artificial Intelligence Engineer - LangChain/LangGraph"),
  (1677556, "Big Ideas Social Media Recruitment", "AI Engineer - Generative AI"),
  (1680383, "The Reliable Jobs", "Full Stack Developer - Python/React.js/AngularJS"),
  (1679127, "BlinkRx", "Blink Health - Senior/Staff Software Engineer - AI & Product Engineering"),
  (1680242, "Giskard Datatech", "Trendlyne - Senior QA Automation Engineer - Mobile & Web Testing"),
  (1675795, "Exponentia.ai", "Exponentia.ai - Machine Learning Engineer - MLOps"),
  (1675797, "Exponentia.ai", "Exponentia.ai - Data Analyst/Business Analyst - Customer Analytics"),
  (1675790, "SPI TECHNOLOGIES INDIA PRIVATE LIMITED", "Straive - Senior Consultant - Splunk & ClickHouse"),
  (1675919, "CREDITSAFE TECHNOLOGY", "Creditsafe - Quality Assurance Automation Engineer - Playwright/Cypress/Python"),
  (1675487, "ZOOP", "Zoop.One - Product Manager - Data Sourcing & Engineering"),
  (1675545, "Hula Global", "Machine Learning Engineer"),
  (1675556, "Hula Global", "React Native Engineer - TypeScript"),
  (1675693, "WowJobs", "Automation Engineer - Data Governance"),
  (1675248, "GyFTR", "Vouchagram - Data Engineering Manager"),
  (1675331, "SMC Group of Companies", "SQL Developer - Oracle DB/MySQL/PostgreSQL"),
  (1672627, "Workplace", "Data Scientist - AI/ML"),
  (1681692, "GyFTR", "Vouchagram - DevOps Engineer - Cloud Infrastructure"),
  (1681641, "HR LOBBY", "Full Stack Engineer"),
  (1681557, "CDM Smith", "CDM Smith - Intermediate IT Infrastructure Specialist"),
  (1681588, "Indexnine Technologies", "Indexnine Technologies - Full Stack Developer - React.js/Node.js"),
  (1681620, "Recruitment Hub 365", "Data Engineer - Azure/Microsoft Fabric"),
  (1680253, "Unico Talent", "Full Stack AI Engineer - TypeScript/NestJS"),
  (1675334, "AuxoAI", "Auxo AI - Senior Applied AI Engineer - AI Agents"),
  (1674802, "kaidoko Automation Solutions Pvt", "Kaidoko - DevOps Engineer - AWS"),
  (1673839, "Pi-labs", "Pi-labs - MLOps Engineer"),
  (1673986, "RattanIndia Enterprises", "RattanIndia - Artificial Intelligence/Machine Learning Engineer - Data Modeling"),
  (1673564, "Terralogic Software Solutions Private Limited.", "BI Engineer - Data Analytics"),
  (1673623, "Recruitment Hub 365", "Data Engineer - Microsoft Azure/Microsoft Fabric"),
  (1673660, "Clinvvo", "Senior Frontend Engineer - React.js/React Native"),
  (1673670, "Quadrant IT Services", "Quadrant IT Services - IBM ACE Developer")
]

results = [{"id": jid, "company": comp, "title": title, "status": "applied", "applied": 1} for jid, comp, title in jobs_raw]

worker5_data = {
  "batch": 5,
  "date": "2026-11-06",
  "tab_index": 4,
  "total": 44,
  "applied_count": len(results),
  "closed_count": 1,
  "results": results
}

with open("src/application_progress/hirist/hirist_progress_assessment_batch_5_2026-11-06.json", "w", encoding="utf-8") as f:
    json.dump(worker5_data, f, indent=2)

print("Saved Worker 5 Batch 5 progress file.")
