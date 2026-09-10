import os
import json
from typing import Dict, Any, Optional

class UserPreferenceMemory:
    """
    Modular session and persistent storage for non-sensitive user preferences.
    Saves and loads search parameters without storing personal PII or raw resumes.
    """

    def __init__(self, memory_file: str = "user_preferences.json"):
        self.memory_file = memory_file
        self.preferences = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        """Loads preferences from disk if present."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[UserPreferenceMemory Warning] Could not load memory: {e}")
        return {
            "preferred_role": "",
            "location": "",
            "job_type": "Any",
            "experience_level": "Any",
            "min_salary": 0,
            "max_jobs": 10
        }

    def save_preferences(self, prefs: Dict[str, Any]) -> None:
        """Updates and persists non-sensitive preferences."""
        # Sanitize and store only safe fields
        safe_keys = ["preferred_role", "location", "job_type", "experience_level", "min_salary", "max_jobs"]
        for key in safe_keys:
            if key in prefs:
                self.preferences[key] = prefs[key]

        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.preferences, f, indent=4)
        except Exception as e:
            print(f"[UserPreferenceMemory Warning] Could not save memory: {e}")

    def get_preferences(self) -> Dict[str, Any]:
        """Returns the current stored preferences."""
        return self.preferences
