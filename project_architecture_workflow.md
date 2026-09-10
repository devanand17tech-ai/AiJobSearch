# AI Job Search Agent: Workflow and Architecture

This project is a classic AI agent pipeline: it reads a resume, understands the candidate profile, searches for jobs, evaluates fit, and ranks the best matches.

The core orchestration is in `agent/agent.py`, with the entry points being `app.py` for the Streamlit UI and `main.py` for CLI testing.

## 1) End-to-end workflow

The actual flow is:

1. User provides a resume
   - In the UI, the user uploads a PDF in `app.py`
   - In the CLI, a sample PDF is generated in `main.py`

2. Resume parsing
   - The PDF is read using PyMuPDF in `resume/parser.py`
   - Raw text is cleaned and normalized
   - Output: plain resume text

3. Candidate profiling
   - `llm/client.py` turns the resume text into a structured profile
   - Fields include:
     - skills
     - programming_languages
     - frameworks
     - preferred_roles
     - experience_level
   - If OpenAI is configured, it uses LLM JSON extraction
   - Otherwise, it falls back to heuristic parsing

4. Search planning
   - The agent asks the LLM to generate targeted job queries
   - Example: “Java Backend Developer”, “Spring Boot Developer”, etc.
   - This happens via the query-generation methods in `llm/client.py`

5. Job acquisition
   - `jobs/job_search.py` performs the actual search
   - If Apify token is available, it searches live jobs through Apify
   - If not, it uses a demo dataset as a fallback
   - Searches are done concurrently for multiple query variations

6. Normalization and deduplication
   - Raw results are normalized into a consistent structure
   - Duplicate jobs are removed
   - This happens in `jobs/normalizer.py` and `jobs/job_search.py`

7. Matching
   - `matching/matcher.py` compares the candidate profile against each job
   - It calculates:
     - skill overlap
     - title fit
     - location preference fit
     - score out of 100
   - It can also use OpenAI to generate a human-style reason

8. Ranking
   - `matching/ranker.py` filters and sorts the results
   - It can enforce:
     - minimum score
     - remote-only filter
     - location filtering
     - best-match sorting

9. Final response
   - The agent returns:
     - candidate profile
     - search plan
     - recommended jobs
     - match reasons
     - execution history

## 2) Architecture layers

The project follows a layered agent design:

### A. UI Layer
- `app.py`: Streamlit interface
- `main.py`: command-line test runner

### B. Agent Orchestration Layer
- `agent/agent.py`
- This is the brain of the app
- It orchestrates:
  - resume extraction
  - profile generation
  - search query creation
  - job search
  - matching
  - ranking
  - final results

### C. State Layer
- `agent/state.py`
- Tracks the lifecycle of the agent:
  - RESUME_UPLOADED
  - PROFILE_CREATED
  - PLANNING_SEARCH
  - SEARCHING_JOBS
  - MATCHING
  - RANKING
  - COMPLETED / FAILED

This gives the project a clear state-machine pattern.

### D. Tool Layer
- `agent/tools.py`
- Wraps the plumbing in reusable methods such as:
  - parse_resume_tool
  - extract_profile_tool
  - plan_search_queries_tool
  - search_jobs_tool
  - match_job_tool
  - rank_jobs_tool

This is a good AI-agent pattern: the orchestrator calls tools rather than embedding every responsibility in one class.

### E. LLM Reasoning Layer
- `llm/client.py`
- Responsible for:
  - parsing the resume into structured JSON
  - generating search queries
  - generating job-fit reasoning

### F. Job Search Layer
- `jobs/job_search.py`
- `jobs/apify_client.py`
- Handles live job fetching from Apify and fallback to demo job data

### G. Matching & Ranking Layer
- `matching/matcher.py`
- `matching/ranker.py`
- Converts search results into a relevance score and sorts them

### H. Memory Layer
- `memory/memory.py`
- Stores non-sensitive preferences like:
  - preferred_role
  - location
  - job_type
  - experience_level

## 3) Architectural flow in one diagram

Resume Upload
  ↓
PDF Text Extraction
  ↓
LLM Candidate Profile Builder
  ↓
Agent Orchestrator
  ↓
Search Query Generator
  ↓
Job Search Manager
  ↓
Normalize + Deduplicate Jobs
  ↓
Match Jobs to Candidate
  ↓
Rank Top Opportunities
  ↓
Return Recommended Jobs

## 4) Why this is “agentic”

This is not just a normal script. It behaves like an agent because it has:

- a goal: find the best jobs for the user
- perception: parse resume text
- reasoning: understand skills and role fit
- planning: generate job search queries
- action: call external job APIs
- observation: inspect job listings
- decision-making: score and rank jobs

That is the core AI agent pattern the project is demonstrating.

## 5) In short

The project is essentially a resume-to-job matching agent:

- resume in
- candidate profile extracted
- queries generated
- jobs fetched
- jobs matched and ranked
- best opportunities shown back to the user

If you want, I can also give you a simplified version, a class diagram, or a file-by-file explanation.
