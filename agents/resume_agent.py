"""
Agent 1: Resume Analysis Agent
Extracts candidate info, technical skills, education, experience, target roles, and weak skills.
"""
import os
import json
import re
from typing import Union, BinaryIO, Optional, Dict, Any

from models.schemas import CandidateProfile, EducationEntry, ExperienceEntry
from tools.resume_parser import parse_pdf_resume
from prompts.resume_prompt import RESUME_PARSER_SYSTEM_PROMPT, RESUME_PARSER_USER_PROMPT

class ResumeAnalysisAgent:
    """
    Specialist agent responsible for PDF resume parsing and candidate profile structuring.
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
                print(f"[ResumeAnalysisAgent] OpenAI client init failed: {e}")

    def is_llm_configured(self) -> bool:
        return bool(self.api_key and self.client is not None and len(self.api_key) > 5)

    def extract_text(self, resume_source: Union[str, bytes, BinaryIO]) -> str:
        """Extracts cleaned text from PDF resume."""
        return parse_pdf_resume(resume_source)

    def analyze(self, resume_text: str) -> CandidateProfile:
        """
        Processes resume text and constructs a validated CandidateProfile.
        """
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is empty. Cannot extract candidate profile.")

        # Try LLM extraction first if configured
        if self.is_llm_configured():
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
                data = json.loads(raw_json)
                return self._build_profile_from_dict(data, resume_text)
            except Exception as e:
                print(f"[ResumeAnalysisAgent Warning] LLM parsing failed: {e}. Falling back to heuristic extractor.")

        # Heuristic fallback parsing
        return self._heuristic_parse(resume_text)

    def _build_profile_from_dict(self, data: Dict[str, Any], raw_text: str) -> CandidateProfile:
        """Maps JSON dictionary from LLM into CandidateProfile schema."""
        education_entries = []
        for edu in data.get("education", []):
            if isinstance(edu, dict):
                education_entries.append(EducationEntry(
                    degree=edu.get("degree", ""),
                    field_of_study=edu.get("field_of_study", ""),
                    institution=edu.get("institution", ""),
                    graduation_year=edu.get("graduation_year"),
                    details=edu.get("details", "")
                ))
            elif isinstance(edu, str):
                education_entries.append(EducationEntry(degree=edu))

        experience_entries = []
        for exp in data.get("experience", []):
            if isinstance(exp, dict):
                experience_entries.append(ExperienceEntry(
                    role=exp.get("role", ""),
                    company=exp.get("company", ""),
                    duration=exp.get("duration", ""),
                    start_year=exp.get("start_year"),
                    end_year=exp.get("end_year"),
                    responsibilities=exp.get("responsibilities", []) if isinstance(exp.get("responsibilities"), list) else []
                ))
            elif isinstance(exp, str):
                experience_entries.append(ExperienceEntry(role=exp))

        # Determine graduation year if not explicitly extracted
        grad_year = data.get("graduation_year")
        if not grad_year and education_entries:
            for edu in education_entries:
                if edu.graduation_year:
                    grad_year = edu.graduation_year
                    break

        # Calculate or parse total experience
        total_exp = data.get("total_years_experience")
        if total_exp is None:
            total_exp = 0.0

        return CandidateProfile(
            name=data.get("name") or "Candidate",
            email=data.get("email"),
            phone=data.get("phone"),
            location=data.get("location"),
            technical_skills=data.get("technical_skills", []) or data.get("skills", []),
            programming_languages=data.get("programming_languages", []),
            frameworks=data.get("frameworks", []),
            databases=data.get("databases", []),
            tools=data.get("tools", []),
            education=education_entries,
            graduation_year=grad_year,
            total_years_experience=float(total_exp),
            experience=experience_entries,
            target_roles=data.get("target_roles", []) or data.get("preferred_roles", ["Software Engineer"]),
            experience_level=data.get("experience_level", "Entry Level"),
            weak_or_missing_skills=data.get("weak_or_missing_skills", [])
        )

    def _heuristic_parse(self, text: str) -> CandidateProfile:
        """Regex and keyword-based extractor for environments without active LLM."""
        text_lower = text.lower()

        # Skill catalogues
        known_langs = ["Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "Go", "Rust", "Ruby", "PHP", "Kotlin", "Swift", "SQL"]
        known_frameworks = ["React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI", "Spring Boot", "Express", "Next.js", "ASP.NET"]
        known_databases = ["PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Oracle", "Cassandra", "DynamoDB"]
        known_tools = ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git", "GitHub Actions", "CI/CD", "Linux", "Terraform", "REST API", "GraphQL"]

        langs = [s for s in known_langs if re.search(r'\b' + re.escape(s.lower()) + r'\b', text_lower)]
        frameworks = [s for s in known_frameworks if re.search(r'\b' + re.escape(s.lower()) + r'\b', text_lower)]
        databases = [s for s in known_databases if re.search(r'\b' + re.escape(s.lower()) + r'\b', text_lower)]
        tools = [s for s in known_tools if re.search(r'\b' + re.escape(s.lower()) + r'\b', text_lower)]
        all_tech = list(dict.fromkeys(langs + frameworks + databases + tools))

        # Extract name from first readable line
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        name = "Candidate"
        if lines:
            first_line = lines[0]
            if len(first_line) < 40 and not any(kw in first_line.lower() for kw in ["resume", "curriculum", "page", "cv", "profile"]):
                name = first_line

        # Extract email and phone
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        email = email_match.group(0) if email_match else None

        phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        phone = phone_match.group(0) if phone_match else None

        # Extract graduation year
        grad_year = None
        grad_match = re.search(r'\b(20[12]\d)\b', text)
        if grad_match:
            grad_year = int(grad_match.group(1))

        # Target roles derivation
        target_roles = []
        if "java" in text_lower and ("backend" in text_lower or "spring" in text_lower):
            target_roles.append("Java Backend Developer")
        if "python" in text_lower and ("backend" in text_lower or "django" in text_lower or "fastapi" in text_lower):
            target_roles.append("Python Backend Developer")
        if ("react" in text_lower or "vue" in text_lower or "angular" in text_lower) and "node" in text_lower:
            target_roles.append("Full Stack Developer")
        elif "react" in text_lower or "frontend" in text_lower:
            target_roles.append("Frontend Developer")
        if not target_roles and langs:
            target_roles.append(f"{langs[0]} Developer")
        if not target_roles:
            target_roles = ["Software Engineer"]

        # Experience level estimate
        exp_level = "Entry Level"
        total_exp = 0.0
        if any(kw in text_lower for kw in ["senior", "lead", "architect", "5+ years", "6+ years", "7+ years"]):
            exp_level = "Senior (5+ yrs)"
            total_exp = 5.0
        elif any(kw in text_lower for kw in ["mid level", "3+ years", "4+ years", "2-4 years"]):
            exp_level = "Mid Level (2-5 yrs)"
            total_exp = 3.0
        elif any(kw in text_lower for kw in ["junior", "1-2 years", "1+ year"]):
            exp_level = "Junior (0-2 yrs)"
            total_exp = 1.0

        # Weak or missing skills identification based on target role
        weak_skills = []
        if "backend" in "".join(target_roles).lower():
            for expected in ["Docker", "Kubernetes", "Redis", "CI/CD"]:
                if expected not in all_tech:
                    weak_skills.append(expected)
        elif "full stack" in "".join(target_roles).lower():
            for expected in ["TypeScript", "Docker", "REST API"]:
                if expected not in all_tech:
                    weak_skills.append(expected)

        edu_entry = EducationEntry(
            degree="Bachelor's Degree in Computer Science or related",
            graduation_year=grad_year
        )

        return CandidateProfile(
            name=name,
            email=email,
            phone=phone,
            location="Remote / Preferred",
            technical_skills=all_tech,
            programming_languages=langs,
            frameworks=frameworks,
            databases=databases,
            tools=tools,
            education=[edu_entry],
            graduation_year=grad_year,
            total_years_experience=total_exp,
            experience=[ExperienceEntry(role="Software Engineer Experience from Resume")],
            target_roles=target_roles,
            experience_level=exp_level,
            weak_or_missing_skills=weak_skills
        )
