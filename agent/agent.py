"""
Backward-compatible wrapper for the legacy JobSearchAgent interface,
powered by the new MultiAgentOrchestrator and specialist agents.
"""
from typing import Dict, Any, List, Union, BinaryIO, Optional
from agents.orchestrator import MultiAgentOrchestrator
from memory.memory import UserPreferenceMemory

class JobSearchAgent:
    """
    Unified entry point maintaining backward compatibility with existing single-agent callers,
    powered internally by the 6-agent Multi-Agent Architecture.
    """

    def __init__(self, openai_api_key: Optional[str] = None, apify_token: Optional[str] = None):
        self.orchestrator = MultiAgentOrchestrator(
            openai_api_key=openai_api_key,
            apify_token=apify_token
        )
        self.memory = UserPreferenceMemory()

    def run_pipeline(
        self,
        resume_source: Union[str, bytes, BinaryIO],
        user_preferences: Dict[str, Any],
        sort_by: str = "Best match",
        min_score: int = 0
    ) -> Dict[str, Any]:
        """
        Executes the multi-agent pipeline and formats the response for backward and forward compatibility.
        """
        raw_result = self.orchestrator.run(
            resume_source=resume_source,
            user_preferences=user_preferences,
            sort_by=sort_by,
            min_score=min_score
        )

        candidate_profile = raw_result.get("candidate_profile")
        profile_dict = candidate_profile.model_dump() if candidate_profile else {}
        if profile_dict:
            # Ensure backward-compatible keys
            profile_dict["skills"] = candidate_profile.all_skills
            profile_dict["preferred_roles"] = profile_dict.get("target_roles", [])

        # Save safe preferences to memory
        if profile_dict:
            merged_prefs = {
                "preferred_role": user_preferences.get("preferred_role") or (profile_dict.get("target_roles", [""])[0] if profile_dict.get("target_roles") else ""),
                "location": user_preferences.get("location") or "",
                "job_type": user_preferences.get("job_type", "Any"),
                "experience_level": user_preferences.get("experience_level") or profile_dict.get("experience_level", "Any")
            }
            self.memory.save_preferences(merged_prefs)

        # Format legacy jobs structure for existing frontend components
        matched_jobs = raw_result.get("matched_jobs", [])
        legacy_jobs = []
        for mj in matched_jobs:
            job_dict = {
                "title": mj.title,
                "company": mj.company,
                "location": mj.location,
                "description": mj.description,
                "salary": mj.salary,
                "experience": mj.verified_job.raw_job.experience,
                "job_type": mj.job_type,
                "skills": mj.skills,
                "url": mj.url,
                "source": mj.source,
                "date_posted": mj.date_posted,
                "is_demo": mj.is_demo,
                "match": {
                    "score": mj.match_score,
                    "matched_skills": mj.matched_skills,
                    "missing_skills": mj.missing_skills,
                    "experience_match": ", ".join(mj.eligibility_reasons[:1]) if mj.eligibility_reasons else "Aligned",
                    "location_match": f"Location: {mj.location}",
                    "reason": mj.match_explanation,
                    "eligibility_status": mj.eligibility_status.value
                },
                "verified": {
                    "status": mj.verification_status.value,
                    "flags": mj.verification_flags,
                    "criteria": mj.verified_job.eligibility_criteria,
                    "min_exp": mj.verified_job.min_experience_years,
                    "deadline": mj.verified_job.application_deadline
                }
            }
            legacy_jobs.append(job_dict)

        # Format execution history for legacy UI
        execution_logs = raw_result.get("execution_logs", [])
        legacy_history = [
            {
                "state": log.agent_name.upper().replace(" ", "_"),
                "message": log.message,
                "timestamp": log.timestamp,
                "status": log.status
            }
            for log in execution_logs
        ]

        career_advice = raw_result.get("career_advice")

        return {
            "success": raw_result.get("success", True),
            "profile": profile_dict,
            "candidate_profile": candidate_profile,
            "resume_text": raw_result.get("resume_text", ""),
            "search_plan": raw_result.get("search_queries", []),
            "jobs": legacy_jobs,
            "matched_jobs": matched_jobs,
            "verified_jobs": raw_result.get("verified_jobs", []),
            "verification_summary": raw_result.get("verification_summary", {}),
            "career_advice": career_advice,
            "metadata": raw_result.get("search_metadata", {}),
            "history": legacy_history,
            "execution_logs": execution_logs,
            "errors": raw_result.get("errors", [])
        }
