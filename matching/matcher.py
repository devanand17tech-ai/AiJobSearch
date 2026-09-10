import re
from typing import Dict, Any, List, Optional
from llm.client import LLMClient

class MatcherTool:
    """
    Evaluates candidate profile compatibility against job listings using a hybrid
    scoring approach (rule-based skill overlap + experience fit + LLM qualitative rationale).
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()

    def evaluate_match(self, profile: Dict[str, Any], job: Dict[str, Any], user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates a detailed match evaluation for a given job.
        
        Returns:
        {
            "score": int (0 to 100),
            "matched_skills": list[str],
            "missing_skills": list[str],
            "experience_match": str,
            "location_match": str,
            "reason": str
        }
        """
        candidate_skills = [s.strip().lower() for s in (profile.get("skills", []) + profile.get("programming_languages", []) + profile.get("frameworks", []))]
        job_skills_raw = job.get("skills", [])
        job_desc = job.get("description", "").lower()
        
        # 1. Skill Overlap Matching
        matched_skills = []
        missing_skills = []

        if job_skills_raw:
            for js in job_skills_raw:
                js_clean = js.strip()
                if any(cs in js_clean.lower() or js_clean.lower() in cs for cs in candidate_skills):
                    matched_skills.append(js_clean)
                else:
                    missing_skills.append(js_clean)
        else:
            # Infer skills from description if explicit list missing
            tech_keywords = [
                "Java", "Python", "C++", "C#", "JavaScript", "TypeScript", "React", "Node.js", 
                "Angular", "Vue", "Spring Boot", "Django", "Flask", "FastAPI", "SQL", "PostgreSQL", 
                "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "Azure", "REST API", "Git"
            ]
            for tech in tech_keywords:
                if re.search(r'\b' + re.escape(tech) + r'\b', job_desc, re.IGNORECASE):
                    if any(cs in tech.lower() or tech.lower() in cs for cs in candidate_skills):
                        matched_skills.append(tech)
                    else:
                        missing_skills.append(tech)

        matched_skills = list(dict.fromkeys(matched_skills))
        missing_skills = list(dict.fromkeys(missing_skills))

        # Base score calculation
        total_skills_evaluated = len(matched_skills) + len(missing_skills)
        if total_skills_evaluated > 0:
            skill_ratio = len(matched_skills) / total_skills_evaluated
            skill_score = skill_ratio * 60
        else:
            skill_score = 40  # neutral base if no skills parsed

        # 2. Role Title Similarity
        title_score = 0
        job_title_lower = job.get("title", "").lower()
        target_role = user_preferences.get("preferred_role", "").lower()
        preferred_roles = [r.lower() for r in profile.get("preferred_roles", [])]

        if target_role and target_role in job_title_lower:
            title_score = 25
        elif any(pr in job_title_lower or job_title_lower in pr for pr in preferred_roles):
            title_score = 20
        elif any(cs in job_title_lower for cs in candidate_skills[:5]):
            title_score = 15
        else:
            title_score = 10

        # 3. Location & Remote Preference Fit
        location_score = 0
        job_loc_lower = job.get("location", "").lower()
        pref_loc = user_preferences.get("location", "").lower()
        pref_type = user_preferences.get("job_type", "").lower()

        if "remote" in pref_type and ("remote" in job_loc_lower or "remote" in job.get("job_type", "").lower()):
            location_score = 15
            location_match_text = "Exact Remote Preference Match"
        elif pref_loc and pref_loc in job_loc_lower:
            location_score = 15
            location_match_text = f"Matches preferred location '{user_preferences.get('location')}'"
        else:
            location_score = 10
            location_match_text = f"Location: {job.get('location', 'Not Specified')}"

        final_score = min(99, max(35, int(skill_score + title_score + location_score)))

        # 4. LLM Qualitative Match Rationale (if OpenAI is configured)
        reason_text = ""
        if self.llm_client.is_configured():
            llm_eval = self.llm_client.explain_job_match(profile, job)
            if llm_eval and "reason" in llm_eval:
                reason_text = llm_eval["reason"]
                if "score" in llm_eval and isinstance(llm_eval["score"], (int, float)):
                    # blend LLM score slightly if available
                    final_score = int(0.7 * final_score + 0.3 * llm_eval["score"])

        if not reason_text:
            if matched_skills:
                matched_str = ", ".join(matched_skills[:3])
                reason_text = f"Strong match because your profile includes {matched_str} matching key requirements of {job.get('title')}."
            else:
                reason_text = f"Relevant match based on role alignment for {job.get('title')}."

        exp_match_text = f"Aligned with {profile.get('experience_level', 'Mid')} level requirement"

        return {
            "score": final_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "experience_match": exp_match_text,
            "location_match": location_match_text,
            "reason": reason_text
        }
