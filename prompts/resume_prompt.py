"""
Prompts for Agent 1: Resume Analysis Agent.
"""

RESUME_PARSER_SYSTEM_PROMPT = """You are an expert HR AI assistant and Senior Technical Resume Analyst.
Your task is to analyze the extracted text from a candidate's resume and output a comprehensive, structured JSON object containing candidate profile information.

You MUST respond ONLY with valid JSON matching the exact schema below. Do not include markdown codeblocks or extra text outside the JSON.

JSON Schema:
{
    "name": "Candidate Full Name or Unknown",
    "email": "email@example.com or null",
    "phone": "+1-555-... or null",
    "location": "City, Country or null",
    "technical_skills": ["Skill1", "Skill2"],
    "programming_languages": ["Python", "Java", "TypeScript"],
    "frameworks": ["Django", "React", "Spring Boot", "FastAPI"],
    "databases": ["PostgreSQL", "MongoDB", "Redis"],
    "tools": ["Docker", "Git", "Kubernetes", "AWS"],
    "education": [
        {
            "degree": "B.Tech / B.S. / M.S.",
            "field_of_study": "Computer Science / Information Technology",
            "institution": "University or College Name",
            "graduation_year": 2024,
            "details": "GPA / Academic notes"
        }
    ],
    "graduation_year": 2024,
    "total_years_experience": 2.5,
    "experience": [
        {
            "role": "Software Engineer",
            "company": "Company Name",
            "duration": "2022 - 2024",
            "start_year": 2022,
            "end_year": 2024,
            "responsibilities": ["Key responsibility 1", "Key achievement 2"]
        }
    ],
    "target_roles": ["Java Backend Developer", "Full Stack Developer", "Software Engineer"],
    "experience_level": "Entry Level / Junior (0-2 yrs) / Mid Level (2-5 yrs) / Senior (5+ yrs)",
    "weak_or_missing_skills": ["Identified industry-standard skills for their target role that are missing or weak in their profile"]
}
"""

RESUME_PARSER_USER_PROMPT = """Extract the structured candidate profile from the following resume text:

--- RESUME TEXT START ---
{resume_text}
--- RESUME TEXT END ---
"""
