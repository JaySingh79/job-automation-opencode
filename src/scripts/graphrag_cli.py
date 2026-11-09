#!/usr/bin/env python3
"""Antigravity Python CLI wrapper for .opencode/tools/graphrag.ts + graphrag_query.py.

Queries the local Neo4j knowledge graph (bolt://localhost:7687) via
.opencode/tools/graphrag_query.py and falls back to the exact keyword-scored
markdown scan of ./ats when Neo4j is empty or unreachable.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

MAX_CHARS = 6000
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
GRAPHRAG_QUERY_SCRIPT = WORKSPACE_ROOT / ".opencode" / "tools" / "graphrag_query.py"

STOPWORDS = set(
    "a an the and or of for to in on at with how what when where which who whom whose "
    "is are was were be been do does did should would could can it its this that these "
    "those from by as into vs via per show list give find get all any our their his her "
    "my your tell about".split()
)


def _keywords(question: str, limit: int = 8) -> list[str]:
    out: list[str] = []
    tokens = re.findall(r"[a-z0-9][a-z0-9_\-.]*|[\u0900-\u097F]+", question.lower())
    for tok in tokens:
        if len(tok) < 3 or tok in STOPWORDS or tok in out:
            continue
        out.append(tok)
        if len(out) >= limit:
            break
    return out


def _walk_md(directory: Path) -> list[Path]:
    out: list[Path] = []
    try:
        entries = sorted(directory.iterdir(), key=lambda p: p.name)
    except Exception:
        return out
    for entry in entries:
        if entry.name.startswith(".") or entry.name == "node_modules":
            continue
        if entry.is_dir():
            out.extend(_walk_md(entry))
        elif entry.is_file() and entry.suffix.lower() in {".md", ".mdx"}:
            out.append(entry)
    return out


def _fallback_search(root: Path, question: str, top_k: int) -> str:
    ats_dir = root / "ats"
    if not ats_dir.is_dir():
        return "Fallback: no ./ats directory found. Nothing to search."
    keys = _keywords(question)
    if not keys:
        return "Fallback: no searchable keywords in query."

    hits: list[dict[str, object]] = []
    files = _walk_md(ats_dir)[:200]
    for file_path in files:
        try:
            if file_path.stat().st_size > 200_000:
                continue
            lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue

        rel_path = file_path.relative_to(root).as_posix()
        for idx, line in enumerate(lines, start=1):
            lower = line.lower()
            score = sum(1 for k in keys if k in lower)
            if score > 0:
                hits.append(
                    {
                        "file": rel_path,
                        "line": idx,
                        "text": line.strip()[:220],
                        "score": score,
                    }
                )

    hits.sort(key=lambda h: (-int(h["score"]), str(h["file"])))
    top = hits[: top_k * 3]
    if not top:
        return (
            f"Fallback (markdown scan of ./ats, keywords: {', '.join(keys)}): no matches. "
            "The graph may need ingest: `uv run python markdown_to_neo4j_gemini.py` "
            "equivalent cocoindex update over ./ats."
        )

    body = "\n".join(f"- {h['file']}:{h['line']} — {h['text']}" for h in top)
    return (
        f"Fallback (Neo4j empty/unreachable; markdown scan of ./ats, keywords: {', '.join(keys)}):\n"
        f"{body}\n\n"
        "Note: populate the graph by running the cocoindex ingest over ./ats, then re-query for relationship context."
    )


def _format_graph(data: dict) -> str:
    parts: list[str] = []
    entities = data.get("entities") or []
    triples = data.get("triples") or []
    documents = data.get("documents") or []

    if entities:
        parts.append(f"Matched entities: {'; '.join(str(e) for e in entities)}")
    if triples:
        rel_lines = [
            f"- {t.get('subject')} --[{t.get('predicate')}]--> {t.get('object')}"
            for t in triples
            if isinstance(t, dict)
        ]
        parts.append("Relationships:\n" + "\n".join(rel_lines))
    if documents:
        doc_lines = []
        for doc in documents:
            if not isinstance(doc, dict):
                continue
            line = f"- {doc.get('filename', '')}"
            if doc.get("title"):
                line += f" — {doc['title']}"
            if doc.get("summary"):
                line += f"\n  {str(doc['summary'])[:300]}"
            doc_lines.append(line)
        parts.append("Sources:\n" + "\n".join(doc_lines))
    return "\n\n".join(parts)


def query_graphrag(question: str, top_k: int = 5) -> str:
    top_k = max(1, min(20, top_k))
    if GRAPHRAG_QUERY_SCRIPT.is_file():
        try:
            proc = subprocess.run(
                [sys.executable, str(GRAPHRAG_QUERY_SCRIPT), question, str(top_k)],
                cwd=str(WORKSPACE_ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=15,
            )
            raw = proc.stdout or ""
            start = raw.find("{")
            if start >= 0:
                data = json.loads(raw[start:])
                if data.get("mode") == "graph":
                    no_hits = (
                        len(data.get("entities") or []) == 0
                        and len(data.get("triples") or []) == 0
                        and len(data.get("documents") or []) == 0
                    )
                    if not no_hits:
                        return _format_graph(data)[:MAX_CHARS]
                    return _fallback_search(WORKSPACE_ROOT, question, top_k)[:MAX_CHARS]
        except Exception:
            pass

    return _fallback_search(WORKSPACE_ROOT, question, top_k)[:MAX_CHARS]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query the repo Neo4j GraphRAG or ./ats markdown fallback."
    )
    parser.add_argument("query", help="Natural-language query (e.g. 'Workday searchable prompt')")
    parser.add_argument(
        "top_k",
        nargs="?",
        type=int,
        default=5,
        help="Max entities/documents per hop (1-20, default: 5)",
    )
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    print(query_graphrag(args.query, args.top_k))


if __name__ == "__main__":
    main()
