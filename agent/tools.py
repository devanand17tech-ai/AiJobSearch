from typing import Dict, Any, List, Union, BinaryIO
from resume.parser import extract_text_from_pdf
from llm.client import LLMClient
from jobs.job_search import JobSearchManager
from matching.matcher import MatcherTool
from matching.ranker import RankerTool

class AgentTools:
    """
    Tool registry providing standardized tool interfaces for the AI Job Search Agent.
    """

    def __init__(self, llm_client: LLMClient, job_manager: JobSearchManager):
        self.llm_client = llm_client
        self.job_manager = job_manager
        self.matcher = MatcherTool(llm_client=llm_client)
        self.ranker = RankerTool()

    def parse_resume_tool(self, source: Union[str, bytes, BinaryIO]) -> str:
        """Tool: Extract raw text from PDF resume."""
        return extract_text_from_pdf(source)

    def extract_profile_tool(self, resume_text: str) -> Dict[str, Any]:
        """Tool: LLM candidate profile structuring."""
        return self.llm_client.parse_candidate_profile(resume_text)

    def plan_search_queries_tool(self, profile: Dict[str, Any], user_prefs: Dict[str, Any]) -> List[str]:
        """Tool: LLM query strategy generation."""
        return self.llm_client.generate_job_search_queries(profile, user_prefs)

    def search_jobs_tool(self, queries: List[str], location: str, max_results: int) -> Dict[str, Any]:
        """Tool: Execute external live job search or demo fallback."""
        return self.job_manager.search(queries=queries, location=location, max_results_per_query=max_results)

    def match_job_tool(self, profile: Dict[str, Any], job: Dict[str, Any], user_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Tool: Match score evaluation."""
        return self.matcher.evaluate_match(profile, job, user_prefs)

    def rank_jobs_tool(
        self,
        jobs_with_matches: List[Dict[str, Any]],
        sort_by: str = "Best match",
        min_score: int = 0,
        filter_remote_only: bool = False,
        location_filter: str = ""
    ) -> List[Dict[str, Any]]:
        """Tool: Rank and filter job list."""
        return self.ranker.rank_jobs(
            jobs_with_matches=jobs_with_matches,
            sort_by=sort_by,
            min_score=min_score,
            filter_remote_only=filter_remote_only,
            location_filter=location_filter
        )
