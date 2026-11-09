"""select_final_100.py — v2: tight pick of exactly 100 from 2026-10-17 harvest pool."""
import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
POOL = ROOT / "src" / "job_search_results" / "2026-10-17-harvest-pool.json"
OUT = ROOT / "src" / "job_search_results" / "2026-10-17-fresh-100-final.json"
POOL2 = ROOT / "src" / "job_search_results" / "2026-10-17-harvest-pool-2.json"

INDIA_RE = re.compile(r"\bindia\b", re.I)  # word-boundary (kill Indianapolis bug)
EXPLICIT_JUNIOR = re.compile(r"\b(intern|internship|trainee|graduate|grad|associate|junior|jr\.?|entry|fresher)\b", re.I)
LEVELI = re.compile(r"\b(engineer|developer|sde|scientist|analyst)\s*(i\b|1\b)", re.I)
EXCL = re.compile(
    r"\b(senior|sr\b|principle|principal|staff|lead|manager|director|head|architect|president|vp|specialist|"
    r"frontend|front-end|front end|qa|recruiting|recruitment|sales|marketing|growth|customer|"
    r"business|financial|legal|design|supply|clinical|revenue|founder|industrial|advisor|copy|support|"
    r"program manager|trainer|annotat|label|linguist|freelance|freelancer|gtm|creative|"
    r"test engineer|tester|in test\b|representative|latam|anz"
    r")", re.I)
LEVELTAIL = re.compile(r"(engineer|developer|scientist|analyst)\s*[-(]?\s*(ii|iii)\b|\blevel\s*(ii|iii|2|3)\b", re.I)
BLOCKUS = re.compile(r"\b(usa|united states|united kingdom|canada|chicago|illinois|austria|germany|europe|singapore|australia|japan|korea|taiwan|hong kong|switzerland|sweden|netherlands|denmark|poland|mexico|brazil|philippines|indonesia|vietnam|thailand|malaysia)\b|\bus\b|\buk\b|\bemea\b|\blatam\b", re.I)
POISON = {
    "greenhouse:conga:5195218007",
    "ashby:gradera:5688991e-7223-4d21-a498-d97a4305c1fd",
    "ashby:level-ai:ca929224-a050-487e-85c3-72969ad935ea",
    "greenhouse:gitlab:8861748002",
    "greenhouse:gravitonresearchcapital:8456543002",
    "greenhouse:hackerrank:8273522",
    "greenhouse:datacor:5242412007",
    "greenhouse:datacor:5257433007",
    "greenhouse:pinterest:8140217",
    "greenhouse:abnormalsecurity:8015179003",
    "greenhouse:affirm:8017340003",
    "greenhouse:coinbase:8265721",
    "greenhouse:gravitonresearchcapital:8764240002",
    "greenhouse:gravitonresearchcapital:8620641002",
    "greenhouse:godaddy:7728664003",
    "greenhouse:skildai-careers:4483966008",
    "greenhouse:stripe:8175647",
    "greenhouse:stripe:8080454",
    "greenhouse:roblox:8020695",
    "greenhouse:roblox:7705949",
    "greenhouse:roblox:8213384",
    "ashby:interview-kickstart:42d5a3d3-662a-4eca-b354-54c6b57c3cfe",
    "ashby:applied:3137ff11-69ad-4a24-8086-36ef9249c611",
    "ashby:ema:c6ec72b0-dce1-422c-895f-9f22c4762a76",
    "ashby:pencil:8a19093b-a687-418b-8eba-4fa08adece8c",
    "ashby:quora:b2462dc7-08d7-4060-8ceb-9a1fa16615fb",
    "ashby:reacher:dbe074b7-0fad-47a8-9623-a18b5a97be72",
    "ashby:reacher:e4d436eb-dd77-44d0-9586-44d48ad84aea",
    "ashby:realmalliance:0a111fba-b589-423b-809d-7b8afe848afc",
    "ashby:bio:b79d687d-541b-425c-be29-143dc065da9b",
    "ashby:bio:a40c8d4d-c2e2-45eb-97a3-4d95f9846794",
    "lever:veeva:a89d4ff8-b50b-4e56-9b74-0823d2751c66",
    "lever:weekdayworks:e9bcc660-1732-4f33-86cc-7bad9ffd3f82",
    "lever:weloglobal:a808d5c0-b4cc-4a3e-b328-bd3b82576976",
    "lever:weloglobal:622bd924-7c24-42dc-9f31-8a4c54d84138",
    "lever:netomi:0e6b7355-330a-4d10-b8d5-c235bd555622",
    "lever:endpointclinical:f16ac3ae-eb44-4b4d-ae87-047ced76f362",
    "lever:endpointclinical:b36d9226-fdfa-40a9-b269-ec9281148f70",
    "lever:endpointclinical:7cfe0d10-e1be-4819-9e27-34e7532b495f",
    "lever:endpointclinical:f6d73ecb-7b57-4e4d-a9db-a36f31db32b9",
    "lever:lingarogroup:024d2a5f-c701-4679-9927-2e831b8aa708",
    "lever:lingarogroup:61654964-c8c7-4f7c-b2f1-3f145a21198a",
    "lever:lingarogroup:f3231a28-9a57-41f2-8bd0-5638bc520904",
    "lever:lingarogroup:b8cd98ac-d72b-48db-85a4-2986f9d9959f",
    "lever:lingarogroup:b57c92ac-62af-40c0-a5d6-d2fa2b4444db",
    "lever:brillio-2:fbeb1776-9c39-4225-a211-b4e0e307b140",
    "lever:brillio-2:e899238d-c1f9-4196-8595-16d64cb1aff7",
    "lever:brillio-2:4eab5886-5daf-42f2-bdfb-e0fb8dcc8b8c",
    "lever:zimperium:6b50bb8b-2a86-4e93-8c17-39b66f3e0789",
    "ashby:bjakcareer:331d1126-1315-48ec-b585-dd05567384f5",
    "ashby:espa:6fa2d441-971f-44c4-9a4e-3304ea041cc8",
    "lever:brillio-2:8463adae-9020-420e-80ef-1cf8ea03580d",
    "lever:brillio-2:04883aa8-c6d4-4fd0-8862-5c371f8991b1",
    "lever:brillio-2:efc3b8ea-6a7b-42a7-8bde-d10957bde4ce",
    "lever:lingarogroup:fcee6859-e315-410e-8a3a-6926ff2a6a58",
    "lever:lingarogroup:2f83b9ea-e0fe-4fdb-89a4-e2dd8f286405",
    "lever:lingarogroup:853310f4-9cc3-45b7-ac29-cf5a624f3c40",
    "greenhouse:gravitonresearchcapital:8788938002",
    "greenhouse:bswiftindia:4714421006",
    "greenhouse:coinbase:7985187",
    "greenhouse:stripe:8172503",
    "greenhouse:stripe:7819426",
    "greenhouse:coinbase:8099099",
    "ashby:interview-kickstart:1adaceae-e7cc-46b7-bf7c-07d05218fee6",
    "ashby:openai:6ba0ce24-ad32-4c3b-b49c-b373be9a8480",
    "ashby:openai:894ce80d-c587-4ef0-92d2-b16deb9a06b9",
    "ashby:openai:d44d9fac-3a9f-4731-a4fc-7a6759ddb427",
    "ashby:outmarket:96a0b0b9-4d09-43d1-a429-776b6e54bd36",
    "ashby:outmarket:0a51cbbb-709e-4c4d-b40f-1f4c06487a73",
    "ashby:realmalliance:49a2da18-3088-43af-a4ba-4db2096abb37",
    "ashby:runpod:475e7a21-59af-4ef4-b2a3-6a0e60fc1356",
    "ashby:runpod:9026d3b8-b736-4bb4-b269-e0b60a7f51ef",
    "ashby:sift:03d426f0-2e0f-408a-9433-55b7a10d1da3",
    "ashby:handshake:7788a34b-f112-467a-ba9a-b8245f8fccfb",
    "ashby:true-talent-solutions-partners:336f1b06-f6cd-4625-81af-f93a9517f3b1",
    "ashby:hex:3f3c943c-7d46-46a7-bc58-5a66785c1e87",
    "ashby:hex:bc90f3b8-79f6-4e7d-a70d-1f00db80deb5",
    "ashby:hex:a059b174-d3ac-4916-b66b-eacdcf436500",
    "ashby:helm-ai:aa111a3f-6a13-4a1d-9932-7c259849f57e",
    "ashby:helm-ai:0b3ebe5a-3cbb-419f-b5d3-4c986b344338",
    "ashby:helm-ai:3570e1b3-cd69-4971-a3b2-786d2a7f52ef",
    "ashby:fal-ai:7fbe1d25-29fb-41bb-bd52-4c8f7f277201",
    "ashby:bio:515cd00c-c691-4082-8036-606ec1a47a2c",
    "lever:brillio-2:e4a4be2d-48cb-4d7e-b912-79d0ac8076a5",
    "lever:brillio-2:265bed8f-1d77-462c-b7ab-b82c4b129bd0",
    "lever:brillio-2:1d2ab0dd-9cf0-41d0-b2c3-dad339829747",
    "lever:lingarogroup:e8f2ef16-8d44-4051-8dad-effd2b690086",
    "lever:lingarogroup:cd1d33c9-de62-40d9-9fec-d15aa8fe81c6",
    "lever:lingarogroup:553e0c1b-895e-401c-824b-e83bb983f225",
    "lever:offchainlabs:d7724d91-fc91-4697-baf3-008de0ee5e37",
    "lever:supermove:a0d545ec-c114-45e5-8707-16e5c1997182",
    "lever:weloglobal:46235545-adae-4d7c-8ed3-eaed18085c50",
    "lever:weloglobal:2de8ebba-9e8c-464f-8a9d-1df0224b043b",
    "ashby:quora:40659fe7-545e-4b08-b6d7-2567b18b9ed3",
    "ashby:quora:cf34f80e-fe5c-454d-bc9a-4c59993ffda0",
    "ashby:realmalliance:a8a2f78e-1c28-4b52-a77a-c2b2ad9b7a8a",
    "ashby:realmalliance:56d8b433-31ad-43a2-997e-b8538f5f2c9f",
    "lever:jobgether:e86bf0f2-104d-45b3-bf5e-6ad2ccfe703f",
    "lever:jobgether:0b788cd9-8998-435a-8387-9d5cf7906403",
    "lever:jobgether:058b3c8d-0a0b-4f77-8e59-854469963f76",
    "lever:jobgether:d5829447-5ecf-4dbe-95e1-fc0f2b49d34d",
    "ashby:bjakcareer:4e7b3e1f-4f8a-49f5-b89a-5bc70ed7576b",
    "ashby:bjakcareer:7e1b725f-c1a3-43e3-87a0-ebdc62eab301",
    "greenhouse:anaplan:8686852002",
    "greenhouse:anaplan:8772322002",
    "greenhouse:jumio:4713139005",
    "greenhouse:jumio:4664041005",
    "greenhouse:jumio:4708116005",
    "greenhouse:okta:7727730",
    "lever:saviynt:5e6c1380-3bd7-49bb-bb6b-7514b89925ba",
}
CAP_OVERRIDE = {"jobgether": 10, "bjakcareer": 8}
GOOD = re.compile(r"\b(software|sde|backend|back-end|back end|full\s?stack|machine|learning|\bml\b|\bai\b|llm|genai|generative|data|engineer|developer|scientist|devops|platform|research|nlp)\b", re.I)


def base_score(j):
    s = 0.0
    tl = (j.get("title") or "").lower()
    if j.get("geo_tag") == "india":
        s += 3
    else:  # remote: only count if explicitly junior
        if not EXPLICIT_JUNIOR.search(tl):
            s -= 6
    if EXPLICIT_JUNIOR.search(tl):
        s += 2
    if LEVELI.search(tl):
        s += 1
    if j.get("updated", "") >= "2026-10-01":
        s += 0.5
    return s


def hard_ok(j):
    t = j.get("title") or ""
    if EXCL.search(t) or LEVELTAIL.search(t) or not GOOD.search(t):
        return False
    lv = j.get("location") or ""
    if j.get("geo_tag") == "india":
        if not INDIA_RE.search(lv):
            return False
    elif BLOCKUS.search(lv):
        return False
    return True


jobs = [j for j in json.loads(POOL.read_text(encoding="utf-8"))["jobs"] + (json.loads(POOL2.read_text(encoding="utf-8"))["jobs"] if POOL2.exists() else []) if hard_ok(j) and j["key"] not in POISON and j["org"] != "brillio-2"]
seen, uniq = set(), []
for j in jobs:
    k = j["key"].lower()
    if k not in seen:
        seen.add(k)
        uniq.append(j)
jobs = uniq
jobs.sort(key=base_score, reverse=True)
print("ELIGIBLE POOL SIZE:", len(jobs))

org_cap = {}
picked = []
for j in jobs:
    org = j["org"]
    if org_cap.get(org, 0) >= CAP_OVERRIDE.get(org, 3):
        continue
    org_cap[org] = org_cap.get(org, 0) + 1
    t = (j.get("title") or "").lower()
    flags = []
    if not EXPLICIT_JUNIOR.search(t) and not LEVELI.search(t):
        flags.append("needs_jd_check")  # no explicit junior/level marker
    j["flags"] = flags
    picked.append(j)

out = picked[:100]
OUT.write_text(json.dumps({"date": "2026-10-17", "count": len(out), "jobs": out}, indent=1, ensure_ascii=False), encoding="utf-8")
print("FINAL COUNT:", len(out))
print("BY PLATFORM:", dict(Counter(x["platform"] for x in out)))
print("BY GEO:", dict(Counter(x["geo_tag"] for x in out)))
print("FLAGGED:", sum(1 for x in out if x["flags"]))
print("-" * 60)
for j in out:
    f = ",".join(j["flags"]) or "-"
    print(f'{j["platform"][0].upper()} | {j["geo_tag"][:2]} | {f[0]} | {(j["title"] or "")[:56]:<56} | {(j["location"] or "")[:36]:<36} | {j["org"][:24]:<24} | {j["url"][-60:]}')
print("=" * 60)
print("BACKUP CANDIDATES (rank 101+):")
for j in jobs[100:160]:
    print(f'{j["platform"][0].upper()} | {j["geo_tag"][:2]} | {(j["title"] or "")[:56]:<56} | {(j["location"] or "")[:36]:<36} | {j["org"][:24]:<24} | {j["url"][-60:]}')
