import re
from typing import Dict, Any, List

def normalize_job(raw_job: Dict[str, Any], source_name: str = "Apify Job Source", is_demo: bool = False) -> Dict[str, Any]:
    """
    Normalizes job data from various source schemas into a single standard job structure.
    
    Standard Schema:
    {
        "title": str,
        "company": str,
        "location": str,
        "description": str,
        "salary": str,
        "experience": str,
        "job_type": str,
        "skills": list[str],
        "url": str,
        "source": str,
        "date_posted": str,
        "is_demo": bool
    }
    """
    # Extract Title
    title = (
        raw_job.get("title") or 
        raw_job.get("positionName") or 
        raw_job.get("jobTitle") or 
        raw_job.get("header", {}).get("title") or 
        "Job Title Not Specified"
    ).strip()

    # Extract Company
    company = (
        raw_job.get("company") or 
        raw_job.get("companyName") or 
        raw_job.get("employerName") or 
        raw_job.get("organization") or 
        "Company Confidential"
    ).strip()

    # Extract Location
    location = (
        raw_job.get("location") or 
        raw_job.get("jobLocation") or 
        raw_job.get("city") or 
        raw_job.get("formattedLocation") or 
        "Location Not Specified"
    ).strip()

    # Extract Description
    description = (
        raw_job.get("description") or 
        raw_job.get("snippet") or 
        raw_job.get("jobDescription") or 
        raw_job.get("summary") or 
        ""
    ).strip()

    # Extract Salary
    salary = (
        raw_job.get("salary") or 
        raw_job.get("salarySnippet") or 
        raw_job.get("pay") or 
        raw_job.get("estimatedSalary") or 
        "Not Specified"
    )
    if isinstance(salary, dict):
        salary = salary.get("text") or salary.get("formatted") or "Not Specified"
    salary = str(salary).strip()

    # Extract Experience
    experience = (
        raw_job.get("experience") or 
        raw_job.get("experienceLevel") or 
        raw_job.get("seniorityLevel") or 
        "Not Specified"
    ).strip()

    # Extract Job Type (Full-time, Remote, etc.)
    job_type = (
        raw_job.get("job_type") or 
        raw_job.get("jobType") or 
        raw_job.get("employmentType") or 
        raw_job.get("workplaceType") or 
        "Full-Time"
    )
    if isinstance(job_type, list):
        job_type = ", ".join(str(item) for item in job_type)
    job_type = str(job_type).strip()

    # Extract Skills
    skills = raw_job.get("skills") or raw_job.get("technologies") or raw_job.get("keywords") or []
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    elif not isinstance(skills, list):
        skills = []
        
    # Heuristic skill extraction from description if empty
    if not skills and description:
        tech_keywords = [
            "Java", "Python", "C++", "C#", "JavaScript", "TypeScript", "React", "Node.js", 
            "Angular", "Vue", "Spring Boot", "Django", "Flask", "FastAPI", "SQL", "PostgreSQL", 
            "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "REST API", "Git"
        ]
        skills = [kw for kw in tech_keywords if re.search(r'\b' + re.escape(kw) + r'\b', description, re.IGNORECASE)]

    # Extract Apply URL
    url = (
        raw_job.get("url") or 
        raw_job.get("jobUrl") or 
        raw_job.get("applyUrl") or 
        raw_job.get("link") or 
        raw_job.get("externalApplyLink") or 
        "#"
    ).strip()

    # Extract Date Posted
    date_posted = (
        raw_job.get("date_posted") or 
        raw_job.get("postedAt") or 
        raw_job.get("postedDate") or 
        raw_job.get("publicationDate") or 
        "Recently Posted"
    ).strip()

    source = raw_job.get("source") or source_name

    return {
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "salary": salary,
        "experience": experience,
        "job_type": job_type,
        "skills": list(set(skills)),
        "url": url,
        "source": source,
        "date_posted": date_posted,
        "is_demo": is_demo or raw_job.get("is_demo", False)
    }

def deduplicate_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicates a list of normalized job dictionaries using URL and composite (Title + Company + Location).
    """
    seen_urls = set()
    seen_composites = set()
    unique_jobs = []

    for job in jobs:
        url = job.get("url", "").strip().lower()
        title = job.get("title", "").strip().lower()
        company = job.get("company", "").strip().lower()
        location = job.get("location", "").strip().lower()

        # Composite key for deduplication
        composite = f"{title}|{company}|{location}"

        # Skip if valid URL seen before
        if url and url != "#" and url in seen_urls:
            continue
        
        # Skip if exact same title, company, and location seen before
        if composite in seen_composites:
            continue

        if url and url != "#":
            seen_urls.add(url)
        seen_composites.add(composite)
        
        unique_jobs.append(job)

    return unique_jobs
