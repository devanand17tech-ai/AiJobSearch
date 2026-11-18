"""
Apify Search Tool wrapper for live and fallback job discovery.
"""
from typing import List, Dict, Any, Optional
import uuid

from jobs.job_search import JobSearchManager
from models.schemas import RawJobListing

def execute_job_search(
    queries: List[str],
    location: str = "",
    max_results_per_query: int = 5,
    apify_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes job search across provided queries using Apify if configured,
    or falls back to demo job database.
    
    Returns:
    {
        "raw_jobs": List[RawJobListing],
        "metadata": Dict[str, Any]
    }
    """
    manager = JobSearchManager(apify_token=apify_token)
    search_res = manager.search(
        queries=queries,
        location=location,
        max_results_per_query=max_results_per_query
    )

    raw_jobs_list: List[RawJobListing] = []
    for item in search_res.get("jobs", []):
        job_id = str(uuid.uuid4())[:8]
        raw_listing = RawJobListing(
            id=job_id,
            title=item.get("title", "Job Title Not Specified"),
            company=item.get("company", "Company Confidential"),
            location=item.get("location", "Location Not Specified"),
            description=item.get("description", ""),
            salary=item.get("salary", "Not Specified"),
            experience=item.get("experience", "Not Specified"),
            job_type=item.get("job_type", "Full-Time"),
            skills=item.get("skills", []),
            url=item.get("url", "#"),
            source=item.get("source", "Apify"),
            date_posted=item.get("date_posted", "Recently Posted"),
            is_demo=item.get("is_demo", False)
        )
        raw_jobs_list.append(raw_listing)

    metadata = {
        "live_configured": search_res.get("live_configured", False),
        "sources_used": search_res.get("sources_used", []),
        "message": search_res.get("message", "")
    }

    return {
        "raw_jobs": raw_jobs_list,
        "metadata": metadata
    }
