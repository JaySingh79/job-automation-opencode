import asyncio
from crawl4ai import *

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://gartner.wd5.myworkdayjobs.com/EXT/job/Gurgaon/Data-Scientist--Classical-ML--NLP---LLM-GenAI-Agentic-AI-_110911/apply?source=JB-10120",
        )
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())
