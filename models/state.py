"""
Workflow State schemas for the Multi-Agent Job Search Orchestrator.
Supports both native LangGraph TypedDict state and Pydantic object state.
"""
from typing import TypedDict, List, Dict, Any, Optional, Union, BinaryIO
from pydantic import BaseModel, Field
from datetime import datetime

from .schemas import (
    CandidateProfile,
    RawJobListing,
    VerifiedJob,
    MatchedJob,
    CareerAdvice,
    AgentExecutionLog
)

class AgentWorkflowState(TypedDict, total=False):
    """
    Shared state dict conforming to LangGraph StateGraph specifications.
    """
    # Inputs
    resume_source: Any
    resume_text: str
    user_preferences: Dict[str, Any]
    sort_by: str
    min_score: int

    # Agent 1 Outputs
    candidate_profile: Optional[CandidateProfile]

    # Agent 2 Outputs
    search_queries: List[str]
    raw_jobs: List[RawJobListing]
    search_metadata: Dict[str, Any]

    # Agent 3 Outputs
    verified_jobs: List[VerifiedJob]
    verification_summary: Dict[str, Any]

    # Agent 4 Outputs
    matched_jobs: List[MatchedJob]

    # Agent 5 Outputs
    career_advice: Optional[CareerAdvice]

    # Agent 6 Orchestrator Tracking
    current_agent: str
    status: str
    execution_logs: List[AgentExecutionLog]
    errors: List[str]
    is_completed: bool

class WorkflowStateModel(BaseModel):
    """
    Pydantic representation of the shared workflow state with helper methods.
    """
    resume_source: Optional[Any] = None
    resume_text: str = ""
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    sort_by: str = "Best match"
    min_score: int = 0

    candidate_profile: Optional[CandidateProfile] = None
    search_queries: List[str] = Field(default_factory=list)
    raw_jobs: List[RawJobListing] = Field(default_factory=list)
    search_metadata: Dict[str, Any] = Field(default_factory=dict)
    verified_jobs: List[VerifiedJob] = Field(default_factory=list)
    verification_summary: Dict[str, Any] = Field(default_factory=dict)
    matched_jobs: List[MatchedJob] = Field(default_factory=list)
    career_advice: Optional[CareerAdvice] = None

    current_agent: str = "Idle"
    status: str = "INITIALIZED"
    execution_logs: List[AgentExecutionLog] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    is_completed: bool = False

    def add_log(self, agent_name: str, status: str, message: str, duration: float = 0.0, details: Optional[Dict[str, Any]] = None):
        """Append an execution trace log entry."""
        log_entry = AgentExecutionLog(
            agent_name=agent_name,
            status=status,
            message=message,
            timestamp=datetime.now().strftime("%H:%M:%S"),
            duration_seconds=round(duration, 2),
            details=details or {}
        )
        self.execution_logs.append(log_entry)
        print(f"[{log_entry.timestamp}] [{agent_name}] [{status}] {message}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to plain dictionary for UI or JSON serialization."""
        return {
            "resume_text": self.resume_text,
            "user_preferences": self.user_preferences,
            "candidate_profile": self.candidate_profile.model_dump() if self.candidate_profile else {},
            "search_queries": self.search_queries,
            "raw_jobs": [j.model_dump() for j in self.raw_jobs],
            "search_metadata": self.search_metadata,
            "verified_jobs": [v.model_dump() for v in self.verified_jobs],
            "verification_summary": self.verification_summary,
            "matched_jobs": [m.model_dump() for m in self.matched_jobs],
            "career_advice": self.career_advice.model_dump() if self.career_advice else {},
            "current_agent": self.current_agent,
            "status": self.status,
            "execution_logs": [l.model_dump() for l in self.execution_logs],
            "errors": self.errors,
            "is_completed": self.is_completed
        }
