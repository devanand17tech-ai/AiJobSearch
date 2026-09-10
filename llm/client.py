import os
import json
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from openai import OpenAI

from prompts.resume_prompt import RESUME_PARSER_SYSTEM_PROMPT, RESUME_PARSER_USER_PROMPT
from prompts.search_prompt import SEARCH_QUERY_SYSTEM_PROMPT, SEARCH_QUERY_USER_PROMPT
from prompts.matching_prompt import MATCHING_SYSTEM_PROMPT, MATCHING_USER_PROMPT

# Load environment variables from .env if present
load_dotenv()

class LLMClient:
    """
    OpenAI API client wrapper responsible for LLM reasoning tasks:
    - Resume parsing into structured candidate profiles
    - Generating search query variations
    - Evaluating job fit rationale
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "").strip()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        
        self.client = None
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                self.client = None

    def is_configured(self) -> bool:
        """Returns True if OpenAI API key is present."""
        return bool(self.api_key and len(self.api_key) > 5)

    def parse_candidate_profile(self, resume_text: str) -> Dict[str, Any]:
        """
        Parses raw resume text into a structured JSON candidate profile.
        Uses OpenAI LLM when configured, otherwise uses heuristic regex extraction.
        """
        if self.is_configured() and self.client:
            try:
                prompt = RESUME_PARSER_USER_PROMPT.format(resume_text=resume_text[:8000])
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": RESUME_PARSER_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                raw_json = response.choices[0].message.content.strip()
                profile = json.loads(raw_json)
                return self._validate_and_normalize_profile(profile)
            except Exception as e:
                print(f"[LLMClient Warning] LLM parsing failed: {e}. Falling back to heuristic extraction.")

        # Fallback heuristic parser if OpenAI API key is missing or call fails
        return self._heuristic_parse_profile(resume_text)

    def generate_job_search_queries(self, profile: Dict[str, Any], user_preferences: Dict[str, Any]) -> List[str]:
        """
        Generates 3 to 5 targeted search query strings for job search APIs.
        """
        role_override = user_preferences.get("preferred_role", "").strip()
        location = user_preferences.get("location", "").strip()
        job_type = user_preferences.get("job_type", "").strip()

        if self.is_configured() and self.client:
            try:
                prompt = SEARCH_QUERY_USER_PROMPT.format(
                    skills=", ".join(profile.get("skills", [])[:10]),
                    languages=", ".join(profile.get("programming_languages", [])[:10]),
                    frameworks=", ".join(profile.get("frameworks", [])[:10]),
                    preferred_roles=", ".join(profile.get("preferred_roles", [])[:5]),
                    experience_level=profile.get("experience_level", "Mid"),
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
                # Clean up any potential markdown codeblocks
                if content.startswith("```"):
                    content = re.sub(r"^```[a-z]*\n?", "", content)
                    content = re.sub(r"\n?```$", "", content)
                queries = json.loads(content)
                if isinstance(queries, list) and len(queries) > 0:
                    return [q.strip() for q in queries if isinstance(q, str)]
            except Exception as e:
                print(f"[LLMClient Warning] Query generation failed: {e}. Using fallback query generation.")

        # Heuristic fallback query generation
        queries = []
        if role_override:
            queries.append(role_override)

        roles = profile.get("preferred_roles", [])
        for role in roles:
            if role and role not in queries:
                queries.append(role)

        langs = profile.get("programming_languages", [])
        frameworks = profile.get("frameworks", [])
        if langs:
            queries.append(f"{langs[0]} Developer")
            if frameworks:
                queries.append(f"{langs[0]} {frameworks[0]} Engineer")
        elif frameworks:
            queries.append(f"{frameworks[0]} Developer")

        if not queries:
            queries = ["Software Engineer", "Backend Developer", "Full Stack Developer"]

        return list(dict.fromkeys(queries))[:4]

    def explain_job_match(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates qualitative match evaluation and explanation for a job.
        """
        if self.is_configured() and self.client:
            try:
                tech_stack = profile.get("programming_languages", []) + profile.get("frameworks", [])
                prompt = MATCHING_USER_PROMPT.format(
                    skills=", ".join(profile.get("skills", [])),
                    tech_stack=", ".join(tech_stack),
                    experience_level=profile.get("experience_level", "Mid"),
                    preferred_location=", ".join(profile.get("preferred_locations", [])),
                    job_title=job.get("title", ""),
                    company=job.get("company", ""),
                    job_location=job.get("location", ""),
                    job_skills=", ".join(job.get("skills", [])),
                    job_description=job.get("description", "")[:1000]
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
                res = json.loads(response.choices[0].message.content.strip())
                return res
            except Exception as e:
                print(f"[LLMClient Warning] Match explanation failed: {e}")

        return {}

    def _validate_and_normalize_profile(self, p: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures all standard profile fields are present and lists are correctly formatted."""
        schema_defaults = {
            "name": "Candidate",
            "skills": [],
            "programming_languages": [],
            "frameworks": [],
            "libraries": [],
            "databases": [],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "preferred_roles": [],
            "preferred_locations": [],
            "experience_level": "Mid Level"
        }
        for key, default_val in schema_defaults.items():
            if key not in p or p[key] is None:
                p[key] = default_val
            elif isinstance(default_val, list) and not isinstance(p[key], list):
                p[key] = [str(p[key])]
        return p

    def _heuristic_parse_profile(self, text: str) -> Dict[str, Any]:
        """Basic regex-based profile extractor when OpenAI API is not available."""
        skills = []
        common_skills = [
            "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "Go", "Rust",
            "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI", "Spring Boot",
            "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "Azure",
            "Git", "REST API", "GraphQL", "Microservices", "Machine Learning", "PyTorch", "TensorFlow"
        ]
        
        text_lower = text.lower()
        found_skills = [s for s in common_skills if s.lower() in text_lower]
        
        langs = [s for s in ["Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "Go", "Rust"] if s in found_skills]
        frameworks = [s for s in ["React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI", "Spring Boot"] if s in found_skills]
        databases = [s for s in ["SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis"] if s in found_skills]
        
        roles = []
        if "java" in text_lower and "backend" in text_lower:
            roles.append("Java Backend Developer")
        if "python" in text_lower or "django" in text_lower or "fastapi" in text_lower:
            roles.append("Python Developer")
        if "full stack" in text_lower or "react" in text_lower:
            roles.append("Full Stack Developer")
        if not roles and found_skills:
            roles.append(f"{found_skills[0]} Developer")
        if not roles:
            roles = ["Software Engineer"]

        # Extract potential name from first non-empty line
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        name = lines[0] if lines and len(lines[0]) < 40 and not any(kw in lines[0].lower() for kw in ["resume", "curriculum", "page"]) else "Candidate Profile"

        exp_level = "Mid Level"
        if any(kw in text_lower for kw in ["senior", "lead", "architect", "5+ years", "7+ years", "10+ years"]):
            exp_level = "Senior"
        elif any(kw in text_lower for kw in ["junior", "intern", "trainee", "entry level", "graduate"]):
            exp_level = "Junior"

        return {
            "name": name,
            "skills": found_skills,
            "programming_languages": langs,
            "frameworks": frameworks,
            "libraries": [],
            "databases": databases,
            "education": ["Extracted from resume"],
            "experience": ["Work history included in resume text"],
            "projects": [],
            "certifications": [],
            "preferred_roles": roles,
            "preferred_locations": ["Remote", "Hybrid"],
            "experience_level": exp_level
        }
