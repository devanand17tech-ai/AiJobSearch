"""
Agent 5: Career Advisor Agent
Synthesizes verified and matched listings to provide strategic, prioritized career advice.
"""
import os
import json
from collections import Counter
from typing import List, Dict, Any, Optional

from models.schemas import (
    CandidateProfile,
    MatchedJob,
    CareerAdvice,
    JobPriorityRecommendation,
    SkillGapAnalysis,
    EligibilityStatus
)
from prompts.advisor_prompt import CAREER_ADVISOR_SYSTEM_PROMPT, CAREER_ADVISOR_USER_PROMPT

class CareerAdvisorAgent:
    """
    Specialist agent that analyzes market matches and formulates actionable career guidance.
    """

    def __init__(self, openai_api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = (openai_api_key or os.getenv("OPENAI_API_KEY", "")).strip()
        self.model = (model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")).strip()
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"[CareerAdvisorAgent] OpenAI client init failed: {e}")

    def is_llm_configured(self) -> bool:
        return bool(self.api_key and self.client is not None and len(self.api_key) > 5)

    def formulate_advice(
        self,
        profile: CandidateProfile,
        matched_jobs: List[MatchedJob]
    ) -> CareerAdvice:
        """
        Analyzes matched job listings and generates prioritized career recommendations.
        """
        if not matched_jobs:
            return CareerAdvice(
                priority_applications=[],
                systemic_skill_gaps=[],
                technologies_to_learn=["Docker", "Git", "Cloud Infrastructure (AWS/GCP)"],
                resume_improvements=["Ensure technical projects clearly highlight measurable accomplishments."],
                executive_summary="No matching jobs were found matching your current parameters. Expand your search locations or target role keywords."
            )

        # 1. Deterministic prioritization
        # Filter for eligible or marginal jobs first, sorted by match score
        valid_jobs = [j for j in matched_jobs if j.eligibility_status != EligibilityStatus.INELIGIBLE]
        if not valid_jobs:
            valid_jobs = matched_jobs

        priority_apps: List[JobPriorityRecommendation] = []
        for rank, job in enumerate(valid_jobs[:5], 1):
            urgency = "High" if job.match_score >= 80 else ("Medium" if job.match_score >= 65 else "Normal")
            reason = f"Rank #{rank}: High fit ({job.match_score}%) with matching core stack: {', '.join(job.matched_skills[:3]) or 'General role fit'}."
            priority_apps.append(JobPriorityRecommendation(
                job_id=job.verified_job.raw_job.id,
                title=job.title,
                company=job.company,
                url=job.url,
                match_score=job.match_score,
                priority_rank=rank,
                apply_urgency=urgency,
                reason_to_apply_first=reason
            ))

        # 2. Deterministic Systemic Skill Gap Analysis
        missing_counter = Counter()
        for job in matched_jobs:
            for s in job.missing_skills:
                missing_counter[s] += 1

        skill_gaps: List[SkillGapAnalysis] = []
        tech_to_learn: List[str] = []
        for skill, count in missing_counter.most_common(5):
            importance = "Critical" if count >= 3 else "Recommended"
            learning_rec = f"Frequently required across {count} postings. Build a working demo or integration with {skill}."
            skill_gaps.append(SkillGapAnalysis(
                skill_name=skill,
                demand_frequency=count,
                importance_level=importance,
                learning_recommendation=learning_rec
            ))
            tech_to_learn.append(skill)

        # Baseline resume improvement suggestions
        resume_improvements = [
            f"Tailor your summary to emphasize your top target role: {profile.target_roles[0] if profile.target_roles else 'Software Engineer'}.",
            "Quantify key project achievements (e.g., latency reduction, user throughput, code coverage).",
            f"Explicitly list proficiencies in {', '.join(tech_to_learn[:2]) or 'high-demand tools'} under a Technical Skills section."
        ]

        summary = (
            f"Based on {len(matched_jobs)} evaluated opportunities, your profile demonstrates strong alignment for "
            f"{', '.join(profile.target_roles[:2])}. You have {len(valid_jobs)} viable openings with compatibility scores up to {matched_jobs[0].match_score}%. "
            f"Bridging key gaps in {', '.join(tech_to_learn[:3]) or 'modern tooling'} will further maximize your callback rate."
        )

        # 3. LLM Qualitative Enhancement (if configured)
        if self.is_llm_configured():
            try:
                summaries_text = "\n".join([
                    f"- {j.title} @ {j.company} | Score: {j.match_score}% | Missing: {', '.join(j.missing_skills[:3])} | Eligibility: {j.eligibility_status.value}"
                    for j in matched_jobs[:6]
                ])
                prompt = CAREER_ADVISOR_USER_PROMPT.format(
                    candidate_name=profile.name,
                    skills=", ".join(profile.technical_skills[:8]),
                    tech_stack=", ".join(profile.programming_languages + profile.frameworks),
                    experience_level=profile.experience_level,
                    target_roles=", ".join(profile.target_roles),
                    weak_skills=", ".join(profile.weak_or_missing_skills),
                    job_count=len(matched_jobs),
                    job_summaries=summaries_text
                )
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": CAREER_ADVISOR_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                llm_advice = json.loads(response.choices[0].message.content.strip())

                if llm_advice.get("executive_summary"):
                    summary = llm_advice["executive_summary"]
                if llm_advice.get("resume_improvements"):
                    resume_improvements = llm_advice["resume_improvements"]
                if llm_advice.get("technologies_to_learn"):
                    tech_to_learn = llm_advice["technologies_to_learn"]

                # Enhance priority application reasons
                if llm_advice.get("priority_applications"):
                    for idx, app_dict in enumerate(llm_advice["priority_applications"]):
                        if idx < len(priority_apps) and app_dict.get("reason_to_apply_first"):
                            priority_apps[idx].reason_to_apply_first = app_dict["reason_to_apply_first"]
                            if app_dict.get("apply_urgency"):
                                priority_apps[idx].apply_urgency = app_dict["apply_urgency"]

            except Exception as e:
                print(f"[CareerAdvisorAgent Warning] LLM advice generation failed: {e}. Kept deterministic advice.")

        return CareerAdvice(
            priority_applications=priority_apps,
            systemic_skill_gaps=skill_gaps,
            technologies_to_learn=tech_to_learn,
            resume_improvements=resume_improvements,
            executive_summary=summary
        )
