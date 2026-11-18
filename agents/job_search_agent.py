"""
Agent 2: Job Search Agent
Generates intelligent queries and searches live job sources (Apify) or fallback demo jobs.
"""
import os
import json
import re
from typing import List, Dict, Any, Optional

from models.schemas import CandidateProfile, RawJobListing
from tools.apify_tool import execute_job_search
from prompts.search_prompt import SEARCH_QUERY_SYSTEM_PROMPT, SEARCH_QUERY_USER_PROMPT

class JobSearchAgent:
    """
    Specialist agent responsible for job query generation and job discovery via Apify.
    """

    def __init__(self, openai_api_key: Optional[str] = None, apify_token: Optional[str] = None, model: Optional[str] = None):
        self.api_key = (openai_api_key or os.getenv("OPENAI_API_KEY", "")).strip()
        self.apify_token = (apify_token or os.getenv("APIFY_API_TOKEN", "")).strip()
        self.model = (model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")).strip()
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"[JobSearchAgent] OpenAI client init failed: {e}")

    def is_llm_configured(self) -> bool:
        return bool(self.api_key and self.client is not None and len(self.api_key) > 5)

    def plan_search_queries(self, profile: CandidateProfile, user_preferences: Dict[str, Any]) -> List[str]:
        """
        Formulates high-yield search queries tailored to profile and preferences.
        """
        role_override = user_preferences.get("preferred_role", "").strip()
        location = user_preferences.get("location", "").strip()
        job_type = user_preferences.get("job_type", "").strip()

        # Try LLM query formulation
        if self.is_llm_configured():
            try:
                prompt = SEARCH_QUERY_USER_PROMPT.format(
                    name=profile.name,
                    skills=", ".join(profile.technical_skills[:8]),
                    languages=", ".join(profile.programming_languages[:6]),
                    frameworks=", ".join(profile.frameworks[:6]),
                    graduation_year=profile.graduation_year or "Not specified",
                    total_experience=profile.total_years_experience,
                    experience_level=profile.experience_level,
                    target_roles=", ".join(profile.target_roles[:4]),
                    role_override=role_override or "None",
                    location=location or "Any",
                    job_type=job_type or "Any"
                )
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SEARCH_QUERY_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                content = response.choices[0].message.content.strip()
                if content.startswith("```"):
                    content = re.sub(r"^```[a-z]*\n?", "", content)
                    content = re.sub(r"\n?```$", "", content)
                queries = json.loads(content)
                if isinstance(queries, list) and queries:
                    return [q.strip() for q in queries if isinstance(q, str)][:5]
            except Exception as e:
                print(f"[JobSearchAgent Warning] LLM query planning failed: {e}. Using intelligent fallback.")

        # Heuristic query planning
        queries = []
        is_fresher = (
            profile.total_years_experience <= 1.0 or
            "entry" in profile.experience_level.lower() or
            "junior" in profile.experience_level.lower()
        )

        if role_override:
            queries.append(role_override)
            if is_fresher and "fresher" not in role_override.lower() and "junior" not in role_override.lower():
                queries.append(f"{role_override} Fresher")

        for role in profile.target_roles:
            if role and role not in queries:
                queries.append(role)
                if is_fresher and len(queries) < 5:
                    queries.append(f"Junior {role}")

        # Tech-stack based queries
        if profile.programming_languages:
            primary_lang = profile.programming_languages[0]
            if profile.frameworks:
                queries.append(f"{primary_lang} {profile.frameworks[0]} Developer")
            else:
                queries.append(f"{primary_lang} Developer")

        if not queries:
            queries = ["Software Engineer", "Backend Developer", "Full Stack Developer"]

        # Deduplicate while preserving order
        unique_queries = list(dict.fromkeys(queries))
        return unique_queries[:5]

    def search_jobs(
        self,
        queries: List[str],
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes search using Apify tool or fallback demo database.
        
        Returns:
        {
            "raw_jobs": List[RawJobListing],
            "metadata": Dict[str, Any]
        }
        """
        location = user_preferences.get("location", "")
        max_results = user_preferences.get("max_jobs", 5)

        return execute_job_search(
            queries=queries,
            location=location,
            max_results_per_query=max_results,
            apify_token=self.apify_token
        )
