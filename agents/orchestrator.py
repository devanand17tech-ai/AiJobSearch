"""
Agent 6: Orchestrator Agent
Central coordinator that manages shared workflow state, executes nodes in a directed graph,
logs execution traces, and unifies all specialist agents.
Supports both native LangGraph and an identical-pattern state graph engine.
"""
import time
from typing import Dict, Any, List, Optional, Callable, Union, BinaryIO
from datetime import datetime

from models.schemas import (
    CandidateProfile,
    RawJobListing,
    VerifiedJob,
    MatchedJob,
    CareerAdvice,
    AgentExecutionLog
)
from models.state import AgentWorkflowState, WorkflowStateModel
from agents.resume_agent import ResumeAnalysisAgent
from agents.job_search_agent import JobSearchAgent
from agents.verification_agent import JobVerificationAgent
from agents.matching_agent import JobMatchingAgent
from agents.career_advisor_agent import CareerAdvisorAgent

# Attempt to import LangGraph
try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    START = "__start__"
    END = "__end__"

class GraphEngineFallback:
    """
    Lightweight, resilient StateGraph engine implementing the LangGraph execution protocol.
    Guarantees zero-dependency reliability in offline or restricted environments.
    """
    def __init__(self, state_schema):
        self.state_schema = state_schema
        self.nodes: Dict[str, Callable] = {}
        self.edges: Dict[str, str] = {}
        self.start_node: Optional[str] = None

    def add_node(self, name: str, func: Callable):
        self.nodes[name] = func

    def add_edge(self, from_node: str, to_node: str):
        if from_node == START:
            self.start_node = to_node
        else:
            self.edges[from_node] = to_node

    def compile(self):
        return self

    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        current = self.start_node
        state_dict = dict(state)

        while current and current != END:
            func = self.nodes.get(current)
            if not func:
                break
            delta = func(state_dict)
            if isinstance(delta, dict):
                state_dict.update(delta)
            current = self.edges.get(current, END)

        return state_dict

class MultiAgentOrchestrator:
    """
    Agent 6: Central Multi-Agent Orchestrator.
    Coordinates Agent 1 through Agent 5 through a shared graph state.
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        apify_token: Optional[str] = None,
        progress_callback: Optional[Callable[[str, str, Dict[str, Any]], None]] = None
    ):
        self.openai_api_key = openai_api_key
        self.apify_token = apify_token
        self.progress_callback = progress_callback

        # Instantiate specialist agents
        self.resume_agent = ResumeAnalysisAgent(openai_api_key=openai_api_key)
        self.job_search_agent = JobSearchAgent(openai_api_key=openai_api_key, apify_token=apify_token)
        self.verification_agent = JobVerificationAgent(openai_api_key=openai_api_key)
        self.matching_agent = JobMatchingAgent(openai_api_key=openai_api_key)
        self.advisor_agent = CareerAdvisorAgent(openai_api_key=openai_api_key)

        # Build execution graph
        self.graph = self._build_workflow_graph()

    def _notify(self, agent_name: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Dispatches real-time status update to callback listener."""
        if self.progress_callback:
            try:
                self.progress_callback(agent_name, status, details or {})
            except Exception as e:
                print(f"[Orchestrator Callback Warning] {e}")

    # ==========================================
    # GRAPH NODES
    # ==========================================

    def resume_analysis_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 1: Resume Analysis Agent node."""
        t0 = time.time()
        agent_name = "Resume Analysis Agent"
        self._notify(agent_name, "RUNNING", {"message": "Extracting text and candidate profile..."})

        logs = list(state.get("execution_logs", []))
        errors = list(state.get("errors", []))

        try:
            resume_source = state.get("resume_source")
            resume_text = state.get("resume_text", "")
            if not resume_text and resume_source:
                resume_text = self.resume_agent.extract_text(resume_source)

            profile = self.resume_agent.analyze(resume_text)
            duration = time.time() - t0

            log_entry = AgentExecutionLog(
                agent_name=agent_name,
                status="SUCCESS",
                message=f"Parsed profile for {profile.name} with {len(profile.all_skills)} skills.",
                timestamp=datetime.now().strftime("%H:%M:%S"),
                duration_seconds=round(duration, 2),
                details={"skills_count": len(profile.all_skills), "target_roles": profile.target_roles}
            )
            logs.append(log_entry)
            self._notify(agent_name, "SUCCESS", {"profile": profile.model_dump()})

            return {
                "resume_text": resume_text,
                "candidate_profile": profile,
                "current_agent": agent_name,
                "execution_logs": logs
            }
        except Exception as e:
            err_msg = f"Resume analysis failed: {str(e)}"
            errors.append(err_msg)
            logs.append(AgentExecutionLog(
                agent_name=agent_name,
                status="FAILED",
                message=err_msg,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                duration_seconds=round(time.time() - t0, 2)
            ))
            self._notify(agent_name, "FAILED", {"error": err_msg})
            return {"errors": errors, "execution_logs": logs}

    def job_search_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 2: Job Search Agent node."""
        t0 = time.time()
        agent_name = "Job Search Agent"
        self._notify(agent_name, "RUNNING", {"message": "Formulating queries and searching listings..."})

        logs = list(state.get("execution_logs", []))
        errors = list(state.get("errors", []))
        profile: Optional[CandidateProfile] = state.get("candidate_profile")
        user_prefs = state.get("user_preferences", {})

        if not profile:
            err_msg = "Missing candidate profile for job search."
            errors.append(err_msg)
            return {"errors": errors}

        try:
            queries = self.job_search_agent.plan_search_queries(profile, user_prefs)
            search_output = self.job_search_agent.search_jobs(queries, user_prefs)

            raw_jobs = search_output.get("raw_jobs", [])
            metadata = search_output.get("metadata", {})
            duration = time.time() - t0

            log_entry = AgentExecutionLog(
                agent_name=agent_name,
                status="SUCCESS",
                message=f"Discovered {len(raw_jobs)} job listings across {len(queries)} queries.",
                timestamp=datetime.now().strftime("%H:%M:%S"),
                duration_seconds=round(duration, 2),
                details={"queries": queries, "job_count": len(raw_jobs)}
            )
            logs.append(log_entry)
            self._notify(agent_name, "SUCCESS", {"job_count": len(raw_jobs), "queries": queries})

            return {
                "search_queries": queries,
                "raw_jobs": raw_jobs,
                "search_metadata": metadata,
                "current_agent": agent_name,
                "execution_logs": logs
            }
        except Exception as e:
            err_msg = f"Job search failed: {str(e)}"
            errors.append(err_msg)
            logs.append(AgentExecutionLog(
                agent_name=agent_name,
                status="FAILED",
                message=err_msg,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                duration_seconds=round(time.time() - t0, 2)
            ))
            self._notify(agent_name, "FAILED", {"error": err_msg})
            return {"errors": errors, "execution_logs": logs}

    def job_verification_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 3: Job Verification Agent node."""
        t0 = time.time()
        agent_name = "Job Verification Agent"
        self._notify(agent_name, "RUNNING", {"message": "Auditing listings for legitimacy, URLs, and eligibility..."})

        logs = list(state.get("execution_logs", []))
        errors = list(state.get("errors", []))
        raw_jobs = state.get("raw_jobs", [])

        try:
            verified_jobs = self.verification_agent.verify_jobs(raw_jobs)
            duration = time.time() - t0

            # Count statuses
            verified_count = sum(1 for j in verified_jobs if j.verification_status.value == "VERIFIED")
            flagged_count = sum(1 for j in verified_jobs if j.verification_status.value == "FLAGGED")
            duplicates_count = sum(1 for j in verified_jobs if j.is_duplicate)

            summary = {
                "total_audited": len(verified_jobs),
                "verified_legitimate": verified_count,
                "flagged": flagged_count,
                "duplicates_removed": duplicates_count
            }

            log_entry = AgentExecutionLog(
                agent_name=agent_name,
                status="SUCCESS",
                message=f"Verified {verified_count} jobs, flagged {flagged_count}, identified {duplicates_count} duplicates.",
                timestamp=datetime.now().strftime("%H:%M:%S"),
                duration_seconds=round(duration, 2),
                details=summary
            )
            logs.append(log_entry)
            self._notify(agent_name, "SUCCESS", summary)

            return {
                "verified_jobs": verified_jobs,
                "verification_summary": summary,
                "current_agent": agent_name,
                "execution_logs": logs
            }
        except Exception as e:
            err_msg = f"Job verification failed: {str(e)}"
            errors.append(err_msg)
            logs.append(AgentExecutionLog(
                agent_name=agent_name,
                status="FAILED",
                message=err_msg,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                duration_seconds=round(time.time() - t0, 2)
            ))
            self._notify(agent_name, "FAILED", {"error": err_msg})
            return {"errors": errors, "execution_logs": logs}

    def job_matching_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 4: Job Matching Agent node."""
        t0 = time.time()
        agent_name = "Job Matching Agent"
        self._notify(agent_name, "RUNNING", {"message": "Evaluating transparent compatibility scores..."})

        logs = list(state.get("execution_logs", []))
        errors = list(state.get("errors", []))
        profile = state.get("candidate_profile")
        verified_jobs = state.get("verified_jobs", [])
        user_prefs = state.get("user_preferences", {})

        if not profile:
            errors.append("Candidate profile missing for matching.")
            return {"errors": errors}

        try:
            matched_jobs = self.matching_agent.match_jobs(profile, verified_jobs, user_prefs)
            duration = time.time() - t0

            # Apply min score and remote filters
            min_score = state.get("min_score", 0)
            filtered_matches = [m for m in matched_jobs if m.match_score >= min_score]

            log_entry = AgentExecutionLog(
                agent_name=agent_name,
                status="SUCCESS",
                message=f"Scored {len(matched_jobs)} jobs. Top score: {matched_jobs[0].match_score if matched_jobs else 0}%.",
                timestamp=datetime.now().strftime("%H:%M:%S"),
                duration_seconds=round(duration, 2),
                details={"matched_count": len(matched_jobs), "top_score": matched_jobs[0].match_score if matched_jobs else 0}
            )
            logs.append(log_entry)
            self._notify(agent_name, "SUCCESS", {"count": len(filtered_matches)})

            return {
                "matched_jobs": filtered_matches,
                "current_agent": agent_name,
                "execution_logs": logs
            }
        except Exception as e:
            err_msg = f"Job matching failed: {str(e)}"
            errors.append(err_msg)
            logs.append(AgentExecutionLog(
                agent_name=agent_name,
                status="FAILED",
                message=err_msg,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                duration_seconds=round(time.time() - t0, 2)
            ))
            self._notify(agent_name, "FAILED", {"error": err_msg})
            return {"errors": errors, "execution_logs": logs}

    def career_advisor_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 5: Career Advisor Agent node."""
        t0 = time.time()
        agent_name = "Career Advisor Agent"
        self._notify(agent_name, "RUNNING", {"message": "Synthesizing strategic career advice..."})

        logs = list(state.get("execution_logs", []))
        errors = list(state.get("errors", []))
        profile = state.get("candidate_profile")
        matched_jobs = state.get("matched_jobs", [])

        if not profile:
            errors.append("Candidate profile missing for career advice.")
            return {"errors": errors}

        try:
            advice = self.advisor_agent.formulate_advice(profile, matched_jobs)
            duration = time.time() - t0

            log_entry = AgentExecutionLog(
                agent_name=agent_name,
                status="SUCCESS",
                message=f"Formulated career advice: {len(advice.priority_applications)} prioritized jobs, {len(advice.systemic_skill_gaps)} systemic skill gaps.",
                timestamp=datetime.now().strftime("%H:%M:%S"),
                duration_seconds=round(duration, 2),
                details={"priority_count": len(advice.priority_applications), "tech_to_learn": advice.technologies_to_learn}
            )
            logs.append(log_entry)
            self._notify(agent_name, "SUCCESS", {"advice": advice.model_dump()})

            return {
                "career_advice": advice,
                "current_agent": agent_name,
                "execution_logs": logs,
                "is_completed": True,
                "status": "COMPLETED"
            }
        except Exception as e:
            err_msg = f"Career advice formulation failed: {str(e)}"
            errors.append(err_msg)
            logs.append(AgentExecutionLog(
                agent_name=agent_name,
                status="FAILED",
                message=err_msg,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                duration_seconds=round(time.time() - t0, 2)
            ))
            self._notify(agent_name, "FAILED", {"error": err_msg})
            return {"errors": errors, "execution_logs": logs}

    # ==========================================
    # WORKFLOW GRAPH BUILDER
    # ==========================================

    def _build_workflow_graph(self):
        """Builds either LangGraph StateGraph or fallback graph engine."""
        if LANGGRAPH_AVAILABLE:
            workflow = StateGraph(AgentWorkflowState)
            workflow.add_node("resume_analysis", self.resume_analysis_node)
            workflow.add_node("job_search", self.job_search_node)
            workflow.add_node("job_verification", self.job_verification_node)
            workflow.add_node("job_matching", self.job_matching_node)
            workflow.add_node("career_advisor", self.career_advisor_node)

            workflow.add_edge(START, "resume_analysis")
            workflow.add_edge("resume_analysis", "job_search")
            workflow.add_edge("job_search", "job_verification")
            workflow.add_edge("job_verification", "job_matching")
            workflow.add_edge("job_matching", "career_advisor")
            workflow.add_edge("career_advisor", END)

            return workflow.compile()
        else:
            fallback = GraphEngineFallback(AgentWorkflowState)
            fallback.add_node("resume_analysis", self.resume_analysis_node)
            fallback.add_node("job_search", self.job_search_node)
            fallback.add_node("job_verification", self.job_verification_node)
            fallback.add_node("job_matching", self.job_matching_node)
            fallback.add_node("career_advisor", self.career_advisor_node)

            fallback.add_edge(START, "resume_analysis")
            fallback.add_edge("resume_analysis", "job_search")
            fallback.add_edge("job_search", "job_verification")
            fallback.add_edge("job_verification", "job_matching")
            fallback.add_edge("job_matching", "career_advisor")
            fallback.add_edge("career_advisor", END)

            return fallback.compile()

    def run(
        self,
        resume_source: Union[str, bytes, BinaryIO],
        user_preferences: Dict[str, Any],
        sort_by: str = "Best match",
        min_score: int = 0
    ) -> Dict[str, Any]:
        """
        Executes the multi-agent system end-to-end.
        """
        initial_state: Dict[str, Any] = {
            "resume_source": resume_source,
            "resume_text": "",
            "user_preferences": user_preferences,
            "sort_by": sort_by,
            "min_score": min_score,
            "candidate_profile": None,
            "search_queries": [],
            "raw_jobs": [],
            "search_metadata": {},
            "verified_jobs": [],
            "verification_summary": {},
            "matched_jobs": [],
            "career_advice": None,
            "current_agent": "Initializing",
            "status": "RUNNING",
            "execution_logs": [],
            "errors": [],
            "is_completed": False
        }

        # Execute through graph
        final_state = self.graph.invoke(initial_state)

        # Apply sorting logic
        matched: List[MatchedJob] = final_state.get("matched_jobs", [])
        if sort_by == "Best match":
            matched.sort(key=lambda x: x.match_score, reverse=True)
        elif sort_by == "Newest":
            matched.sort(key=lambda x: x.date_posted, reverse=True)

        final_state["matched_jobs"] = matched
        final_state["success"] = (len(final_state.get("errors", [])) == 0) or bool(final_state.get("candidate_profile"))

        return final_state
