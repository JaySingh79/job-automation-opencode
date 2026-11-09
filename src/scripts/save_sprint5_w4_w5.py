import json

worker4_data = {
    "worker": 4,
    "sprint": 5,
    "batch": 4,
    "target_applied": 12,
    "total_batch_jobs": 17,
    "applied_count": 11,
    "parked_count": 6,
    "already_applied_count": 0,
    "failed_count": 0,
    "status": "COMPLETE",
    "applied_jobs": [
        {"id": 1681955, "applicationId": 79305337, "title": "Falcon - Senior Software Developer - Java", "company": "Falcon India", "appliedAt": "2026-11-05T18:41:51Z"},
        {"id": 1681672, "applicationId": 79305339, "title": "Java Microservices Engineer - Agentic AI Integration", "company": "HiringBlaze", "appliedAt": "2026-11-05T18:41:52Z"},
        {"id": 1678631, "applicationId": 79305342, "title": "InfoBeans Technologies - Java Developer - AI Assisted Development", "company": "InfoBeans", "appliedAt": "2026-11-05T18:41:59Z"},
        {"id": 1678277, "applicationId": 79305345, "title": "BotLab Dynamics - Unreal Engine Developer - C++", "company": "BotLab Dynamics", "appliedAt": "2026-11-05T18:42:01Z"},
        {"id": 1678180, "applicationId": 79305346, "title": "K4 Mobility India - Backend Engineer - Node.js Framework", "company": "K4 Mobility", "appliedAt": "2026-11-05T18:42:02Z"},
        {"id": 1678005, "applicationId": 79305354, "title": "Sciative Solutions - Full Stack Developer - Python/Django", "company": "Sciative - We Price Right", "appliedAt": "2026-11-05T18:42:20Z"},
        {"id": 1677894, "applicationId": 79305356, "title": "True Credits - Software Engineer - Java/J2EE", "company": "TRUE CREDITS PRIVATE LIMITED", "appliedAt": "2026-11-05T18:42:22Z"},
        {"id": 1677809, "applicationId": 79305359, "title": "Solution Architect", "company": "Axnode Immigration", "appliedAt": "2026-11-05T18:42:24Z"},
        {"id": 1677802, "applicationId": 79305360, "title": "Software Programmer - Java/Python", "company": "Axnode Immigration", "appliedAt": "2026-11-05T18:42:25Z"},
        {"id": 1677810, "applicationId": 79305363, "title": "Backend Developer - Node.js/Spring Boot", "company": "Axnode Immigration", "appliedAt": "2026-11-05T18:42:27Z"},
        {"id": 1672761, "applicationId": 79305368, "title": "OZI - Backend Engineer - Node.js/Java", "company": "OZI Technologies", "appliedAt": "2026-11-05T18:42:32Z"}
    ],
    "parked_job_ids": [1681391, 1680259, 1679385, 1678110, 1677740, 1677405]
}

worker5_data = {
    "worker": 5,
    "sprint": 5,
    "batch": 5,
    "target_applied": 12,
    "total_batch_jobs": 17,
    "applied_count": 9,
    "parked_count": 8,
    "already_applied_count": 0,
    "failed_count": 0,
    "status": "BATCH_EXHAUSTED",
    "applied_jobs": [
        { "id": 1665631, "applicationId": 79305335, "title": "Software Development Engineer II - Python", "company": "Ensemble Health Partners" },
        { "id": 1670331, "applicationId": 79305336, "title": "SatSure - Software Development Engineer II - Java/Python", "company": "SatSure" },
        { "id": 1669079, "applicationId": 79305338, "title": "C++ Developer - Multiprocessing & Multithreading", "company": "VASINFOTEC " },
        { "id": 1666184, "applicationId": 79305340, "title": "OZI - Backend Engineer - Java/Node.js", "company": "OZI Technologies" },
        { "id": 1662143, "applicationId": 79305343, "title": "Garmin - Software Development Engineer - Python/Node.js", "company": "Garmin Technologies" },
        { "id": 1676768, "applicationId": 79305364, "title": "Senior Software Engineer - Java", "company": "TalentGen Advisory LLP" },
        { "id": 1676682, "applicationId": 79305365, "title": "Circular Angle - Software Developer - .Net Technologies", "company": "Circular Angle" },
        { "id": 1675962, "applicationId": 79305370, "title": "Java/Niagara Consultant", "company": "Xohani Solutions Pvt. Ltd." },
        { "id": 1675662, "applicationId": 79305371, "title": "Josys - Senior Software Engineer - Node.js/Ruby on Rails", "company": "Josys" }
    ],
    "parked_job_ids": [1666551, 1662835, 1661997, 1677186, 1676905, 1676493, 1675973, 1675921]
}

with open("src/application_progress/hirist/hirist_progress_additional_sprint5_batch_4_2026-11-05.json", "w", encoding="utf-8") as f:
    json.dump(worker4_data, f, indent=2)

with open("src/application_progress/hirist/hirist_progress_additional_sprint5_batch_5_2026-11-05.json", "w", encoding="utf-8") as f:
    json.dump(worker5_data, f, indent=2)

print("Saved Worker 4 and Worker 5 progress files.")
