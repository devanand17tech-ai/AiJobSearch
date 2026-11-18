import os
import sys
from dotenv import load_dotenv

from agent.agent import JobSearchAgent

load_dotenv()

# Sample Resume Text for CLI testing
SAMPLE_RESUME_TEXT = """
ALEXANDER WANG
Email: alexander.wang@example.com | Phone: +1-555-019-2834 | San Francisco, CA

SUMMARY:
Results-driven Senior Java Backend Engineer with 5+ years of experience designing and implementing scalable microservices, REST APIs, and cloud-native solutions.

SKILLS:
- Languages: Java 17, Python, SQL, TypeScript
- Frameworks & Tools: Spring Boot, Spring Cloud, Hibernate, FastAPI, Docker, Kubernetes, Git
- Databases: PostgreSQL, MySQL, Redis, MongoDB
- Cloud & DevOps: AWS (EC2, S3, RDS), CI/CD (GitHub Actions), RESTful API design

EXPERIENCE:
Senior Software Engineer | Apex Financial Systems (2021 - Present)
- Architected high-throughput payment processing service using Java 17 and Spring Boot, handling 2M+ daily transactions.
- Optimized database queries in PostgreSQL and implemented Redis caching, reducing API latency by 45%.
- Containerized application services with Docker and deployed to AWS EKS using Kubernetes.

Backend Developer | TechCorp Solutions (2018 - 2021)
- Developed REST APIs in Java and MySQL for client portal system.
- Collaborated with frontend team (React) to define API contracts and WebSocket integrations.

EDUCATION:
B.S. in Computer Science | University of California, Berkeley (2014 - 2018)
"""

def create_sample_pdf(pdf_path: str = "sample_resume.pdf"):
    """Generates a sample PDF resume file using PyMuPDF for CLI testing."""
    import pymupdf as fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), SAMPLE_RESUME_TEXT)
    doc.save(pdf_path)
    doc.close()
    return pdf_path

def main():
    print("=" * 70)
    print("Multi-Agent AI Job Search System - Command Line Interface Tester")
    print("=" * 70)

    sample_pdf = create_sample_pdf("sample_resume.pdf")
    print(f"[CLI] Created sample PDF resume at '{sample_pdf}'")

    openai_key = os.getenv("OPENAI_API_KEY", "")
    apify_token = os.getenv("APIFY_API_TOKEN", "")

    print(f"[CLI] OpenAI API Key: {'Configured' if openai_key else 'Not Configured (using heuristic fallback)'}")
    print(f"[CLI] Apify API Token: {'Configured' if apify_token else 'Not Configured (using demo job source)'}")
    print("-" * 70)

    agent = JobSearchAgent(openai_api_key=openai_key, apify_token=apify_token)

    user_preferences = {
        "preferred_role": "Java Backend Developer",
        "location": "Remote",
        "job_type": "Remote Only",
        "experience_level": "Senior",
        "max_jobs": 5
    }

    print("[CLI] Launching Multi-Agent System (6 Specialist Agents)...")
    result = agent.run_pipeline(
        resume_source=sample_pdf,
        user_preferences=user_preferences,
        sort_by="Best match"
    )

    if not result.get("success") and not result.get("candidate_profile"):
        print(f"[CLI Error] Pipeline failed: {result.get('errors') or result.get('error')}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("MULTI-AGENT SYSTEM EXECUTION RESULTS")
    print("=" * 70)

    # 1. Candidate Profile (Agent 1)
    print("\n--- AGENT 1: CANDIDATE PROFILE ---")
    profile = result.get("profile", {})
    print(f"Name: {profile.get('name')}")
    print(f"Graduation Year: {profile.get('graduation_year') or '2018'}")
    print(f"Experience Level: {profile.get('experience_level')}")
    print(f"Target Roles: {', '.join(profile.get('preferred_roles', []))}")
    print(f"Technical Skills: {', '.join(profile.get('skills', []))}")
    if profile.get("weak_or_missing_skills"):
        print(f"Weak/Missing Industry Skills: {', '.join(profile.get('weak_or_missing_skills', []))}")

    # 2. Formulated Search Plan (Agent 2)
    print("\n--- AGENT 2: INTELLIGENT SEARCH QUERIES ---")
    queries = result.get("search_plan", [])
    print(f"Planned Queries: {queries}")

    # 3. Verification Audit (Agent 3)
    print("\n--- AGENT 3: JOB VERIFICATION AUDIT ---")
    summary = result.get("verification_summary", {})
    print(f"Total Audited: {summary.get('total_audited', len(result.get('jobs', [])))}")
    print(f"Verified Legitimate: {summary.get('verified_legitimate', 0)}")
    print(f"Flagged with Warnings: {summary.get('flagged', 0)}")
    print(f"Duplicates Removed: {summary.get('duplicates_removed', 0)}")

    # 4. Matched Opportunities (Agent 4)
    print("\n--- AGENT 4: MATCHED & SCORED OPPORTUNITIES ---")
    jobs = result.get("jobs", [])
    for idx, job in enumerate(jobs, 1):
        match = job.get("match", {})
        verified = job.get("verified", {})
        print(f"\n[{idx}] {job.get('title')} @ {job.get('company')}")
        print(f"    Location: {job.get('location')} | Type: {job.get('job_type')}")
        print(f"    Match Score: {match.get('score')}% | Eligibility: {match.get('eligibility_status', 'Eligible')}")
        print(f"    Verification Status: {verified.get('status', 'VERIFIED')}")
        print(f"    Matched Skills: {', '.join(match.get('matched_skills', []))}")
        print(f"    Missing Skills: {', '.join(match.get('missing_skills', [])) or 'None'}")
        print(f"    Match Explanation: {match.get('reason')}")
        print(f"    Apply Link: {job.get('url')}")

    # 5. Career Advisor Recommendations (Agent 5)
    advice = result.get("career_advice")
    if advice:
        print("\n--- AGENT 5: CAREER ADVISOR RECOMMENDATIONS ---")
        advice_dict = advice.model_dump() if hasattr(advice, "model_dump") else advice
        print(f"Executive Summary:\n  {advice_dict.get('executive_summary', '')}\n")
        
        print("Application Priority Queue:")
        for app in advice_dict.get("priority_applications", []):
            print(f"  #{app.get('priority_rank')}: {app.get('title')} @ {app.get('company')} [{app.get('apply_urgency')} Urgency] - {app.get('reason_to_apply_first')}")

        print("\nSystemic Market Skill Gaps:")
        for gap in advice_dict.get("systemic_skill_gaps", []):
            print(f"  - {gap.get('skill_name')}: {gap.get('learning_recommendation')}")

        print(f"\nRecommended Tech to Learn: {', '.join(advice_dict.get('technologies_to_learn', []))}")
        print("\nResume Optimization Tips:")
        for tip in advice_dict.get("resume_improvements", []):
            print(f"  • {tip}")

    # 6. Execution Trace History (Agent 6)
    print("\n" + "=" * 70)
    print("AGENT 6: ORCHESTRATOR TRACE LOGS")
    print("=" * 70)
    for entry in result.get("history", []):
        print(f"  [{entry['timestamp']}] {entry['state']}: {entry['message']}")
    print("=" * 70)

    # Clean up temporary sample PDF
    if os.path.exists(sample_pdf):
        os.remove(sample_pdf)

if __name__ == "__main__":
    main()
