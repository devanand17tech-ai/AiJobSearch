"""
Data models and schemas for the Multi-Agent AI Job Search System.
"""
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field

class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    FLAGGED = "FLAGGED"
    SUSPICIOUS = "SUSPICIOUS"
    EXPIRED = "EXPIRED"
    UNVERIFIED = "UNVERIFIED"

class EligibilityStatus(str, Enum):
    ELIGIBLE = "Eligible"
    MARGINAL = "Marginal"
    INELIGIBLE = "Ineligible"

class EducationEntry(BaseModel):
    degree: str = Field(default="", description="Degree title (e.g. B.Tech, B.S., M.S.)")
    field_of_study: str = Field(default="", description="Major or specialization (e.g. Computer Science)")
    institution: str = Field(default="", description="University or college name")
    graduation_year: Optional[int] = Field(default=None, description="Year of graduation if identifiable")
    details: str = Field(default="", description="Additional academic details or GPA")

class ExperienceEntry(BaseModel):
    role: str = Field(default="", description="Job title or role")
    company: str = Field(default="", description="Company or organization name")
    duration: str = Field(default="", description="Duration string e.g. '2021 - Present'")
    start_year: Optional[int] = Field(default=None, description="Starting year")
    end_year: Optional[int] = Field(default=None, description="Ending year (None if Present)")
    responsibilities: List[str] = Field(default_factory=list, description="Key achievements and duties")

class CandidateProfile(BaseModel):
    name: str = Field(default="Candidate", description="Full name of candidate")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    location: Optional[str] = Field(default=None, description="Current location or city")
    technical_skills: List[str] = Field(default_factory=list, description="Core technical competencies")
    programming_languages: List[str] = Field(default_factory=list, description="Languages e.g. Python, Java")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks e.g. React, Spring Boot, FastAPI")
    databases: List[str] = Field(default_factory=list, description="Databases e.g. PostgreSQL, Redis")
    tools: List[str] = Field(default_factory=list, description="DevOps / build tools e.g. Docker, Git, AWS")
    education: List[EducationEntry] = Field(default_factory=list, description="Education records")
    graduation_year: Optional[int] = Field(default=None, description="Primary graduation year")
    total_years_experience: float = Field(default=0.0, description="Estimated total professional experience in years")
    experience: List[ExperienceEntry] = Field(default_factory=list, description="Employment history")
    target_roles: List[str] = Field(default_factory=list, description="Primary job titles candidate qualifies for")
    experience_level: str = Field(default="Entry Level", description="Entry Level / Junior / Mid / Senior / Lead")
    weak_or_missing_skills: List[str] = Field(default_factory=list, description="Skills typically expected for target roles that are weak or missing")

    @property
    def all_skills(self) -> List[str]:
        """Consolidated unique list of all skills."""
        combined = []
        for s in (self.technical_skills + self.programming_languages + self.frameworks + self.databases + self.tools):
            s_clean = s.strip()
            if s_clean and s_clean not in combined:
                combined.append(s_clean)
        return combined

class RawJobListing(BaseModel):
    id: str = Field(default="", description="Unique identifier for the job listing")
    title: str = Field(default="Job Title Not Specified", description="Job title")
    company: str = Field(default="Company Confidential", description="Hiring company")
    location: str = Field(default="Location Not Specified", description="Job location or Remote")
    description: str = Field(default="", description="Full or snippet job description")
    salary: str = Field(default="Not Specified", description="Compensation if listed")
    experience: str = Field(default="Not Specified", description="Experience description")
    job_type: str = Field(default="Full-Time", description="Full-Time, Part-Time, Contract, etc.")
    skills: List[str] = Field(default_factory=list, description="Required or mentioned skills")
    url: str = Field(default="#", description="Application or listing URL")
    source: str = Field(default="Apify", description="Source scraper or DEMO DATA")
    date_posted: str = Field(default="Recently Posted", description="Posting timestamp or date string")
    is_demo: bool = Field(default=False, description="True if sourced from fallback mock data")

class VerifiedJob(BaseModel):
    raw_job: RawJobListing = Field(description="Underlying raw job details")
    is_url_valid: bool = Field(default=True, description="True if URL has valid protocol and hostname")
    is_duplicate: bool = Field(default=False, description="True if duplicate listing detected")
    eligibility_criteria: List[str] = Field(default_factory=list, description="Extracted eligibility rules from description")
    min_experience_years: float = Field(default=0.0, description="Minimum years of experience required (0 if entry/fresher)")
    max_experience_years: Optional[float] = Field(default=None, description="Maximum years if specified")
    graduation_years_accepted: List[int] = Field(default_factory=list, description="Allowed graduation batches e.g. [2024, 2025, 2026]")
    application_deadline: Optional[str] = Field(default=None, description="Explicit deadline if identified")
    verification_status: VerificationStatus = Field(default=VerificationStatus.VERIFIED, description="Verification outcome")
    verification_flags: List[str] = Field(default_factory=list, description="Warnings or flags (e.g. Expired, Incomplete info)")
    verification_evidence: Dict[str, Any] = Field(default_factory=dict, description="Documented evidence supporting status")

    @property
    def title(self) -> str:
        return self.raw_job.title

    @property
    def company(self) -> str:
        return self.raw_job.company

    @property
    def location(self) -> str:
        return self.raw_job.location

    @property
    def description(self) -> str:
        return self.raw_job.description

    @property
    def salary(self) -> str:
        return self.raw_job.salary

    @property
    def job_type(self) -> str:
        return self.raw_job.job_type

    @property
    def skills(self) -> List[str]:
        return self.raw_job.skills

    @property
    def url(self) -> str:
        return self.raw_job.url

    @property
    def source(self) -> str:
        return self.raw_job.source

    @property
    def date_posted(self) -> str:
        return self.raw_job.date_posted

    @property
    def is_demo(self) -> bool:
        return self.raw_job.is_demo

class MatchedJob(BaseModel):
    verified_job: VerifiedJob = Field(description="Verified job listing")
    match_score: int = Field(default=0, ge=0, le=100, description="Overall compatibility score (0-100)")
    skill_score: int = Field(default=0, ge=0, le=100, description="Skill overlap subscore")
    experience_score: int = Field(default=0, ge=0, le=100, description="Experience alignment subscore")
    title_score: int = Field(default=0, ge=0, le=100, description="Role title alignment subscore")
    location_score: int = Field(default=0, ge=0, le=100, description="Location and workplace fit subscore")
    matched_skills: List[str] = Field(default_factory=list, description="Candidate skills matching job requirements")
    missing_skills: List[str] = Field(default_factory=list, description="Required skills candidate lacks")
    eligibility_status: EligibilityStatus = Field(default=EligibilityStatus.ELIGIBLE, description="Eligibility classification")
    eligibility_reasons: List[str] = Field(default_factory=list, description="Reasons justifying eligibility classification")
    match_explanation: str = Field(default="", description="Clear, transparent narrative of match rationale")

    @property
    def title(self) -> str:
        return self.verified_job.title

    @property
    def company(self) -> str:
        return self.verified_job.company

    @property
    def location(self) -> str:
        return self.verified_job.location

    @property
    def description(self) -> str:
        return self.verified_job.description

    @property
    def salary(self) -> str:
        return self.verified_job.salary

    @property
    def job_type(self) -> str:
        return self.verified_job.job_type

    @property
    def skills(self) -> List[str]:
        return self.verified_job.skills

    @property
    def url(self) -> str:
        return self.verified_job.url

    @property
    def source(self) -> str:
        return self.verified_job.source

    @property
    def date_posted(self) -> str:
        return self.verified_job.date_posted

    @property
    def is_demo(self) -> bool:
        return self.verified_job.is_demo

    @property
    def verification_status(self) -> VerificationStatus:
        return self.verified_job.verification_status

    @property
    def verification_flags(self) -> List[str]:
        return self.verified_job.verification_flags

class JobPriorityRecommendation(BaseModel):
    job_id: str = Field(description="ID of the recommended job")
    title: str = Field(description="Job title")
    company: str = Field(description="Company")
    url: str = Field(description="Application link")
    match_score: int = Field(description="Calculated match score")
    priority_rank: int = Field(description="Rank e.g. 1, 2, 3")
    apply_urgency: str = Field(default="High", description="High / Medium / Normal urgency")
    reason_to_apply_first: str = Field(description="Concrete strategic reason why candidate should apply immediately")

class SkillGapAnalysis(BaseModel):
    skill_name: str = Field(description="Name of the missing skill")
    demand_frequency: int = Field(default=1, description="Number of target jobs requiring this skill")
    importance_level: str = Field(default="Recommended", description="Critical / Recommended / Nice-to-have")
    learning_recommendation: str = Field(description="Actionable path or project recommendation to acquire this skill")

class CareerAdvice(BaseModel):
    priority_applications: List[JobPriorityRecommendation] = Field(
        default_factory=list,
        description="Ranked list of jobs to apply for first based on match and eligibility"
    )
    systemic_skill_gaps: List[SkillGapAnalysis] = Field(
        default_factory=list,
        description="Identified cross-job skill gaps observed across listings"
    )
    technologies_to_learn: List[str] = Field(
        default_factory=list,
        description="High-ROI technologies recommended for learning"
    )
    resume_improvements: List[str] = Field(
        default_factory=list,
        description="Concrete suggestions to tailor resume for the target roles"
    )
    executive_summary: str = Field(
        default="",
        description="High-level career advisory summary for candidate"
    )

class AgentExecutionLog(BaseModel):
    agent_name: str = Field(description="Name of the specialist agent")
    status: str = Field(description="SUCCESS, FAILED, RUNNING, or SKIPPED")
    message: str = Field(description="Status description")
    timestamp: str = Field(description="Timestamp formatted e.g. '12:30:45'")
    duration_seconds: float = Field(default=0.0, description="Execution time in seconds")
    details: Dict[str, Any] = Field(default_factory=dict, description="Metadata or counts produced")
