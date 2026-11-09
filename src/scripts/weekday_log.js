const fs = require("fs");
function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8").replace(/^﻿/, ""));
}
const ap = "src/application_progress/ats_progress.json";
const d = readJson(ap);
d.blocked.push({
  company: "Weekday",
  role: "Software Engineer Intern (client role, Bengaluru Remote)",
  url: "https://jobs.lever.co/weekdayworks/a86efff4-1c2e-43fc-8ecb-dc8f873db2f1/apply",
  platform: "lever",
  location: "Bengaluru, India (Remote)",
  resume: "GenAI_DS (Jay Resume GenAI+DS 5th Aug.pdf, 130007 bytes, %PDF verified, Success! + filename + resumeStorageId persisted)",
  status: "awaiting_human_captcha_submit",
  exp: "0yr SDE Python fits",
  salary: "JD band 3-6 LPA (BELOW 22 LPA floor; fill+submit per override, floor gap flagged)",
  filled: [
    "Full name Jay Singh",
    "Email jays.iitkgp@gmail.com",
    "Phone +91-8651274328",
    "Location Gaya, Bihar, India",
    "Company Pibit AI (YC W21)",
    "LinkedIn URL https://linkedin.com/in/jay-singh-ds/",
    "Current salary 0 (no full-time salary fact in profile; fresher proxy, flagged)",
    "Notice Immediately available"
  ],
  verification: "URL-guarded evaluate on /apply: 0 empty required, Success! true, select=Immediately available; screenshot src/accessability_snapshot/weekday/review-ready-captcha.png",
  reason: "READY-filled; hCaptcha checkbox challenge open after submit click (visible widget) - human must solve checkbox + click Submit application on tab 1",
  date: "2026-10-13"
});
fs.writeFileSync(ap, JSON.stringify(d, null, 2));
const jp = "src/job_search_results/job_links.json";
const j = readJson(jp);
j.Weekday = "https://jobs.lever.co/weekdayworks/a86efff4-1c2e-43fc-8ecb-dc8f873db2f1";
fs.writeFileSync(jp, JSON.stringify(j));
console.log("OK blocked=" + d.blocked.length + " links=" + Object.keys(j).length);
