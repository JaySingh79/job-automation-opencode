import json

worker4_sprint6 = {
  "worker": 4,
  "sprint": 6,
  "batch": 4,
  "target_applied": 3,
  "total_batch_jobs": 6,
  "applied_count": 6,
  "parked_count": 0,
  "already_applied_count": 0,
  "failed_count": 0,
  "status": "COMPLETE",
  "applied_jobs": [
    {"id": 1670445, "applicationId": 79305428, "title": "SCORELABS - Backend Engineer - Python/Golang", "company": "SCORESOFTLABS(OPC)PRIVATE LIMITED", "appliedAt": "2026-11-05T18:46:40Z"},
    {"id": 1669887, "applicationId": 79305430, "title": "NielsenIQ - Software Engineer - PHP/Symfony", "company": "NielsenIQ", "appliedAt": "2026-11-05T18:46:42Z"},
    {"id": 1670165, "applicationId": 79305431, "title": "Software Developer - Python/Java", "company": "Skyleaf Consultants", "appliedAt": "2026-11-05T18:46:44Z"},
    {"id": 1669826, "applicationId": 79305435, "title": "Backend Software Engineer - Ruby/Go", "company": "HyrMe", "appliedAt": "2026-11-05T18:46:45Z"},
    {"id": 1669374, "applicationId": 79305438, "title": "System Engineer - Microservices Architecture", "company": "BinaryStar SearchX", "appliedAt": "2026-11-05T18:46:47Z"},
    {"id": 1669195, "applicationId": 79305442, "title": "AI Engineer - C++/Python", "company": "QuickHyre", "appliedAt": "2026-11-05T18:46:49Z"}
  ],
  "parked_job_ids": []
}

worker5_sprint6 = {
  "worker": 5,
  "sprint": 6,
  "batch": 5,
  "target_applied": 3,
  "total_batch_jobs": 6,
  "applied_count": 5,
  "parked_count": 1,
  "already_applied_count": 0,
  "failed_count": 0,
  "status": "BATCH_EXHAUSTED",
  "applied_jobs": [
    { "id": 1669316, "applicationId": 79305433, "title": "Quadient Inspire Developer - Document Composition Tools", "company": "Upcruit" },
    { "id": 1668919, "applicationId": 79305440, "title": "C# Developer - .Net/ASP", "company": "Code Vyasa" },
    { "id": 1668723, "applicationId": 79305444, "title": "MediaMint - Python Desktop Automation Engineer", "company": "VUCHI MEDIA" },
    { "id": 1668245, "applicationId": 79305446, "title": ".Net Developer - WebForms", "company": "Programming.Com" },
    { "id": 1668206, "applicationId": 79305448, "title": "Senior C++ Developer - Trading Systems", "company": "Break into bfsi" }
  ],
  "parked_job_ids": [1669211]
}

with open("src/application_progress/hirist/hirist_progress_additional_sprint6_batch_4_2026-11-05.json", "w", encoding="utf-8") as f:
    json.dump(worker4_sprint6, f, indent=2)

with open("src/application_progress/hirist/hirist_progress_additional_sprint6_batch_5_2026-11-05.json", "w", encoding="utf-8") as f:
    json.dump(worker5_sprint6, f, indent=2)

print("Saved Worker 4 and Worker 5 Sprint 6 progress files.")
