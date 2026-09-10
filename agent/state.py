from enum import Enum
from typing import List, Dict, Any
from datetime import datetime

class AgentState(Enum):
    IDLE = "IDLE"
    RESUME_UPLOADED = "RESUME_UPLOADED"
    RESUME_PARSED = "RESUME_PARSED"
    PROFILE_CREATED = "PROFILE_CREATED"
    PLANNING_SEARCH = "PLANNING_SEARCH"
    SEARCHING_JOBS = "SEARCHING_JOBS"
    JOBS_RECEIVED = "JOBS_RECEIVED"
    MATCHING = "MATCHING"
    RANKING = "RANKING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AgentStateMachine:
    """
    Tracks and records state transitions during AI Agent execution flow.
    """

    def __init__(self):
        self.current_state = AgentState.IDLE
        self.history: List[Dict[str, Any]] = []

    def set_state(self, state: AgentState, message: str = ""):
        self.current_state = state
        entry = {
            "state": state.value,
            "message": message,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.history.append(entry)
        print(f"[Agent State Machine] [{entry['timestamp']}] {state.value}: {message}")

    def get_current_state(self) -> AgentState:
        return self.current_state

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

    def reset(self):
        self.current_state = AgentState.IDLE
        self.history = []
