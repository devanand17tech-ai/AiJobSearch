"""
Agent 4: Job Matching Agent
Evaluates candidate compatibility against verified job listings using transparent multi-factor scoring.
"""
import os
import json
import re
from typing import List, Dict, Any, Optional

from models.schemas import CandidateProfile, VerifiedJob, MatchedJob, EligibilityStatus
from prompts.matching_prompt import MATCHING_SYSTEM_PROMPT, MATCHING_USER_PROMPT

class JobMatchingAgent:
    """
    Specialist agent responsible for transparent resume-job compatibility evaluation.
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
                print(f"[JobMatchingAgent] OpenAI client init failed: {e}")

    def is_llm_configured(self) -> bool:
        return bool(self.api_key and self.client is not None and len(self.api_key) > 5)

    def match_jobs(
        self,
        profile: CandidateProfile,
        verified_jobs: List[VerifiedJob],
        user_preferences: Dict[str, Any]
    ) -> List[MatchedJob]:
        """
        Evaluates and ranks verified job opportunities against candidate profile.
        """
        matched_results: List[MatchedJob] = []

        for v_job in verified_jobs:
            # Skip duplicates from match output
            if v_job.is_duplicate:
                continue

            match_data = self._evaluate_single_match(profile, v_job, user_preferences)
            matched_results.append(match_data)

        # Sort descending by match score
        matched_results.sort(key=lambda m: m.match_score, reverse=True)
        return matched_results

    def _evaluate_single_match(
        self,
        profile: CandidateProfile,
        v_job: VerifiedJob,
        user_preferences: Dict[str, Any]
    ) -> MatchedJob:
        """Calculates transparent multi-factor compatibility score and eligibility."""
        candidate_skills = [s.strip().lower() for s in profile.all_skills]
        job_skills = v_job.skills or []
        job_desc = v_job.description.lower()

        # 1. Skill Overlap Analysis
        matched_skills = []
        missing_skills = []

        all_eval_skills = list(job_skills)
        if not all_eval_skills:
            common_tech = [
                "Java", "Python", "C++", "C#", "JavaScript", "TypeScript", "React", "Node.js",
                "Angular", "Vue", "Spring Boot", "Django", "Flask", "FastAPI", "SQL", "PostgreSQL",
                "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "Azure", "Git", "REST API"
            ]
            for tech in common_tech:
                if re.search(r'\b' + re.escape(tech) + r'\b', job_desc, re.IGNORECASE):
                    all_eval_skills.append(tech)

        for js in all_eval_skills:
            js_clean = js.strip()
            if any(cs in js_clean.lower() or js_clean.lower() in cs for cs in candidate_skills):
                if js_clean not in matched_skills:
                    matched_skills.append(js_clean)
            else:
                if js_clean not in missing_skills:
                    missing_skills.append(js_clean)

        total_skills = len(matched_skills) + len(missing_skills)
        if total_skills > 0:
            skill_ratio = len(matched_skills) / total_skills
            skill_score = int(round(skill_ratio * 50))
        else:
            skill_score = 30  # baseline if no explicit skills extracted

        # 2. Experience Alignment (0-20 pts)
        cand_exp = profile.total_years_experience
        min_req = v_job.min_experience_years
        max_req = v_job.max_experience_years

        exp_reasons = []
        if min_req == 0.0:
            exp_score = 20
            exp_reasons.append("Open to entry-level / freshers; experience requirement fully met.")
        elif cand_exp >= min_req:
            if max_req and cand_exp > (max_req + 2.0):
                exp_score = 15  # slightly overqualified
                exp_reasons.append(f"Candidate ({cand_exp} yrs) slightly exceeds upper target ({max_req} yrs).")
            else:
                exp_score = 20
                exp_reasons.append(f"Candidate experience ({cand_exp} yrs) meets minimum requirement ({min_req} yrs).")
        else:
            diff = min_req - cand_exp
            if diff <= 1.0:
                exp_score = 12
                exp_reasons.append(f"Candidate has {cand_exp} yrs against {min_req} yrs required (marginal gap).")
            else:
                exp_score = 5
                exp_reasons.append(f"Candidate has {cand_exp} yrs but job requires {min_req} yrs minimum.")

        # 3. Role Title Alignment (0-15 pts)
        job_title_lower = v_job.title.lower()
        pref_role = user_preferences.get("preferred_role", "").lower()
        target_roles = [r.lower() for r in profile.target_roles]

        title_score = 0
        if pref_role and pref_role in job_title_lower:
            title_score = 15
        elif any(tr in job_title_lower or job_title_lower in tr for tr in target_roles):
            title_score = 13
        elif any(cs in job_title_lower for cs in candidate_skills[:4]):
            title_score = 10
        else:
            title_score = 6

        # 4. Location & Workplace Fit (0-15 pts)
        loc_score = 0
        job_loc_lower = v_job.location.lower()
        pref_loc = user_preferences.get("location", "").lower()
        pref_workplace = user_preferences.get("job_type", "").lower()

        if "remote" in pref_workplace and ("remote" in job_loc_lower or "remote" in v_job.job_type.lower()):
            loc_score = 15
        elif pref_loc and pref_loc in job_loc_lower:
            loc_score = 15
        elif not pref_loc or pref_loc == "any":
            loc_score = 12
        else:
            loc_score = 8

        # 5. Graduation Year Restrictions & Eligibility Evaluation
        eligibility = EligibilityStatus.ELIGIBLE
        eligibility_reasons = list(exp_reasons)

        if v_job.graduation_years_accepted and profile.graduation_year:
            if profile.graduation_year in v_job.graduation_years_accepted:
                eligibility_reasons.append(f"Graduation year ({profile.graduation_year}) matches accepted batch ({v_job.graduation_years_accepted}).")
            else:
                eligibility = EligibilityStatus.INELIGIBLE
                eligibility_reasons.append(f"Graduation year ({profile.graduation_year}) outside accepted batches: {v_job.graduation_years_accepted}.")

        if cand_exp < (min_req - 1.5):
            eligibility = EligibilityStatus.INELIGIBLE
            eligibility_reasons.append("Significant experience deficit relative to minimum requirement.")
        elif cand_exp < min_req and eligibility != EligibilityStatus.INELIGIBLE:
            eligibility = EligibilityStatus.MARGINAL

        # Calculate total match score
        total_score = min(99, max(30, skill_score + exp_score + title_score + loc_score))

        # Adjust score if ineligible
        if eligibility == EligibilityStatus.INELIGIBLE:
            total_score = min(50, total_score)

        # 6. Qualitative Match Explanation
        explanation = ""
        if self.is_llm_configured():
            try:
                prompt = MATCHING_USER_PROMPT.format(
                    candidate_name=profile.name,
                    skills=", ".join(profile.technical_skills),
                    languages=", ".join(profile.programming_languages),
                    frameworks_databases=", ".join(profile.frameworks + profile.databases),
                    graduation_year=profile.graduation_year or "Not specified",
                    total_experience=profile.total_years_experience,
                    experience_level=profile.experience_level,
                    target_roles=", ".join(profile.target_roles),
                    job_title=v_job.title,
                    company=v_job.company,
                    job_location=v_job.location,
                    experience_required=v_job.raw_job.experience,
                    min_exp=v_job.min_experience_years,
                    accepted_grad_years=v_job.graduation_years_accepted or "Any",
                    job_skills=", ".join(v_job.skills),
                    job_description=v_job.description[:1200]
                )
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": MATCHING_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                llm_eval = json.loads(response.choices[0].message.content.strip())
                explanation = llm_eval.get("match_explanation") or llm_eval.get("reason", "")
                if "eligibility_status" in llm_eval:
                    es_val = llm_eval["eligibility_status"].capitalize()
                    if es_val in ["Eligible", "Marginal", "Ineligible"]:
                        eligibility = EligibilityStatus(es_val)
                if llm_eval.get("eligibility_reasons"):
                    for er in llm_eval["eligibility_reasons"]:
                        if er not in eligibility_reasons:
                            eligibility_reasons.append(er)
            except Exception as e:
                print(f"[JobMatchingAgent Warning] LLM matching failed: {e}. Using deterministic explanation.")

        if not explanation:
            if matched_skills:
                explanation = f"Solid fit ({total_score}%) with strong alignment on {', '.join(matched_skills[:3])}. {exp_reasons[0]}"
            else:
                explanation = f"Opportunity matches role category '{v_job.title}' with {total_score}% overall compatibility."

        return MatchedJob(
            verified_job=v_job,
            match_score=total_score,
            skill_score=skill_score,
            experience_score=exp_score,
            title_score=title_score,
            location_score=loc_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            eligibility_status=eligibility,
            eligibility_reasons=eligibility_reasons,
            match_explanation=explanation
        )
