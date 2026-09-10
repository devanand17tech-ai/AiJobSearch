SEARCH_QUERY_SYSTEM_PROMPT = """You are a specialized recruitment AI Agent.
Given a candidate profile and user search preferences, generate 3 to 5 targeted search query strings for job search APIs (like Google Jobs, Indeed, LinkedIn).

Return ONLY a JSON list of strings.
Example: ["Java Developer", "Spring Boot Backend Engineer", "Junior Java Developer"]
"""

SEARCH_QUERY_USER_PROMPT = """Candidate Profile:
- Skills: {skills}
- Programming Languages: {languages}
- Frameworks: {frameworks}
- Preferred Roles: {preferred_roles}
- Experience Level: {experience_level}

User Preferences Overrides (if any):
- Role Override: {role_override}
- Location: {location}
- Job Type: {job_type}

Generate 3-5 concise, high-yield job search keywords/queries.
"""
