"""Read-only GraphRAG retriever for the opencode `graphrag` tool.

Queries the Neo4j knowledge graph built by `markdown_to_neo4j_gemini.py`
(cocoindex ingest over ./ats) against the REAL schema:

    (:Document {filename, title, summary})
    (:Entity {value})
    (:Entity)-[:RELATIONSHIP {id, predicate}]->(:Entity)
    (:Document)-[:MENTION]->(:Entity)

No LLM, no writes, no side effects. All parameters are bound ($param),
never interpolated, so natural-language input cannot inject Cypher.
Prints one JSON object to stdout; exit 0 on success (even with zero hits),
exit 2 when Neo4j is unreachable so the caller can fall back to markdown.

Usage (repo root, per AGENTS.md `uv` rule):
    uv run python .opencode/tools/graphrag_query.py "<question>" [top_k]
"""

import json
import os
import re
import sys

STOPWORDS = frozenset(
    "a an the and or of for to in on at with how what when where which who "
    "whom whose is are was were be been do does did should would could can "
    "it its this that these those from by as into vs via per show list give "
    "find get all any our their his her my your tell about".split()
)


def keywords(question: str, limit: int = 8) -> list[str]:
    tokens = re.findall(r"[a-z0-9][a-z0-9_\-\.]*", question.lower())
    seen: list[str] = []
    for t in tokens:
        if len(t) < 3 or t in STOPWORDS or t in seen:
            continue
        seen.append(t)
        if len(seen) >= limit:
            break
    return seen


def main() -> int:
    question = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        top_k = max(1, min(int(sys.argv[2]) if len(sys.argv) > 2 else 5, 20))
    except ValueError:
        top_k = 5
    if not question.strip():
        print(json.dumps({"mode": "error", "error": "empty query"}))
        return 1

    try:
        from neo4j import GraphDatabase
    except ImportError as exc:
        print(json.dumps({"mode": "unavailable", "error": f"neo4j driver missing: {exc}"}))
        return 2

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD") or os.getenv("GRAPH_DB_PASSWORD") or ""
    database = os.getenv("NEO4J_DATABASE", "neo4j")

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
    except Exception as exc:
        print(json.dumps({"mode": "unavailable", "error": f"neo4j unreachable: {exc}"}))
        return 2

    keys = keywords(question)
    out: dict = {"mode": "graph", "keywords": keys, "entities": [], "triples": [], "documents": []}
    try:
        with driver.session(database=database) as session:
            ent_rows = session.run(
                "MATCH (e:Entity) "
                "WHERE any(k IN $keys WHERE toLower(e.value) CONTAINS k) "
                "RETURN e.value AS value LIMIT $lim",
                keys=keys,
                lim=top_k * 3,
            ).data()
            out["entities"] = [r["value"] for r in ent_rows]
            if out["entities"]:
                out["triples"] = session.run(
                    "MATCH (a:Entity)-[r:RELATIONSHIP]->(b:Entity) "
                    "WHERE a.value IN $vals OR b.value IN $vals "
                    "RETURN a.value AS subject, r.predicate AS predicate, "
                    "b.value AS object LIMIT $lim",
                    vals=out["entities"],
                    lim=top_k * 4,
                ).data()
                out["documents"] = session.run(
                    "MATCH (d:Document)-[:MENTION]->(e:Entity) "
                    "WHERE e.value IN $vals "
                    "RETURN DISTINCT d.filename AS filename, d.title AS title, "
                    "d.summary AS summary LIMIT $lim",
                    vals=out["entities"],
                    lim=top_k * 2,
                ).data()
            if not out["documents"]:
                out["documents"] = session.run(
                    "MATCH (d:Document) "
                    "WHERE any(k IN $keys WHERE "
                    "toLower(coalesce(d.title, '')) CONTAINS k "
                    "OR toLower(coalesce(d.summary, '')) CONTAINS k "
                    "OR toLower(d.filename) CONTAINS k) "
                    "RETURN d.filename AS filename, d.title AS title, "
                    "d.summary AS summary LIMIT $lim",
                    keys=keys,
                    lim=top_k * 2,
                ).data()
    except Exception as exc:
        print(json.dumps({"mode": "unavailable", "error": f"cypher failed: {exc}"}))
        return 2
    finally:
        driver.close()

    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
