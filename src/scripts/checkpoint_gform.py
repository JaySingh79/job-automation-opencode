import json, pathlib
p = pathlib.Path('src/application_progress/ats_progress.json')
data = json.loads(p.read_text(encoding='utf-8'))
data.setdefault('applied', []).append(
 {"company":"Unlisted (AI/ML Internship, Bengaluru)","role":"AI/ML Intern (6-month, Bengaluru office)","url":"https://docs.google.com/forms/d/e/1FAIpQLSewQMiOcp5slQMJb9_5OCpykLwyBwkxthkKht6K8Z1HVu5JnQ/viewform","platform":"google-form","location":"Bengaluru, India","resume":"GenAI_DS (Jay Resume GenAI+DS 5th Aug.pdf, Drive upload OK)","status":"applied","exp":"Final-year/recent-grad Yes; B.Tech/B.E.; 6-month availability","salary":"Internship (stipend undisclosed)","verification":"'Your response has been recorded.' + screenshot google-form-aiml-intern-submitted.png; all radios/grid/checkboxes verified checked, resume attached","applied_date":"2026-10-14","submitted_by":"primary agent per user direct 'fill thi' order"}
)
p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"applied_total={len(data['applied'])}")
