# AI/ML/Data Science Job Dorking — ATS Platform Playbook

## 1. Objective

Use search-engine dorking to discover AI/ML/Data Science jobs across major ATS/job platforms.

Core structure:

```text
PLATFORM FINGERPRINT
        +
ROLE / SKILL TERMS
        +
OPTIONAL LOCATION / FRESHNESS / EXPERIENCE
```

No single dork finds every job because some platforms expose jobs on shared domains, some use company subdomains, and some are proxied through the employer's own careers domain.

---

# 2. AI/ML/Data Keyword Bank

## Role/title terms

```text
"machine learning engineer"
"ML engineer"
"AI engineer"
"AI/ML engineer"
"artificial intelligence engineer"
"machine learning developer"
"AI developer"
"data scientist"
"data science"
"data engineer"
"deep learning engineer"
"computer vision engineer"
"NLP engineer"
"natural language processing"
"applied scientist"
"research scientist"
"research engineer"
"ML researcher"
"MLOps engineer"
"ML platform engineer"
"AI platform engineer"
"AI software engineer"
"generative AI engineer"
"GenAI engineer"
"LLM engineer"
"LLM developer"
```

## Technology terms

```text
"machine learning"
"deep learning"
"artificial intelligence"
"generative AI"
"large language model"
LLM
RAG
"retrieval augmented generation"
NLP
"natural language processing"
"computer vision"
PyTorch
TensorFlow
"scikit-learn"
XGBoost
MLflow
"neural networks"
"recommendation systems"
"MLOps"
"model deployment"
"model serving"
"feature engineering"
"reinforcement learning"
Transformers
HuggingFace
```

---

# 3. Greenhouse

Typical patterns:

```text
boards.greenhouse.io/<company>
job-boards.greenhouse.io/<company>
```

### Dorks

```text
site:boards.greenhouse.io "machine learning"
```

```text
site:job-boards.greenhouse.io "machine learning"
```

```text
site:boards.greenhouse.io ("AI engineer" OR "ML engineer" OR "machine learning engineer")
```

```text
site:job-boards.greenhouse.io ("data scientist" OR "data science")
```

```text
site:boards.greenhouse.io ("generative AI" OR "LLM" OR "RAG")
```

```text
site:boards.greenhouse.io ("computer vision" OR NLP OR "deep learning")
```

### Maximum recall

```text
(site:boards.greenhouse.io OR site:job-boards.greenhouse.io)
("machine learning" OR "artificial intelligence" OR
"data scientist" OR "data engineer" OR
"AI engineer" OR "deep learning" OR
"NLP" OR "computer vision" OR
"generative AI" OR LLM OR MLOps)
```

---

# 4. Lever

Pattern:

```text
jobs.lever.co/<company>
```

### Dorks

```text
site:jobs.lever.co "machine learning"
```

```text
site:jobs.lever.co ("AI engineer" OR "ML engineer")
```

```text
site:jobs.lever.co ("data scientist" OR "data engineer")
```

```text
site:jobs.lever.co ("generative AI" OR LLM OR RAG)
```

```text
site:jobs.lever.co ("computer vision" OR NLP OR "deep learning")
```

### Maximum recall

```text
site:jobs.lever.co
("machine learning" OR "artificial intelligence" OR
"data science" OR "data scientist" OR
"AI engineer" OR "data engineer" OR
"deep learning" OR NLP OR
"computer vision" OR "generative AI" OR LLM OR MLOps)
```

---

# 5. Ashby

Pattern:

```text
jobs.ashbyhq.com/<company>
```

### Dorks

```text
site:jobs.ashbyhq.com "machine learning"
```

```text
site:jobs.ashbyhq.com ("AI engineer" OR "ML engineer")
```

```text
site:jobs.ashbyhq.com ("data scientist" OR "data engineer")
```

```text
site:jobs.ashbyhq.com ("generative AI" OR LLM OR RAG)
```

```text
site:jobs.ashbyhq.com ("deep learning" OR "computer vision" OR NLP)
```

### Maximum recall

```text
site:jobs.ashbyhq.com
("machine learning" OR "artificial intelligence" OR
"data scientist" OR "data engineer" OR
"AI engineer" OR "deep learning" OR
NLP OR "computer vision" OR
"generative AI" OR LLM OR MLOps)
```

---

# 6. Workday

Common patterns:

```text
<tenant>.wd1.myworkdayjobs.com
<tenant>.wd2.myworkdayjobs.com
<tenant>.wd3.myworkdayjobs.com
<tenant>.wd5.myworkdayjobs.com
<tenant>.wd10.myworkdayjobs.com
<tenant>.wd12.myworkdayjobs.com
```

### Dorks

```text
site:myworkdayjobs.com "machine learning"
```

```text
site:myworkdayjobs.com "artificial intelligence"
```

```text
site:myworkdayjobs.com "AI engineer"
```

```text
site:myworkdayjobs.com "machine learning engineer"
```

```text
site:myworkdayjobs.com "data scientist"
```

```text
site:myworkdayjobs.com "data engineer"
```

```text
site:myworkdayjobs.com ("generative AI" OR LLM OR RAG)
```

```text
site:myworkdayjobs.com ("computer vision" OR NLP OR "deep learning")
```

### Maximum recall

```text
site:myworkdayjobs.com
("machine learning" OR "artificial intelligence" OR
"data scientist" OR "data science" OR
"data engineer" OR "AI engineer" OR
"deep learning" OR NLP OR
"computer vision" OR "generative AI" OR LLM OR MLOps)
```

---

# 7. SmartRecruiters

Patterns:

```text
jobs.smartrecruiters.com/<company>
careers.smartrecruiters.com/<company>
```

### Dorks

```text
site:jobs.smartrecruiters.com "machine learning"
```

```text
site:jobs.smartrecruiters.com ("AI engineer" OR "ML engineer")
```

```text
site:jobs.smartrecruiters.com ("data scientist" OR "data engineer")
```

```text
site:jobs.smartrecruiters.com ("generative AI" OR LLM OR RAG)
```

```text
site:jobs.smartrecruiters.com ("computer vision" OR NLP OR "deep learning")
```

```text
site:careers.smartrecruiters.com "machine learning"
```

---

# 8. Workable

Pattern:

```text
apply.workable.com/<company>
```

### Dorks

```text
site:apply.workable.com "machine learning"
```

```text
site:apply.workable.com ("AI engineer" OR "ML engineer")
```

```text
site:apply.workable.com ("data scientist" OR "data engineer")
```

```text
site:apply.workable.com ("generative AI" OR LLM OR RAG)
```

```text
site:apply.workable.com ("computer vision" OR NLP OR "deep learning")
```

---

# 9. Recruitee

Typical pattern:

```text
<company>.recruitee.com
```

### Dorks

```text
site:recruitee.com "machine learning"
```

```text
site:recruitee.com "data scientist"
```

```text
site:recruitee.com "AI engineer"
```

```text
site:recruitee.com ("generative AI" OR LLM)
```

---

# 10. Personio

Typical patterns:

```text
<company>.jobs.personio.de
<company>.jobs.personio.com
```

### Dorks

```text
site:jobs.personio.de "machine learning"
```

```text
site:jobs.personio.de "data scientist"
```

```text
site:jobs.personio.de "AI engineer"
```

```text
site:jobs.personio.de ("generative AI" OR LLM)
```

```text
site:jobs.personio.com "machine learning"
```

---

# 11. Teamtailor

Typical pattern:

```text
<company>.teamtailor.com
```

### Dorks

```text
site:teamtailor.com "machine learning"
```

```text
site:teamtailor.com "data scientist"
```

```text
site:teamtailor.com "AI engineer"
```

```text
site:teamtailor.com ("generative AI" OR LLM)
```

---

# 12. BambooHR

Typical pattern:

```text
<company>.bamboohr.com/careers
```

### Dorks

```text
site:bamboohr.com/careers "machine learning"
```

```text
site:bamboohr.com/careers "data scientist"
```

```text
site:bamboohr.com/careers "AI engineer"
```

```text
site:bamboohr.com/careers ("generative AI" OR LLM)
```

---

# 13. iCIMS

iCIMS is less uniform because employers may use their own career domains.

### Dorks

```text
site:icims.com "machine learning"
```

```text
site:icims.com "data scientist"
```

```text
site:icims.com "AI engineer"
```

```text
site:icims.com ("artificial intelligence" OR "generative AI")
```

```text
inurl:icims "machine learning"
```

```text
inurl:icims "data scientist"
```

```text
inurl:icims "AI engineer"
```

---

# 14. SAP SuccessFactors

Common fingerprints:

```text
successfactors.com
sapsf.com
```

### Dorks

```text
site:successfactors.com "machine learning"
```

```text
site:successfactors.com "data scientist"
```

```text
site:successfactors.com "AI engineer"
```

```text
site:successfactors.com ("artificial intelligence" OR "generative AI")
```

```text
site:sapsf.com "machine learning"
```

---

# 15. Oracle / Taleo

### Dorks

```text
site:taleo.net "machine learning"
```

```text
site:taleo.net "data scientist"
```

```text
site:taleo.net "AI engineer"
```

```text
site:taleo.net ("artificial intelligence" OR "generative AI")
```

```text
site:oraclecloud.com "machine learning"
```

```text
site:oraclecloud.com "data scientist"
```

---

# 16. Jobvite

```text
site:jobs.jobvite.com "machine learning"
```

```text
site:jobs.jobvite.com "data scientist"
```

```text
site:jobs.jobvite.com "AI engineer"
```

```text
site:jobs.jobvite.com ("generative AI" OR LLM)
```

---

# 17. Breezy HR

```text
site:breezy.hr "machine learning"
```

```text
site:breezy.hr "data scientist"
```

```text
site:breezy.hr "AI engineer"
```

```text
site:breezy.hr ("generative AI" OR LLM)
```

---

# 18. JazzHR

```text
site:jazz.co "machine learning"
```

```text
site:jazz.co "data scientist"
```

```text
site:jazz.co "AI engineer"
```

```text
site:jazz.co ("generative AI" OR LLM)
```

Also:

```text
site:jazzhr.com "machine learning"
```

---

# 19. Pinpoint

```text
site:pinpointhq.com "machine learning"
```

```text
site:pinpointhq.com "data scientist"
```

```text
site:pinpointhq.com "AI engineer"
```

---

# 20. JobScore

```text
site:jobscore.com "machine learning"
```

```text
site:jobscore.com "data scientist"
```

```text
site:jobscore.com "AI engineer"
```

---

# 21. Phenom

Phenom frequently fronts employer-owned career domains, so direct `site:` searches can have lower recall.

Try:

```text
inurl:phenom "machine learning"
```

```text
inurl:phenom "data scientist"
```

```text
inurl:phenom "AI engineer"
```

```text
inurl:phenom ("generative AI" OR LLM)
```

---

# 22. Avature

```text
site:avature.net "machine learning"
```

```text
site:avature.net "data scientist"
```

```text
site:avature.net "AI engineer"
```

```text
site:avature.net ("artificial intelligence" OR "generative AI")
```

---

# 23. IBM Kenexa BrassRing

```text
site:brassring.com "machine learning"
```

```text
site:brassring.com "data scientist"
```

```text
site:brassring.com "AI engineer"
```

```text
inurl:brassring "machine learning"
```

---

# 24. CareerPlug

```text
site:careerplug.com "machine learning"
```

```text
site:careerplug.com "data scientist"
```

```text
site:careerplug.com "AI engineer"
```

---

# 25. Freshteam

```text
site:freshteam.com "machine learning"
```

```text
site:freshteam.com "data scientist"
```

```text
site:freshteam.com "AI engineer"
```

---

# 26. Rippling

Current job-board patterns can include:

```text
ats.rippling.com/<slug>/jobs
```

### Dorks

```text
site:rippling.com "machine learning" jobs
```

```text
site:rippling.com "data scientist" jobs
```

```text
site:rippling.com "AI engineer" jobs
```

---

# 27. Paylocity

```text
site:paylocity.com "machine learning" careers
```

```text
site:paylocity.com "data scientist" careers
```

```text
site:paylocity.com "AI engineer" careers
```

---

# 28. UKG

```text
site:ukg.com "machine learning" careers
```

```text
site:ukg.com "data scientist" careers
```

```text
site:ukg.com "AI engineer" careers
```

---

# 29. Dayforce

```text
site:dayforce.com "machine learning" careers
```

```text
site:dayforce.com "data scientist" careers
```

---

# 30. Cornerstone

```text
site:cornerstoneondemand.com "machine learning" careers
```

```text
site:cornerstone.com "data scientist" jobs
```

---

# 31. ADP

```text
site:jobs.adp.com "machine learning"
```

```text
site:jobs.adp.com "data scientist"
```

```text
site:jobs.adp.com "AI engineer"
```

---

# 32. Radancy / TalentBrew

These can front employer-owned career domains.

### Dorks

```text
inurl:radancy "machine learning"
```

```text
inurl:radancy "data scientist"
```

```text
inurl:talentbrew "machine learning"
```

```text
inurl:talentbrew "data scientist"
```

---

# 33. Comeet

```text
site:comeet.co "machine learning"
```

```text
site:comeet.co "data scientist"
```

```text
site:comeet.co "AI engineer"
```

---

# 34. Factorial

```text
site:factorialhr.com "machine learning" jobs
```

```text
site:factorialhr.com "data scientist" jobs
```

---

# 35. Softgarden

```text
site:softgarden.io "machine learning"
```

```text
site:softgarden.io "data scientist"
```

---

# 36. JOIN

```text
site:join.com "machine learning"
```

```text
site:join.com "data scientist"
```

```text
site:join.com "AI engineer"
```

---

# 37. Jobylon

```text
site:jobylon.com "machine learning"
```

```text
site:jobylon.com "data scientist"
```

---

# 38. TalentLyft

```text
site:talentlyft.com "machine learning"
```

```text
site:talentlyft.com "data scientist"
```

---

# 39. Manatal

```text
site:manatal.com "machine learning"
```

```text
site:manatal.com "data scientist"
```

---

# 40. Zoho Recruit

```text
site:zoho.com/recruit "machine learning"
```

```text
site:zoho.com/recruit "data scientist"
```

```text
site:zoho.com/recruit "AI engineer"
```

---

# 41. Generic Dork Formulas

Instead of manually remembering every query, use these templates.

## Formula A — AI/ML/Data titles

```text
site:PLATFORM
("machine learning engineer" OR
"ML engineer" OR
"AI engineer" OR
"AI/ML engineer" OR
"data scientist" OR
"data engineer")
```

## Formula B — AI

```text
site:PLATFORM
("artificial intelligence" OR
"AI engineer" OR
"AI developer" OR
"AI/ML")
```

## Formula C — Machine Learning

```text
site:PLATFORM
("machine learning" OR
"machine learning engineer" OR
"ML engineer" OR
"MLOps")
```

## Formula D — GenAI / LLM

```text
site:PLATFORM
("generative AI" OR
GenAI OR
LLM OR
"large language model" OR
RAG)
```

## Formula E — Traditional ML

```text
site:PLATFORM
("deep learning" OR
"computer vision" OR
"NLP" OR
"natural language processing" OR
"neural networks")
```

## Formula F — ML tooling

```text
site:PLATFORM
(PyTorch OR
TensorFlow OR
"scikit-learn" OR
XGBoost OR
MLflow OR
HuggingFace)
```

## Formula G — Data

```text
site:PLATFORM
("data scientist" OR
"data science" OR
"data engineer" OR
"data analytics" OR
"decision scientist")
```

## Formula H — Fresher / Entry Level

```text
site:PLATFORM
("machine learning" OR
"AI engineer" OR
"data scientist")
("entry level" OR
junior OR
graduate OR
"new grad" OR
fresher OR
trainee)
```

## Formula I — India

```text
site:PLATFORM
("machine learning" OR
"AI engineer" OR
"data scientist")
(India OR
Bengaluru OR
Bangalore OR
Hyderabad OR
Pune OR
Chennai OR
Mumbai OR
Delhi OR
Noida OR
Gurugram)
```

## Formula J — Remote

```text
site:PLATFORM
("machine learning" OR
"AI engineer" OR
"data scientist")
(remote OR
"work from home")
```

---

# 42. Employer-Owned Career Domains

This is important for Workday, Phenom, iCIMS, Radancy, Avature, SuccessFactors, Oracle, etc.

The ATS may be hidden behind:

```text
careers.company.com
jobs.company.com
company.com/careers
```

Therefore search using the ATS fingerprint itself:

```text
"machine learning" "workday"
```

```text
"data scientist" "greenhouse"
```

```text
"AI engineer" "successfactors"
```

```text
"machine learning" "iCIMS"
```

```text
"data scientist" "taleo"
```

```text
"AI engineer" "phenom"
```

```text
"machine learning" "avature"
```

```text
"data scientist" "brassring"
```

This second tier is necessary because `site:ATS_DOMAIN` searches can miss jobs where the employer owns the visible career domain.

---

# 43. High-Priority ATS Platform List

For broad AI/ML/Data job discovery, prioritize:

```text
Greenhouse
Lever
Ashby
Workday
SmartRecruiters
Workable
Recruitee
Personio
Teamtailor
BambooHR
iCIMS
SAP SuccessFactors
Oracle/Taleo
Jobvite
Breezy HR
JazzHR
Pinpoint
Phenom
Avature
BrassRing
CareerPlug
Freshteam
Rippling
Paylocity
UKG
Dayforce
Cornerstone
Radancy/TalentBrew
Comeet
Factorial
Jobylon
JOIN
TalentLyft
Zoho Recruit
```

---

# 44. Recommended Search Architecture

Don't depend on one giant Google query.

Use two tiers:

```text
                    JOB DISCOVERY
                         |
             +-----------+-----------+
             |                       |
          TIER 1                  TIER 2
       ATS domains          Employer-owned domains
             |                       |
       site:ATS_DOMAIN         AI/ML keywords
             |                       +
       AI/ML keywords          ATS fingerprint
             |                       |
             +-----------+-----------+
                         |
                  COLLECT RESULTS
                         |
                  EXTRACT JOB URL
                         |
                   EXTRACT JOB ID
                         |
                 EXTRACT EMPLOYER
                         |
              CHECK POSTING STATUS
                         |
                  DEDUPLICATE
                         |
                AI/ML/Data FILTER
```

## Important limitation

Search-engine indexing does **not** equal the complete live job inventory.

A job can be:

- not indexed yet
- blocked from indexing
- removed from the index
- hosted behind an employer-owned domain
- dynamically rendered
- accessible only through an ATS API
- already closed while still appearing in search results

Therefore, for high coverage:

```text
Dorking
   ↓
Discover ATS / employer
   ↓
Identify job feed/API
   ↓
Enumerate jobs directly
   ↓
Filter AI/ML/Data
   ↓
Check whether applications are still open
```

Dorking is best treated as the **discovery layer**, not the complete job database.
