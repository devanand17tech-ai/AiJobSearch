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
    print("=" * 60)
    print("AI Job Search Agent - Command Line Interface Tester")
    print("=" * 60)

    sample_pdf = create_sample_pdf("sample_resume.pdf")
    print(f"[CLI] Created sample PDF resume at '{sample_pdf}'")

    openai_key = os.getenv("OPENAI_API_KEY", "")
    apify_token = os.getenv("APIFY_API_TOKEN", "")

    print(f"[CLI] OpenAI API Key: {'Configured' if openai_key else 'Not Configured (using heuristic fallback)'}")
    print(f"[CLI] Apify API Token: {'Configured' if apify_token else 'Not Configured (using demo job source)'}")
    print("-" * 60)

    agent = JobSearchAgent(openai_api_key=openai_key, apify_token=apify_token)

    user_preferences = {
        "preferred_role": "Java Backend Developer",
        "location": "Remote",
        "job_type": "Remote Only",
        "experience_level": "Senior",
        "max_jobs": 5
    }

    print("[CLI] Launching AI Agent Pipeline...")
    result = agent.run_pipeline(
        resume_source=sample_pdf,
        user_preferences=user_preferences,
        sort_by="Best match"
    )

    if not result.get("success"):
        print(f"[CLI Error] Pipeline failed: {result.get('error')}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("SUCCESSFUL PIPELINE RESULTS")
    print("=" * 60)
    
    print("\n--- CANDIDATE PROFILE ---")
    profile = result.get("profile", {})
    print(f"Name: {profile.get('name')}")
    print(f"Skills: {', '.join(profile.get('skills', []))}")
    print(f"Preferred Roles: {', '.join(profile.get('preferred_roles', []))}")

    print("\n--- FORMULATED SEARCH PLAN ---")
    print(f"Queries: {result.get('search_plan')}")

    print("\n--- RECOMMENDED JOBS ---")
    jobs = result.get("jobs", [])
    for idx, job in enumerate(jobs, 1):
        match = job.get("match", {})
        print(f"\n[{idx}] {job.get('title')} @ {job.get('company')}")
        print(f"    Location: {job.get('location')}")
        print(f"    Match Score: {match.get('score')}%")
        print(f"    Matched Skills: {', '.join(match.get('matched_skills', []))}")
        print(f"    Reason: {match.get('reason')}")
        print(f"    Apply URL: {job.get('url')}")

    print("\n" + "=" * 60)
    print("AI Agent Execution History:")
    for entry in result.get("history", []):
        print(f"  [{entry['timestamp']}] {entry['state']}: {entry['message']}")
    print("=" * 60)

    # Clean up temporary sample PDF
    if os.path.exists(sample_pdf):
        os.remove(sample_pdf)

if __name__ == "__main__":
    main()
