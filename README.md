deva# AI Job Search Agent 🤖💼

> An intelligent, autonomous AI Job Search Agent built with Python, Streamlit, PyMuPDF, OpenAI, and Apify. Designed for beginners learning AI Agent architectures.

---

## 📚 What is an AI Agent?

An **AI Agent** is an autonomous system that takes inputs from its **Environment**, processes them through **Perception** and **Reasoning**, formulates a **Plan**, executes **Actions** using **Tools**, gathers **Observations**, and makes **Decisions** to achieve a specific **Goal**.

Unlike a simple script or a basic LLM prompt, an AI Agent acts as an **orchestration layer** that dynamically coordinates multiple tools (PDF parsers, API web scrapers, LLMs, and ranking algorithms) to solve complex workflows.

---

## 🎯 What This Project Does

1. **Upload Resume**: Accepts any user's PDF resume and parses raw text cleanly.
2. **Candidate Profile**: Uses LLM reasoning to extract technical skills, experience level, and target roles.
3. **Formulate Search Strategy**: Dynamically plans optimal job search queries based on candidate profile and user preferences.
4. **Live Job Search**: Connects to legitimate live job sources via the Apify API (e.g. Google Jobs Scraper) to fetch active listings.
5. **Normalize & Deduplicate**: Standardizes raw API pay-loads and eliminates duplicate postings.
6. **Evaluate & Match**: Calculates compatibility scores, skill overlaps, and missing skills.
7. **Rank & Present**: Sorts opportunities from highest to lowest relevance and presents clean job cards with original apply links.

---

## 🏛️ AI Agent Core Concepts Mapping

| Agent Concept | Implementation in this Application |
|---|---|
| **Environment** | User PDF resume + Web Job APIs (Apify) + User Preference Settings |
| **Perception** | PDF text extraction (`resume/parser.py`) & comprehension of user constraints |
| **Reasoning** | LLM analysis (`llm/client.py`) for candidate profiling & qualitative match rationale |
| **Planning** | Dynamic query generation strategy (`prompts/search_prompt.py`) |
| **Tool Usage** | Calling `ResumeParserTool`, `LLMClientTool`, `ApifyJobClient`, `MatcherTool`, `RankerTool` |
| **Action** | Executing API job scrapers across multiple search queries concurrently |
| **Observation** | Ingesting raw JSON API responses, normalizing schemas, and deduplicating jobs |
| **Decision Making** | Skill-overlap scoring, filtering, ranking jobs, and recommending top matches |
| **Goal** | Find, score, and rank the most suitable live job opportunities for any user |

---

## 🏗️ Complete Workflow Architecture

```text
               USER
                │
         [ Upload PDF Resume ]
                │
                ▼
          RESUME PARSER (PyMuPDF)
                │
                ▼
        CANDIDATE PROFILE (LLM / Regex)
                │
                ▼
       ┌────────────────────────┐
       │     AI AGENT           │
       │  (Orchestration Layer) │
       └───────────┬────────────┘
                   │
                   ▼
        JOB SEARCH TOOL MANAGER
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
    APIFY API           DEMO MODE
(Live Job Scraper)      (Fallback Data)
        │                     │
        └──────────┬──────────┘
                   │
                   ▼
         JOB NORMALIZER & DEDUP
                   │
                   ▼
         MATCHING ENGINE & SCORES
                   │
                   ▼
          RANKING & FILTERING
                   │
                   ▼
         RECOMMENDED JOB CARDS
                   │
                   ▼
     [ APPLY / VIEW ORIGINAL JOB URL ]
```

---

## 📁 Project Structure

```text
AI-Job-Search-Agent/
│
├── app.py                     # Streamlit web application dashboard
├── main.py                    # Command-line (CLI) test runner
│
├── agent/                     # Core Agent Orchestration Layer
│   ├── __init__.py
│   ├── agent.py               # Main JobSearchAgent class
│   ├── state.py               # Agent State Machine tracking progress
│   └── tools.py               # Tool registry wrapping capabilities
│
├── resume/                    # Resume Perception Module
│   ├── __init__.py
│   └── parser.py              # PyMuPDF text extraction & validation
│
├── llm/                       # LLM Reasoning Layer
│   ├── __init__.py
│   └── client.py              # OpenAI Python SDK client with fallback logic
│
├── jobs/                      # Action & Observation Layer
│   ├── __init__.py
│   ├── apify_client.py        # Apify API SDK client for live job scraping
│   ├── job_search.py          # Job Search Manager & concurrent execution
│   └── normalizer.py          # Schema normalizer & duplicate detection
│
├── matching/                  # Decision Making Layer
│   ├── __init__.py
│   ├── matcher.py             # Match score evaluator & skill gap analysis
│   └── ranker.py              # Ranking and sorting engine
│
├── memory/                    # Preference Memory Layer
│   ├── __init__.py
│   └── memory.py              # Session memory for non-sensitive user settings
│
├── prompts/                   # Reusable Prompt Templates
│   ├── __init__.py
│   ├── resume_prompt.py       # Candidate profile JSON prompt
│   ├── search_prompt.py       # Query planning prompt
│   └── matching_prompt.py     # Qualitative fit explanation prompt
│
├── requirements.txt           # Python dependencies
├── .env.example               # Template for environment credentials
├── .gitignore                 # Excludes secrets & temporary files
└── README.md                  # Documentation (this file)
```

---

## ⚡ Installation & Setup

### 1. Prerequisites
- Python 3.9+ installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to add your credentials:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
APIFY_API_TOKEN=your_apify_api_token_here
APIFY_ACTOR_ID=misceres/indeed-scraper
APIFY_COUNTRY=IN
```

*(Note: You can also enter API keys directly in the Streamlit sidebar UI).*

---

## 🚀 How to Run the Application

### Option A: Interactive Streamlit Web UI (Recommended)
Run the Streamlit app:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Option B: Command Line Interface (CLI Test)
Run the programmatic agent test script:
```bash
python main.py
```

---

## 🔍 How Live Job Search Works

- **When `APIFY_API_TOKEN` is configured**: The Agent sends generated queries to the Apify API which launches the specified Actor (e.g. `apify/google-jobs-scraper`) to gather real active job listings.
- **When `APIFY_API_TOKEN` is missing**: The app gracefully displays `"Live job search is not configured."` and uses labeled **DEMO DATA** to demonstrate the complete AI Agent workflow.

---

## 🔒 Security Principles

1. **No Hardcoded Keys**: API keys are loaded via `.env` or user UI input.
2. **Ignored Secrets**: `.env` is listed in `.gitignore` to prevent accidental commits.
3. **No Applications Submitted**: The application NEVER submits job applications automatically. It only provides original direct links for the user to apply manually.
4. **Data Privacy**: Resumes are parsed in-memory and are not permanently stored on remote servers.

---

## 🛠️ Summary of Technologies Used
- **UI**: Streamlit
- **PDF Extraction**: PyMuPDF (`pymupdf`)
- **LLM**: OpenAI API (`openai` Python SDK v1.0+)
- **Live Scraper**: Apify API (`apify-client`)
- **State & Logic**: Pure Python OOP & Functional design
