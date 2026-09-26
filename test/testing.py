# import asyncio
# from claude_agent_sdk import query, ClaudeAgentOptions


# async def main():
#     options = ClaudeAgentOptions()
#     async for message in query(
#         prompt="List the files in this directory", options=options
#     ):
#         print(message)


# asyncio.run(main())


import json
import serpapi
from dotenv import load_dotenv
load_dotenv()

client = serpapi.Client()

all_results = []
for start in range(0, 50, 10):  # Results 1–50
    
    results = client.search(
        {
            "engine": "google",
            "q": "(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com) ('Machine Learning' OR 'AI' OR 'ML')",
            "google_domain": "google.com",
            "hl": "en",
            "gl": "us",
            "start": start,
        }
    )

    all_results.append(results)
    
traversable = []
responses = [{"title": item['title'], "link": item['link'], "snippet": item['snippet']} for item[] in all_results]
res = {
    "response": responses
}

with open("rtest.json", 'w', encoding="utf-8") as f:
    json.dump(res, f, indent=2)


print(responses)