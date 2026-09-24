import subprocess
import json
import asyncio

# with open("job_links 2.json", "r") as f:
#     job_links = json.loads(f.read())
    
# print(type(job_links))

# async def run_job_appli(company, link):
    # prompt = f"@initiate_fill ; {link} ; signup with google wherever asked"
    
    # process = await asyncio.create_subprocess_exec(
    #     "claude",
    #     prompt,
    #     stdout=asyncio.subprocess.PIPE,
    #     stderr=asyncio.subprocess.PIPE
    # )

    # stdout, stderr = await process.communicate()
    # return {
    #     "company": company,
    #     "return_code": process.returncode,
    #     "stdout": stdout.decode(),
    #     "stderr": stderr.decode(),
    # }
    
    
    
# async def main():
    
#     tasks = [
#         run_job_appli(company, link)
#         for company, link in job_links.items()
#     ]
    
#     results = await asyncio.gather(*tasks)
#     return results

# asyncio.run(main())
subprocess.run(["powershell", "pwd"], shell=True, start_new_session=True)