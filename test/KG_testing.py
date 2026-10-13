"""LLM knowledge-graph extraction: roadmap MD -> Neo4j via Google GenAI.

Pipeline: split MD into ## sections -> one grounded `generate_content` call per
section with a strict JSON schema -> validate labels/relations against
allowlists -> MERGE into Neo4j under LLMDocument/LLMSection/LLMEntity nodes
(kept separate from the deterministic graph in test/testing.py).

Auth: GEMINI_API_KEY (or GOOGLE_API_KEY) from environment / .env.
Run: .venv\\Scripts\\python.exe test/KG_testing.py
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # minimal .env fallback
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("\"'"))

from google import genai
from google.genai import types
from neo4j import GraphDatabase

MD_PATH = (
    Path(__file__).resolve().parent.parent
    / "src" / "knowledge_source"
    / "job-application-roadmap_wellfound_instahyre.md"
)
DOC_SOURCE = "job-application-roadmap_wellfound_instahyre.md"
MODEL = os.getenv("MODEL") or os.getenv("llm_model") or "gemini-2.0-flash"

NEO4J_URI = os.getenv("NEO4J_URI") or "bolt://localhost:7687"
NEO4J_USER = os.getenv("NEO4J_USER") or "neo4j"
NEO4J_PASSWORD = os.getenv("GRAPH_DB_PASSWORD") or "password@1234"

# Closed vocabularies: everything the model returns must fit these,
# which also makes dynamic labels / rel-types injection-safe in Cypher.
ENTITY_LABELS = {
    "Platform", "Page", "Rule", "Constraint", "FilterCondition",
    "SkipReason", "Step", "AntiPattern", "ChecklistItem", "Concept", "FileRef",
}
RELATIONS = {
    "HAS_PAGE", "STATES", "REQUIRES", "BLOCKED_BY", "ALLOWS",
    "APPLIES_WHEN", "SKIPS_WHEN", "NEXT_STEP", "MENTIONS",
    "USES_FILE", "VERIFIED_BY",
}

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "label": {"type": "string", "enum": sorted(ENTITY_LABELS)},
                    "detail": {"type": "string"},
                },
                "required": ["name", "label"],
            },
        },
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "relation": {"type": "string", "enum": sorted(RELATIONS)},
                },
                "required": ["source", "target", "relation"],
            },
        },
    },
    "required": ["entities", "relationships"],
}

SYSTEM_PROMPT = (
    "You extract a knowledge graph from a job-application playbook. "
    "Return ONLY entities and relationships stated in or directly implied by "
    "the given section text. NEVER invent profile facts, URLs, numbers, or "
    "entities not present in the text. Keep names short and canonical "
    "(e.g. platform 'Wellfound', page '/jobs', file 'jobs_applied.json'). "
    "Label guide: Platform/ Page (a site route); Rule (general practice); "
    "Constraint (NEVER / must-not rule); FilterCondition (when to apply); "
    "SkipReason (named skip cause like SENIOR_TITLE); Step (ordered action); "
    "AntiPattern (wasted action to avoid); ChecklistItem (do-not-repeat item); "
    "Concept (tool/term); FileRef (a JSON/MD ledger or authority file)."
)


def split_sections(text: str) -> list[dict]:
    sections, current = [], None
    for line in text.splitlines():
        m = re.match(r"^##\s+(\d+)\.\s+(.+?)\s*$", line.strip())
        if m:
            current = {"num": int(m.group(1)), "title": m.group(2), "lines": []}
            sections.append(current)
        elif current is not None:
            current["lines"].append(line)
    return [
        {"num": s["num"], "title": s["title"], "text": "\n".join(s["lines"]).strip()}
        for s in sections
        if "\n".join(s["lines"]).strip()
    ]


def extract_section(client: genai.Client, section: dict) -> dict:
    resp = client.models.generate_content(
        model=MODEL,
        contents=f"## {section['num']}. {section['title']}\n\n{section['text']}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=EXTRACTION_SCHEMA,
            temperature=0.0,
        ),
    )
    data = json.loads(resp.text)
    # Defensive: drop anything outside the closed vocabularies.
    entities = [
        e for e in data.get("entities", [])
        if e.get("label") in ENTITY_LABELS and e.get("name")
    ]
    names = {e["name"] for e in entities}
    relationships = [
        r for r in data.get("relationships", [])
        if r.get("relation") in RELATIONS
        and r.get("source") in names and r.get("target") in names
    ]
    return {"entities": entities, "relationships": relationships}


def load_graph(sections: list[dict], extractions: list[dict]) -> dict:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
    with driver.session() as session:
        session.run(
            "MATCH (d:LLMDocument {source: $src}) "
            "OPTIONAL MATCH (d)-[:HAS_SECTION]->(s:LLMSection) "
            "OPTIONAL MATCH (s)-[:CONTAINS_FACT]->(e:LLMEntity) "
            "DETACH DELETE d, s, e",
            src=DOC_SOURCE,
        )
        session.run(
            "CREATE (d:LLMDocument {source: $src, method: 'google-genai'})",
            src=DOC_SOURCE,
        )
        for sec, ext in zip(sections, extractions):
            session.run(
                """
                MATCH (d:LLMDocument {source: $src})
                CREATE (s:LLMSection {doc_source: $src, num: $num, title: $title})
                CREATE (d)-[:HAS_SECTION]->(s)
                """.strip(),
                src=DOC_SOURCE, num=sec["num"], title=sec["title"],
            )
            for e in ext["entities"]:
                session.run(
                    f"""
                    MATCH (s:LLMSection {{doc_source: $src, num: $num}})
                    MERGE (e:LLMEntity:{e['label']} {{doc_source: $src, name: $name}})
                    SET e.detail = $detail
                    MERGE (s)-[:CONTAINS_FACT]->(e)
                    """.strip(),
                    src=DOC_SOURCE, num=sec["num"],
                    name=e["name"], detail=e.get("detail", ""),
                )
            for r in ext["relationships"]:
                session.run(
                    f"""
                    MATCH (a:LLMEntity {{doc_source: $src, name: $a}})
                    MATCH (b:LLMEntity {{doc_source: $src, name: $b}})
                    MERGE (a)-[:{r['relation']}]->(b)
                    """.strip(),
                    src=DOC_SOURCE, a=r["source"], b=r["target"],
                )
        stats = session.run(
            """
            MATCH (d:LLMDocument {source: $src})-[:HAS_SECTION]->(s:LLMSection)
            OPTIONAL MATCH (s)-[:CONTAINS_FACT]->(e:LLMEntity)
            OPTIONAL MATCH (e)-[r]->(:LLMEntity)
            RETURN count(DISTINCT s) AS sections,
                   count(DISTINCT e) AS entities,
                   count(DISTINCT r) AS relations
            """.strip(),
            src=DOC_SOURCE,
        ).single()
    driver.close()
    return dict(stats)


def main() -> None:
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        raise SystemExit("Missing GEMINI_API_KEY (or GOOGLE_API_KEY) in env/.env")
    assert MD_PATH.exists(), f"Markdown not found: {MD_PATH}"
    sections = split_sections(MD_PATH.read_text(encoding="utf-8"))
    print(f"Sections: {len(sections)} | model: {MODEL}")
    assert len(sections) >= 7, "expected §0-§6"

    client = genai.Client()  # picks up GEMINI_API_KEY / GOOGLE_API_KEY
    extractions = []
    for sec in sections:
        ext = extract_section(client, sec)
        extractions.append(ext)
        print(f"§{sec['num']} {sec['title']}: "
              f"{len(ext['entities'])} entities, {len(ext['relationships'])} rels")

    summary = load_graph(sections, extractions)
    print("Loaded into Neo4j:", summary)
    assert summary["sections"] >= 7
    assert summary["entities"] > 20, "expected a non-trivial entity set"
    print("TEST PASS: LLM knowledge graph stored.")


if __name__ == "__main__":
    main()