# import asyncio
# from crawl4ai import *

# async def main():
#     async with AsyncWebCrawler() as crawler:
#         result = await crawler.arun(
#             url="https://gartner.wd5.myworkdayjobs.com/EXT/job/Gurgaon/Data-Scientist--Classical-ML--NLP---LLM-GenAI-Agentic-AI-_110911/apply?source=JB-10120",
#         )
#         print(result.markdown)

# if __name__ == "__main__":
#     asyncio.run(main())
import os

from crawl4ai import AsyncWebCrawler

async def scrape_linkedin():
    # Session cookie comes from the environment — a literal here is an account credential
    # in the repo, and it stays valid long after the probe is forgotten.
    cookies = [
        {
            "name": "li_at",
            "value": os.environ["LI_AT"],
            "domain": ".www.linkedin.com",
            "path": "/"
        }
    ]

    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url="https://www.linkedin.com/in/jay-singh-ds/details/experience/",
            cookies=cookies,
            # Requires residential proxy to avoid account flagging
            proxy="http://user:pass@residential-proxy-ip:port"
        )
        print(result.markdown)