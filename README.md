# Multi-Agent AI Job Search System 🤖💼

> A modular, production-style **Multi-Agent AI Job Search System** built with Python, LangGraph, Streamlit, PyMuPDF, OpenAI, Pydantic, and Apify.

---

## 📚 Multi-Agent Architecture Overview

Unlike a single-agent script where one controller handles parsing, searching, and scoring in a monolithic loop, this system implements an autonomous **team of 6 specialized AI agents**. Each agent has bounded responsibilities, formal data contracts via **Pydantic models**, dedicated system prompts, and interacts through a central **LangGraph StateGraph**:

```text
                           USER RESUME (PDF) + PREFERENCES
                                          │
                                          ▼
                          ┌───────────────────────────────┐
                          │     Agent 6: Orchestrator     │
                          │   (LangGraph State Machine)   │
                          └───────┬───────────────┬───────┘
                                  │               │
            ┌─────────────────────┘               └─────────────────────┐
            ▼                                                           ▼
┌───────────────────────────────┐                   ┌───────────────────────────────┐
│ Agent 1: Resume Analysis      │                   │ Shared State (LangGraph)      │
│ - PyMuPDF Extraction          │                   │ - CandidateProfile (Pydantic) │
│ - Technical Skill Discovery   │                   │ - RawJobListings              │
│ - Education, Grad Year, Exp   │                   │ - VerifiedJobListings         │
│ - Target Roles & Weak Skills  │                   │ - MatchedJobListings          │
└───────────────┬───────────────┘                   │ - CareerAdviceReport          │
                │                                   │ - ExecutionTraceLogs          │
                ▼                                   └───────────────────────────────┘
┌───────────────────────────────┐
│ Agent 2: Job Search Agent     │
│ - Intelligent Query Strategy  │
│ - Apify Live Search & Fallback│
│ - Fresher/Intern/Exp Targeting│
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Agent 3: Job Verification     │
│ - Application URL Validity    │
│ - Semantic Deduplication      │
│ - Eligibility & Grad Criteria │
│ - Expired/Suspicious Flagging │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Agent 4: Job Matching Agent   │
│ - Transparent Scoring Logic   │
│ - Skill Overlap & Missing Tech│
│ - Grad Year & Exp Eligibility │
│ - Explainable Match Rationale │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Agent 5: Career Advisor Agent │
│ - Opportunity Prioritization  │
│ - Systemic Skill Gap Analysis │
│ - Tech Stack Learning Roadmap │
│ - Role-Specific Resume Advice │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Orchestrator Final Response   │
│ - Rich Streamlit Interface    │
│ - Live Agent Progress Status  │
│ - Verified & Matched Cards    │
│ - Direct Links & Career Plan  │
└───────────────────────────────┘
```

---

## 🤖 The 6 Specialist Agents

### 1. Resume Analysis Agent (`agents/resume_agent.py`)
- **Responsibilities**: Extracts text from PDF resumes using PyMuPDF; structures technical competencies, programming languages, frameworks, databases, developer tools, education history, graduation year, total years of experience, target roles, and missing industry skills.
- **Output**: `CandidateProfile` (Pydantic model).

### 2. Job Search Agent (`agents/job_search_agent.py`)
- **Responsibilities**: Plans 3–5 targeted search query strings tailored to candidate seniority (including fresher, junior, or entry-level variants when experience $\le 1$ year); queries live web listings via Apify actors or fallback database.
- **Output**: `List[RawJobListing]`.

### 3. Job Verification Agent (`agents/verification_agent.py`)
- **Responsibilities**: Audits application URLs for syntax and host legitimacy; deduplicates across URL and composite (`title|company|location`) signatures; extracts experience requirements (`min_experience_years`, `max_experience_years`), graduation-year restrictions (`graduation_years_accepted`), and application deadlines; flags expired or suspicious listings with documented evidence without hallucinating missing data.
- **Output**: `List[VerifiedJob]`.

### 4. Job Matching Agent (`agents/matching_agent.py`)
- **Responsibilities**: Computes transparent, explainable compatibility scores (0–100) using weighted subscores:
  - Skill Overlap Subscore ($\le 50$ pts)
  - Experience Alignment Subscore ($\le 20$ pts)
  - Role Title Alignment Subscore ($\le 15$ pts)
  - Location & Workplace Alignment Subscore ($\le 15$ pts)
- Compares graduation-year and experience requirements against candidate credentials to assign formal eligibility status (`Eligible`, `Marginal`, `Ineligible`).
- **Output**: `List[MatchedJob]`.

### 5. Career Advisor Agent (`agents/career_advisor_agent.py`)
- **Responsibilities**: Synthesizes verified and matched listings; computes a prioritized application queue (which jobs to apply for first); detects systemic market skill gaps across listings; recommends high-ROI technologies to learn; provides actionable resume improvement suggestions.
- **Output**: `CareerAdvice`.

### 6. Orchestrator Agent (`agents/orchestrator.py`)
- **Responsibilities**: Central coordinator maintaining shared workflow state (`AgentWorkflowState`); manages state transitions across a LangGraph directed graph; tracks execution duration and status for every agent; handles failures and retries; notifies UI of live agent transitions.

---

## 📁 Project Structure

```text
AI-Job-Search-Agent/
│
├── models/                         # Formal Pydantic schemas & workflow state
│   ├── __init__.py
│   ├── schemas.py                  # CandidateProfile, RawJobListing, VerifiedJob, MatchedJob, CareerAdvice
│   └── state.py                    # LangGraph TypedDict & Pydantic state model
│
├── agents/                         # The 6 Autonomous Specialist Agents
│   ├── __init__.py
│   ├── orchestrator.py             # Agent 6: LangGraph Central Orchestrator
│   ├── resume_agent.py             # Agent 1: Resume Analysis Agent
│   ├── job_search_agent.py         # Agent 2: Job Search Agent
│   ├── verification_agent.py       # Agent 3: Job Verification Agent
│   ├── matching_agent.py           # Agent 4: Job Matching Agent
│   └── career_advisor_agent.py     # Agent 5: Career Advisor Agent
│
├── tools/                          # Modular agent tools
│   ├── __init__.py
│   ├── resume_parser.py            # PyMuPDF extraction tool
│   ├── apify_tool.py               # Apify job search and mock fallback tool
│   └── job_verification_tool.py    # URL validator, eligibility extractor, and audit tool
│
├── prompts/                        # Structured system and user prompts
│   ├── __init__.py
│   ├── resume_prompt.py            # Agent 1 prompt templates
│   ├── search_prompt.py            # Agent 2 prompt templates
│   ├── verification_prompt.py      # Agent 3 prompt templates
│   ├── matching_prompt.py          # Agent 4 prompt templates
│   └── advisor_prompt.py           # Agent 5 prompt templates
│
├── tests/                          # Automated test suite
│   ├── __init__.py
│   └── test_multi_agent_system.py  # Comprehensive multi-agent unit & integration tests
│
├── resume/                         # Core perception engine (preserved)
│   └── parser.py
├── jobs/                           # Scraper & normalizer engine (preserved)
│   ├── apify_client.py
│   ├── job_search.py
│   └── normalizer.py
├── matching/                       # Core scoring engine (preserved)
│   ├── matcher.py
│   └── ranker.py
├── memory/                         # User preference storage (preserved)
│   └── memory.py
│
├── app.py                          # Streamlit Multi-Agent UI dashboard
├── main.py                         # Command-Line (CLI) multi-agent test runner
├── requirements.txt                # Updated Python dependencies
├── .env.example                    # Environment credentials template
└── README.md                       # Documentation (this file)
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

Edit `.env` to configure your credentials:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
APIFY_API_TOKEN=your_apify_api_token_here
APIFY_ACTOR_ID=misceres/indeed-scraper
APIFY_COUNTRY=IN
```

*(Note: API keys can also be entered directly in the Streamlit sidebar UI).*

---

## 🚀 How to Run the Application

### Option A: Interactive Streamlit Web UI (Recommended)
Launch the Streamlit dashboard:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

**Features in UI:**
- Resume PDF upload with automated size & format validation.
- Live agent execution pipeline with status badges for each specialist agent.
- Metrics grid: Discovered jobs, verified listings, flagged warnings, top match score.
- **Recommended Jobs Tab**: Verified cards, eligibility status, transparent score breakdown, matched/missing skill tags, and direct application links.
- **Career Advisor Guidance Tab**: Priority application queue, systemic skill gap analysis, learning roadmap, and resume optimization tips.
- **Candidate Profile Tab**: Extracted skills, graduation year, target roles, and formulated search queries.
- **Audit & Trace Logs Tab**: Chronological event logs for complete observability.

### Option B: Command Line Interface (CLI Tester)
Run the CLI test script:
```bash
python main.py
```

---

## 🧪 Running Automated Tests

Run the comprehensive multi-agent test suite:
```bash
python -m unittest tests/test_multi_agent_system.py
```

The test suite validates:
1. `ResumeAnalysisAgent`: PDF extraction and profile structuring.
2. `JobSearchAgent`: Query planning and job discovery.
3. `JobVerificationAgent`: URL validation, duplicate detection, and eligibility auditing.
4. `JobMatchingAgent`: Multi-factor compatibility scoring and eligibility classification.
5. `CareerAdvisorAgent`: Application prioritization, skill gap analysis, and learning roadmap.
6. `MultiAgentOrchestrator`: Full directed graph execution and error recovery.

---

## 🔒 Security & Robustness Principles

1. **Zero Key Leakage**: API credentials are loaded exclusively from `.env` or password-masked Streamlit inputs; `.env` is excluded in `.gitignore`.
2. **Offline & Resilient Execution**: All agents feature heuristic fallback modes to ensure testing and execution succeed even if external APIs encounter downtime or rate limits.
3. **No Automatic Applications**: The system never submits job applications on behalf of the user. It provides verified direct links for manual candidate review.
4. **Data Privacy**: Uploaded resumes are processed in-memory and are not permanently persisted to remote storage.
