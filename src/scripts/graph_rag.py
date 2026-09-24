import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
AUTH = ("neo4j", os.getenv("NEO4J_PASSWORD") or os.getenv("GRAPH_DB_PASSWORD") or "password@1234")
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Optional: use neo4j-graphrag if installed, else fallback to direct Gemini text2cypher
try:
    from neo4j_graphrag.llm import OpenAILLM  # type: ignore
    from neo4j_graphrag.generation import GraphRAG  # type: ignore
    from neo4j_graphrag.retrievers import text2cypher  # type: ignore
    HAS_GRAPH_RAG = True
except ImportError:
    HAS_GRAPH_RAG = False


def get_driver():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()
    return driver


def gemini_text2cypher_query(question: str) -> str:
    """Fallback when neo4j-graphrag not installed: Gemini generates Cypher, we run it."""
    from markdown_to_neo4j_gemini import _call_gemini  # reuse Gemini client

    schema_hint = """
    You are a Neo4j Cypher expert. Given the user question, write a single Cypher query.
    Nodes have label :Entity plus a specific label (e.g. :Document, :Section, :Technology) and properties id, name, description, source.
    Relationships are dynamic but upper-snake (e.g. :CONTAINS, :USES, :RELATED_TO).
    Return JSON only: {"cypher": "MATCH ... RETURN ..."}
    Question: """
    raw = _call_gemini(schema_hint + question)
    import json, re
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        data = json.loads(m.group(0))
        return data.get("cypher", "MATCH (n:Entity) RETURN n.name LIMIT 5")
    return "MATCH (n:Entity) RETURN n LIMIT 5"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query Neo4j graph via GraphRAG / Gemini text2cypher")
    parser.add_argument("--query", type=str, default=None, help="Natural language question")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    query_text = args.query or input("Enter your question: ").strip()
    if not query_text:
        raise SystemExit("No query provided.")

    driver = get_driver()
    print(f"[connected] {URI} / db={DATABASE}")

    if HAS_GRAPH_RAG and os.getenv("OPENAI_API_KEY"):
        print("[mode] neo4j-graphrag + OpenAI")
        retriever = text2cypher.Text2CypherRetriever(driver=driver, llm=OpenAILLM(model_name="gpt-4o-mini"))
        from neo4j_graphrag.llm import OpenAILLM as _LLM
        llm = _LLM(model_name="gpt-4o-mini")
        rag = GraphRAG(retriever=retriever, llm=llm)
        response = rag.search(query_text=query_text, retriever_config={"top_k": args.top_k})
        print(response.answer)
    else:
        # Gemini fallback
        print(f"[mode] Gemini text2cypher fallback (model={os.getenv('MODEL','gemini-2.0-flash')})")
        cypher = gemini_text2cypher_query(query_text)
        print(f"[cypher] {cypher}")
        with driver.session(database=DATABASE) as session:
            result = session.run(cypher)
            records = [r.data() for r in result]
            if not records:
                print("(no results)")
            else:
                for r in records[: args.top_k * 2]:
                    print(r)
                # Ask Gemini to synthesize an answer from records
                from markdown_to_neo4j_gemini import _call_gemini
                context = str(records[:20])[:4000]
                prompt = f"User question: {query_text}\nCypher results: {context}\nSynthesize a concise answer grounded in results. If empty, say so."
                answer = _call_gemini(prompt)
                print(f"\n[answer]\n{answer}")

    driver.close()


if __name__ == "__main__":
    main()