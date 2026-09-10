from typing import Dict, Any, List, Union, BinaryIO, Optional
from agent.state import AgentState, AgentStateMachine
from agent.tools import AgentTools
from llm.client import LLMClient
from jobs.job_search import JobSearchManager
from memory.memory import UserPreferenceMemory

class JobSearchAgent:
    """
    Core AI Job Search Agent orchestrator.
    
    Demonstrates fundamental AI Agent architecture:
    - Environment: Internet + Job APIs + User Resume + User Preferences
    - Perception: PDF parsing + Candidate text & input comprehension
    - Reasoning: LLM skill extraction & match rationale
    - Planning: Formulate search query strategy
    - Tool Usage: Resume Parser Tool, LLM Tool, Apify Job Search Tool, Matcher & Ranker Tools
    - Action: Querying Apify / external job sources
    - Observation: Raw job payload ingestion, normalization & deduplication
    - Decision Making: Scoring, filtering, ranking recommendations to meet Goal
    """

    def __init__(self, openai_api_key: Optional[str] = None, apify_token: Optional[str] = None):
        self.llm_client = LLMClient(api_key=openai_api_key)
        self.job_manager = JobSearchManager(apify_token=apify_token)
        self.tools = AgentTools(llm_client=self.llm_client, job_manager=self.job_manager)
        self.state_machine = AgentStateMachine()
        self.memory = UserPreferenceMemory()

        self.resume_text: str = ""
        self.candidate_profile: Dict[str, Any] = {}
        self.search_plan: List[str] = []
        self.raw_jobs: List[Dict[str, Any]] = []
        self.matched_jobs: List[Dict[str, Any]] = []
        self.ranked_jobs: List[Dict[str, Any]] = []
        self.search_metadata: Dict[str, Any] = {}

    def run_pipeline(
        self,
        resume_source: Union[str, bytes, BinaryIO],
        user_preferences: Dict[str, Any],
        sort_by: str = "Best match",
        min_score: int = 0
    ) -> Dict[str, Any]:
        """
        Executes the complete end-to-end AI Agent pipeline.
        """
        self.state_machine.reset()

        try:
            # 1. Perception & Resume Extraction
            self.state_machine.set_state(AgentState.RESUME_UPLOADED, "Resume received into Environment.")
            self.state_machine.set_state(AgentState.RESUME_PARSED, "Perception: Extracting text from PDF resume via PyMuPDF tool...")
            
            self.resume_text = self.tools.parse_resume_tool(resume_source)
            if not self.resume_text:
                raise ValueError("Resume text extraction yielded empty content.")

            # 2. Perception & Reasoning (Profile Generation)
            self.state_machine.set_state(AgentState.PROFILE_CREATED, "Reasoning: LLM analyzing candidate skills, tech stack, and experience...")
            self.candidate_profile = self.tools.extract_profile_tool(self.resume_text)

            # Persist safe preferences to Memory
            merged_prefs = {
                "preferred_role": user_preferences.get("preferred_role") or (self.candidate_profile.get("preferred_roles", [""])[0] if self.candidate_profile.get("preferred_roles") else ""),
                "location": user_preferences.get("location") or "",
                "job_type": user_preferences.get("job_type", "Any"),
                "experience_level": user_preferences.get("experience_level") or self.candidate_profile.get("experience_level", "Any")
            }
            self.memory.save_preferences(merged_prefs)

            # 3. Planning (Query strategy generation)
            self.state_machine.set_state(AgentState.PLANNING_SEARCH, "Planning: Agent formulating high-yield search query strategy...")
            self.search_plan = self.tools.plan_search_queries_tool(self.candidate_profile, user_preferences)

            # 4. Action & Tool Usage (Job Search)
            self.state_machine.set_state(AgentState.SEARCHING_JOBS, f"Action & Tool Usage: Searching job sources using queries {self.search_plan}...")
            search_result = self.tools.search_jobs_tool(
                queries=self.search_plan,
                location=user_preferences.get("location", ""),
                max_results=user_preferences.get("max_jobs", 5)
            )

            # 5. Observation
            self.state_machine.set_state(AgentState.JOBS_RECEIVED, f"Observation: Received job listings. {search_result.get('message')}")
            self.raw_jobs = search_result.get("jobs", [])
            self.search_metadata = {
                "live_configured": search_result.get("live_configured", False),
                "sources_used": search_result.get("sources_used", []),
                "message": search_result.get("message", "")
            }

            # 6. Decision Making: Matching
            self.state_machine.set_state(AgentState.MATCHING, "Decision Making: Evaluating job requirements against candidate profile...")
            self.matched_jobs = []
            for job in self.raw_jobs:
                match_eval = self.tools.match_job_tool(self.candidate_profile, job, user_preferences)
                self.matched_jobs.append({
                    **job,
                    "match": match_eval
                })

            # 7. Decision Making: Ranking
            self.state_machine.set_state(AgentState.RANKING, "Decision Making: Ranking opportunities from highest relevance score...")
            self.ranked_jobs = self.tools.rank_jobs_tool(
                jobs_with_matches=self.matched_jobs,
                sort_by=sort_by,
                min_score=min_score,
                filter_remote_only=(user_preferences.get("job_type") == "Remote Only"),
                location_filter=user_preferences.get("location_filter", "")
            )

            self.state_machine.set_state(AgentState.COMPLETED, f"Goal Achieved: Successfully produced {len(self.ranked_jobs)} job recommendations!")

            return {
                "success": True,
                "profile": self.candidate_profile,
                "resume_text": self.resume_text,
                "search_plan": self.search_plan,
                "jobs": self.ranked_jobs,
                "metadata": self.search_metadata,
                "history": self.state_machine.get_history()
            }

        except Exception as e:
            error_msg = f"Pipeline execution failed: {str(e)}"
            self.state_machine.set_state(AgentState.FAILED, error_msg)
            return {
                "success": False,
                "error": error_msg,
                "history": self.state_machine.get_history()
            }
