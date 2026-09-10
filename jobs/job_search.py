import os
import concurrent.futures
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from .apify_client import ApifyJobClient
from .normalizer import normalize_job, deduplicate_jobs

load_dotenv()

DEMO_JOB_DATABASE = [
    {
        "title": "Java Backend Developer",
        "company": "TechCorp Innovations",
        "location": "Bangalore, India (Hybrid)",
        "description": "Seeking an experienced Java Backend Developer to build scalable RESTful microservices. Requirements: 3+ years experience with Java 17, Spring Boot, Hibernate, MySQL, and Docker. Experience with AWS and Kafka is a plus.",
        "salary": "₹12,000,000 - ₹18,000,000 / year",
        "experience": "3-5 years",
        "job_type": "Full-Time / Hybrid",
        "skills": ["Java", "Spring Boot", "MySQL", "REST API", "Microservices", "Docker"],
        "url": "https://example.com/jobs/java-backend-dev-techcorp",
        "source": "DEMO DATA (Sample listing)",
        "date_posted": "2 days ago",
        "is_demo": True
    },
    {
        "title": "Senior Python & AI Engineer",
        "company": "DataMind Solutions",
        "location": "Remote",
        "description": "Looking for a Senior Python Developer with strong background in FastAPI, OpenAI API, LangChain, and PostgreSQL. You will design agentic AI pipelines and RAG workflows.",
        "salary": "$120,000 - $150,000 / year",
        "experience": "5+ years",
        "job_type": "Remote",
        "skills": ["Python", "FastAPI", "OpenAI", "PostgreSQL", "Docker", "Git", "REST API"],
        "url": "https://example.com/jobs/sr-python-ai-datamind",
        "source": "DEMO DATA (Sample listing)",
        "date_posted": "1 day ago",
        "is_demo": True
    },
    {
        "title": "Full Stack Engineer (React + Node.js)",
        "company": "Apex Global Systems",
        "location": "New York, NY (Hybrid)",
        "description": "Apex is hiring a Full Stack Engineer proficient in React, TypeScript, Node.js, and MongoDB. Responsible for developing modern web interfaces and GraphQL APIs.",
        "salary": "$110,000 - $135,000 / year",
        "experience": "2-4 years",
        "job_type": "Full-Time",
        "skills": ["JavaScript", "TypeScript", "React", "Node.js", "MongoDB", "GraphQL"],
        "url": "https://example.com/jobs/fullstack-react-apex",
        "source": "DEMO DATA (Sample listing)",
        "date_posted": "3 days ago",
        "is_demo": True
    },
    {
        "title": "Junior Java Developer",
        "company": "NextGen Softwares",
        "location": "Bangalore, India",
        "description": "Entry-level position for passionate developers. Core requirements: Java, OOPs concepts, basic Spring Boot knowledge, SQL queries, and good problem solving skills.",
        "salary": "₹6,000,000 - ₹9,000,000 / year",
        "experience": "0-2 years",
        "job_type": "Full-Time",
        "skills": ["Java", "Spring Boot", "SQL", "Git"],
        "url": "https://example.com/jobs/jr-java-nextgen",
        "source": "DEMO DATA (Sample listing)",
        "date_posted": "Just posted",
        "is_demo": True
    },
    {
        "title": "DevOps & Cloud Infrastructure Engineer",
        "company": "CloudScale Technologies",
        "location": "Remote",
        "description": "Join our infrastructure team to manage Kubernetes clusters, Terraform scripts, AWS infrastructure, and CI/CD pipelines with GitHub Actions.",
        "salary": "$130,000 - $160,000 / year",
        "experience": "4+ years",
        "job_type": "Remote",
        "skills": ["Docker", "Kubernetes", "AWS", "Terraform", "Python", "Git"],
        "url": "https://example.com/jobs/devops-cloudscale",
        "source": "DEMO DATA (Sample listing)",
        "date_posted": "5 days ago",
        "is_demo": True
    }
]

class JobSearchManager:
    """
    Coordinates job searches across configured live job sources (Apify) and demo fallback.
    """

    def __init__(self, apify_token: Optional[str] = None):
        self.apify_client = ApifyJobClient(api_token=apify_token)

    def is_live_configured(self) -> bool:
        """Returns True if at least one live job API source is configured."""
        return self.apify_client.is_configured()

    def search(
        self,
        queries: List[str],
        location: str = "",
        max_results_per_query: int = 5,
        use_demo_if_unconfigured: bool = True
    ) -> Dict[str, Any]:
        """
        Performs concurrent job searches across queries using configured sources.
        
        Returns:
        {
            "live_configured": bool,
            "jobs": list[dict],
            "sources_used": list[str],
            "message": str
        }
        """
        all_raw_jobs = []
        sources_used = []
        is_live = self.is_live_configured()

        if is_live:
            sources_used.append("Apify Live Job Scraper")
            # Concurrent execution across query variations
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(queries))) as executor:
                future_to_query = {
                    executor.submit(self.apify_client.search_jobs, q, location, max_results_per_query): q
                    for q in queries
                }
                for future in concurrent.futures.as_completed(future_to_query):
                    query = future_to_query[future]
                    try:
                        results = future.result()
                        for item in results:
                            normalized = normalize_job(item, source_name="Apify Live Source", is_demo=False)
                            all_raw_jobs.append(normalized)
                    except Exception as e:
                        print(f"[JobSearchManager Error] Query '{query}' failed: {e}")

            message = f"Found {len(all_raw_jobs)} live job listings via Apify."

            # Keep the workflow useful when an actor returns no items because of
            # an invalid token, actor input mismatch, or temporary API issue.
            if not all_raw_jobs and use_demo_if_unconfigured:
                sources_used.append("DEMO DATA (Fallback after empty live response)")
                for demo_job in DEMO_JOB_DATABASE:
                    all_raw_jobs.append(normalize_job(demo_job, source_name="DEMO DATA", is_demo=True))
                error_detail = self.apify_client.last_error
                message = (
                    "Apify returned no job listings. Displaying demo listings so the "
                    "matching workflow can still be tested."
                )
                if error_detail:
                    message += f" Apify error: {error_detail}"
        else:
            message = "Live job search is not configured."
            if use_demo_if_unconfigured:
                sources_used.append("DEMO DATA (Fallback Mode)")
                for demo_job in DEMO_JOB_DATABASE:
                    all_raw_jobs.append(normalize_job(demo_job, source_name="DEMO DATA", is_demo=True))
                message += " Displaying demo listings for testing."

        # Remove obvious duplicates across sources & queries
        unique_jobs = deduplicate_jobs(all_raw_jobs)

        return {
            "live_configured": is_live,
            "jobs": unique_jobs,
            "sources_used": sources_used,
            "message": message
        }
