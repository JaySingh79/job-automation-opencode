# import asyncio
# from claude_agent_sdk import query, ClaudeAgentOptions


# async def main():
#     options = ClaudeAgentOptions()
#     async for message in query(
#         prompt="List the files in this directory", options=options
#     ):
#         print(message)


# asyncio.run(main())


# import json
# import serpapi
# from dotenv import load_dotenv
# load_dotenv()

# client = serpapi.Client()

# all_results = []
# for start in range(0, 50, 10):  # Results 1–50
    
#     results = client.search(
#         {
#             "engine": "google",
#             "q": "(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com) ('Machine Learning' OR 'AI' OR 'ML')",
#             "google_domain": "google.com",
#             "hl": "en",
#             "gl": "us",
#             "start": start,
#         }
#     )

#     all_results.append(results)
    
# traversable = []
# responses = [{"title": item['title'], "link": item['link'], "snippet": item['snippet']} for item[] in all_results]
# res = {
#     "response": responses
# }

# with open("rtest.json", 'w', encoding="utf-8") as f:
#     json.dump(res, f, indent=2)


# print(responses)

"""Test loader: roadmap MD -> Neo4j knowledge graph.

Graph schema (test-only):
  (d:Document {source, title})-[:HAS_SECTION]->(s:Section {num, title})
  (s)-[:HAS_CHUNK]->(c:Chunk {type, text, ord})
  (s)-[:ABOUT_PLATFORM]->(p:Platform {name})
  (p:Platform)-[:HAS_PAGE]->(pg:Page {path})
  (c)-[:MENTIONS_PLATFORM]->(p)
  (c)-[:MENTIONS_PAGE]->(pg)
  (c)-[:MENTIONS_CONCEPT]->(k:Concept {name})
  (c1:Chunk {type:'loop_step'})-[:NEXT_STEP]->(c2:Chunk)  # ordered §4 steps

Run: .venv\\Scripts\\python.exe test/testing.py
"""
from __future__ import annotations

import re
from pathlib import Path

from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password@1234")
MD_PATH = (
    Path(__file__).resolve().parent.parent
    / "src" / "knowledge_source"
    / "job-application-roadmap_wellfound_instahyre.md"
)
DOC_SOURCE = "job-application-roadmap_wellfound_instahyre.md"

SECTION_RE = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$")
BULLET_RE = re.compile(r"^-\s+(.*)")
NUMBERED_RE = re.compile(r"^(\d+)\.\s+(.*)")
CHECK_RE = re.compile(r"^-\s+\[\s\]\s+(.*)")
BACKTICK_RE = re.compile(r"`([^`]+)`")
PATH_RE = re.compile(r"`?((?:https?://[^\s`]+)|/(?:candidate|jobs|search|login)[^\s`]*)`?")


def parse_markdown(text: str):
    lines = text.splitlines()
    title = next((l.lstrip("# ").strip() for l in lines if l.startswith("# ")), DOC_SOURCE)
    sections: list[dict] = []
    current = None
    last_chunk = None
    blank = True  # paragraph boundary tracker

    for line in lines:
        m_sec = SECTION_RE.match(line.strip())
        if m_sec:
            current = {"num": int(m_sec.group(1)), "title": m_sec.group(2), "chunks": []}
            sections.append(current)
            last_chunk = None
            blank = True
            continue
        if current is None:
            continue  # skip preamble before §0
        s = line.strip()
        if not s:
            blank = True
            continue
        m_check = CHECK_RE.match(s)
        m_num = NUMBERED_RE.match(s)
        m_bul = BULLET_RE.match(s)
        if m_check:
            last_chunk = {"kind": "checklist", "text": m_check.group(1).strip()}
            current["chunks"].append(last_chunk)
        elif m_num and current["num"] == 4:
            # §4 token-cheap loop steps are ordered
            last_chunk = {"kind": "step", "text": m_num.group(2).strip(), "ord": int(m_num.group(1))}
            current["chunks"].append(last_chunk)
        elif m_bul:
            last_chunk = {"kind": "bullet", "text": m_bul.group(1).strip()}
            current["chunks"].append(last_chunk)
        elif m_num:
            last_chunk = {"kind": "bullet", "text": m_num.group(2).strip()}
            current["chunks"].append(last_chunk)
        elif blank or last_chunk is None:
            # Prose paragraph (§3 relevance filter has no bullet markers)
            last_chunk = {"kind": "prose", "text": s}
            current["chunks"].append(last_chunk)
        else:
            last_chunk["text"] += " " + s  # wrapped-line continuation
        blank = False

    # Split long prose paragraphs into sentence chunks so each fact
    # classifies/links independently (e.g. §3 apply vs skip sentences).
    # Fragments <25 chars (e.g. "Rs.") are merged forward.
    for sec in sections:
        expanded = []
        for ch in sec["chunks"]:
            if ch["kind"] == "prose":
                parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\(\"'])", ch["text"])
                buf = ""
                for part in parts:
                    buf = (buf + " " + part).strip() if buf else part.strip()
                    if len(buf) >= 25:
                        expanded.append({"kind": "prose", "text": buf})
                        buf = ""
                if buf:
                    if expanded:
                        expanded[-1]["text"] += " " + buf
                    else:
                        expanded.append({"kind": "prose", "text": buf})
            else:
                expanded.append(ch)
        sec["chunks"] = expanded
    return title, sections


def classify_chunk(sec_num: int, kind: str, text: str) -> str:
    t = text.upper()
    if kind == "checklist":
        return "checklist_item"
    if kind == "step":
        return "loop_step"
    if sec_num == 0:
        return "constraint" if t.startswith("NEVER") else "standing_rule"
    if sec_num in (1, 2):
        return "platform_fact"
    if sec_num == 3:
        if t.startswith("APPLY WHEN"):
            return "apply_condition"
        if "SKIP" in t or "SENIOR" in t or "SALARY" in t or "MISMATCH" in t:
            return "skip_reason"
        return "filter_fact"
    if sec_num == 5:
        return "antipattern"
    return "fact"


def detect_platforms(sec_title: str, text: str) -> list[str]:
    blob = f"{sec_title} {text}".lower()
    out = []
    if "instahyre" in blob:
        out.append("Instahyre")
    if "wellfound" in blob:
        out.append("Wellfound")
    return out


def detect_pages(text: str) -> list[str]:
    pages = []
    for m in PATH_RE.finditer(text):
        raw = m.group(1)
        # normalize full URLs to path
        path = re.sub(r"^https?://[^/]+", "", raw).split("?")[0]
        if path and len(path) > 1:
            pages.append(path.rstrip("/") or "/")
    return sorted(set(pages))


def detect_concepts(text: str) -> list[str]:
    concepts = []
    for m in BACKTICK_RE.finditer(text):
        term = m.group(1).strip()
        if term.startswith("/") or term.startswith("http") or len(term) > 60:
            continue  # paths/URLs go to Page nodes, not Concept
        concepts.append(term)
    return sorted(set(concepts))


def load_graph(title: str, sections: list[dict]) -> dict:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()

    # Build serializable payload in Python (classification + entity extraction)
    payload = []
    for sec in sections:
        chunks = []
        for i, ch in enumerate(sec["chunks"]):
            ctype = classify_chunk(sec["num"], ch["kind"], ch["text"])
            chunks.append({
                "ord": ch.get("ord", i),
                "type": ctype,
                "text": ch["text"][:2000],
                "platforms": detect_platforms(sec["title"], ch["text"]),
                "pages": detect_pages(ch["text"]),
                "concepts": detect_concepts(ch["text"]),
            })
        payload.append({"num": sec["num"], "title": sec["title"], "chunks": chunks})

    with driver.session() as session:
        # Idempotent reload of this document (+ its sections/chunks only;
        # Platform/Page/Concept nodes are shared and must survive)
        session.run(
            """
            MATCH (d:Document {source: $src})
            OPTIONAL MATCH (d)-[:HAS_SECTION]->(s:Section)-[:HAS_CHUNK]->(c:Chunk)
            DETACH DELETE d, s, c
            """.strip(),
            src=DOC_SOURCE,
        )
        session.run(
            """
            MATCH (s:Section) WHERE NOT (s)<-[:HAS_SECTION]-(:Document)
            DETACH DELETE s
            """.strip()
        )
        session.run(
            """
            MATCH (c:Chunk) WHERE NOT ()-[:HAS_CHUNK]->(c)
            DETACH DELETE c
            """.strip()
        )
        session.run(
            """
            MERGE (:Platform {name: 'Instahyre'})
            MERGE (:Platform {name: 'Wellfound'})
            """.strip()
        )
        session.run(
            """
            CREATE (d:Document {source: $src, title: $title})
            WITH d
            UNWIND $sections AS sec
            CREATE (s:Section {num: sec.num, title: sec.title})
            CREATE (d)-[:HAS_SECTION]->(s)
            WITH s, sec
            UNWIND sec.chunks AS ch
            CREATE (c:Chunk {type: ch.type, text: ch.text, ord: ch.ord,
                             section_num: s.num, doc_source: $src})
            CREATE (s)-[:HAS_CHUNK]->(c)
            """.strip(),
            src=DOC_SOURCE, title=title, sections=payload,
        )
        # Mentions pass: match chunks back via (doc_source, section_num, ord)
        session.run(
            """
            UNWIND $sections AS sec
            UNWIND sec.chunks AS ch
            MATCH (c:Chunk {doc_source: $src, section_num: sec.num, ord: ch.ord})
            MATCH (s:Section {num: sec.num})<-[:HAS_SECTION]-(:Document {source: $src})
            WITH c, s, ch
            UNWIND ch.platforms AS pname
            MATCH (p:Platform {name: pname})
            MERGE (c)-[:MENTIONS_PLATFORM]->(p)
            MERGE (s)-[:ABOUT_PLATFORM]->(p)
            """.strip(),
            src=DOC_SOURCE, sections=payload,
        )
        session.run(
            """
            UNWIND $sections AS sec
            UNWIND sec.chunks AS ch
            UNWIND ch.pages AS ppath
            WITH sec, ch, ppath
            MATCH (c:Chunk {doc_source: $src, section_num: sec.num, ord: ch.ord})
            MERGE (pg:Page {path: ppath})
            MERGE (c)-[:MENTIONS_PAGE]->(pg)
            WITH c, pg
            MATCH (c)-[:MENTIONS_PLATFORM]->(p:Platform)
            MERGE (p)-[:HAS_PAGE]->(pg)
            """.strip(),
            src=DOC_SOURCE, sections=payload,
        )
        session.run(
            """
            UNWIND $sections AS sec
            UNWIND sec.chunks AS ch
            UNWIND ch.concepts AS cname
            WITH sec, ch, cname
            MATCH (c:Chunk {doc_source: $src, section_num: sec.num, ord: ch.ord})
            MERGE (k:Concept {name: cname})
            MERGE (c)-[:MENTIONS_CONCEPT]->(k)
            """.strip(),
            src=DOC_SOURCE, sections=payload,
        )
        # Link §4 loop steps in order + attach pages to their platform
        session.run(
            """
            MATCH (c:Chunk {doc_source: $src, type: 'loop_step'})
            WITH c ORDER BY c.ord
            WITH collect(c) AS steps
            UNWIND range(0, size(steps)-2) AS i
            WITH steps[i] AS a, steps[i+1] AS b
            MERGE (a)-[:NEXT_STEP]->(b)
            """.strip(),
            src=DOC_SOURCE,
        )
        session.run(
            """
            MATCH (c:Chunk {doc_source: $src})-[:MENTIONS_PAGE]->(pg:Page)
            MATCH (c)-[:MENTIONS_PLATFORM]->(p:Platform)
            MERGE (p)-[:HAS_PAGE]->(pg)
            """.strip(),
            src=DOC_SOURCE,
        )
        stats = session.run(
            """
            MATCH (d:Document {source: $src})-[:HAS_SECTION]->(s:Section)
            OPTIONAL MATCH (s)-[:HAS_CHUNK]->(c:Chunk)
            RETURN count(DISTINCT s) AS sections, count(DISTINCT c) AS chunks
            """.strip(),
            src=DOC_SOURCE,
        ).single()
        extra = session.run(
            """
            MATCH (p:Platform) RETURN count(*) AS platforms
            """.strip()
        ).single()
        pages = session.run("MATCH (pg:Page) RETURN count(*) AS n").single()
        concepts = session.run("MATCH (k:Concept) RETURN count(*) AS n").single()
        rels = session.run("MATCH ()-[r]->() RETURN count(*) AS n").single()
        dist = session.run(
            """
            MATCH (c:Chunk {doc_source: $src})
            RETURN c.type AS t, count(*) AS n ORDER BY n DESC
            """.strip(),
            src=DOC_SOURCE,
        ).data()
        chain = session.run(
            """
            MATCH (:Chunk {doc_source: $src, type: 'loop_step'})-[r:NEXT_STEP]->()
            RETURN count(r) AS links
            """.strip(),
            src=DOC_SOURCE,
        ).single()
        plats = session.run(
            """
            MATCH (s:Section)<-[:HAS_SECTION]-(:Document {source: $src})
            OPTIONAL MATCH (s)-[:ABOUT_PLATFORM]->(p:Platform)
            RETURN s.num AS sec, collect(p.name) AS platforms ORDER BY sec
            """.strip(),
            src=DOC_SOURCE,
        ).data()
    driver.close()
    return {
        "sections": stats["sections"],
        "chunks": stats["chunks"],
        "platforms": extra["platforms"],
        "pages": pages["n"],
        "concepts": concepts["n"],
        "relationships": rels["n"],
        "chunk_types": {r["t"]: r["n"] for r in dist},
        "loop_step_links": chain["links"],
        "section_platforms": {r["sec"]: r["platforms"] for r in plats},
    }


def main() -> None:
    assert MD_PATH.exists(), f"Markdown not found: {MD_PATH}"
    title, sections = parse_markdown(MD_PATH.read_text(encoding="utf-8"))
    print(f"Parsed: {title!r} -> {len(sections)} sections, "
          f"{sum(len(s['chunks']) for s in sections)} chunks")
    summary = load_graph(title, sections)
    print("Loaded into Neo4j:", summary)
    assert summary["sections"] >= 7, "expected §0-§6 (7 sections)"
    assert summary["chunks"] > 30, "expected 30+ chunks from bullets/steps"
    assert "apply_condition" in summary["chunk_types"], "§3 prose lost: no apply_condition chunk"
    assert "skip_reason" in summary["chunk_types"], "§3 prose lost: no skip_reason chunk"
    assert summary["loop_step_links"] == 4, "§4 should chain 5 steps with 4 NEXT_STEP links"
    print("TEST PASS: roadmap graph stored.")


if __name__ == "__main__":
    main()