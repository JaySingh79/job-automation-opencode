"""
discover_greenhouse_orgs.py — Probe potential tech companies on Greenhouse API.
"""
import urllib.request
import urllib.error
import json
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0"}

CANDIDATES = [
    # Top tech startups / companies often using Greenhouse:
    "postman", "clevertap", "hackerrank", "browserstack", "hasura", "inmobi",
    "swiggy", "meesho", "urbancompany", "zerodha", "cred", "zepto", "groww",
    "stripe", "figma", "canva", "gitlab", "cloudflare", "mongodb", "elastic",
    "scaleai", "cohere", "anthropic", "weightsbiases", "wandb", "langchain",
    "llamaindex", "huggingface", "vercel", "supabase", "modal", "replicate",
    "perplexity", "togetherai", "anyscale", "runway", "characterai", "glean",
    "adept", "inflection", "cohereai", "databricks", "rubrik", "snowflake",
    "couchbase", "confluent", "dbtlabs", "astronomer", "prefect", "airbyte",
    "census", "fivetran", "hevo", "clickhouse", "starrocks", "pinecone",
    "weaviate", "qdrant", "milvus", "chroma", "neo4j", "redis",
    "sentry", "datadog", "newrelic", "dynatrace", "honeycomb",
    "launchdarkly", "pagerduty", "hashicorp", "pulumi", "temporal",
    "argo", "snyk", "wiz", "lacework", "orca", "cyera", "abnormal",
    "gusto", "deel", "remote", "rippling", "oyster", "lattice",
    "carta", "brex", "ramp", "mercury", "plaid", "checkr",
    "affirm", "klarna", "chime", "monzo", "revolut", "n26",
    "robinhood", "coinbase", "kraken", "gemini", "chainalysis", "fireblocks"
]

def check_org(org):
    url = f"https://boards-api.greenhouse.io/v1/boards/{org}/jobs"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=5, context=CTX) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
            jobs = data.get("jobs", [])
            if jobs:
                return org, len(jobs)
    except Exception:
        pass
    return None

def main():
    print(f"Probing {len(CANDIDATES)} candidate Greenhouse orgs...")
    valid = {}
    with ThreadPoolExecutor(max_workers=25) as ex:
        futs = {ex.submit(check_org, o): o for o in CANDIDATES}
        for f in as_completed(futs):
            res = f.result()
            if res:
                org, count = res
                valid[org] = count
                print(f"  [FOUND] {org}: {count} jobs")

    print(f"\nDiscovered {len(valid)} active Greenhouse boards:")
    print(sorted(valid.keys()))

if __name__ == "__main__":
    main()
