"""
Comprehensive Automated Test Suite for Multi-Agent AI Job Search System.
Tests each specialist agent independently, inter-agent communication,
orchestration workflow, and error resilience.
"""
import unittest
import os
import io

from models.schemas import (
    CandidateProfile,
    EducationEntry,
    ExperienceEntry,
    RawJobListing,
    VerifiedJob,
    MatchedJob,
    CareerAdvice,
    VerificationStatus,
    EligibilityStatus
)
from agents.resume_agent import ResumeAnalysisAgent
from agents.job_search_agent import JobSearchAgent
from agents.verification_agent import JobVerificationAgent
from agents.matching_agent import JobMatchingAgent
from agents.career_advisor_agent import CareerAdvisorAgent
from agents.orchestrator import MultiAgentOrchestrator
from tools.job_verification_tool import (
    validate_job_url,
    extract_experience_bounds,
    extract_graduation_years,
    extract_deadline,
    audit_job_listing
)

class TestMultiAgentSystem(unittest.TestCase):
    """Unit and Integration Tests for the 6-agent system."""

    def setUp(self):
        self.sample_resume = """
        EMILY ZHANG
        Email: emily.zhang@example.com | Phone: +1-555-014-9821 | Seattle, WA
        
        SUMMARY:
        Full Stack Software Engineer with 3+ years experience building cloud applications in Python, React, and PostgreSQL.
        
        SKILLS:
        - Languages: Python, JavaScript, TypeScript, SQL
        - Frameworks: React, FastAPI, Django, Node.js
        - Databases: PostgreSQL, Redis
        - Tools: Docker, Git, AWS
        
        EXPERIENCE:
        Software Engineer | CloudScale Inc (2021 - Present)
        - Developed REST APIs in FastAPI and React frontends.
        - Managed Docker containers and AWS deployment.
        
        EDUCATION:
        B.S. in Computer Science | University of Washington (2017 - 2021)
        """

    def test_01_agent1_resume_analysis(self):
        """Test Agent 1: Resume Analysis Agent extraction and profile structuring."""
        agent = ResumeAnalysisAgent()
        profile = agent.analyze(self.sample_resume)

        self.assertIsInstance(profile, CandidateProfile)
        self.assertIn("EMILY ZHANG", profile.name.upper())
        self.assertIn("Python", profile.programming_languages)
        self.assertIn("React", profile.frameworks)
        self.assertEqual(profile.graduation_year, 2021)
        self.assertGreaterEqual(len(profile.target_roles), 1)
        self.assertGreaterEqual(len(profile.all_skills), 5)

    def test_02_agent2_job_search(self):
        """Test Agent 2: Job Search Agent query generation and discovery."""
        agent = JobSearchAgent()
        profile = CandidateProfile(
            name="Emily Zhang",
            technical_skills=["Python", "FastAPI", "React", "Docker"],
            programming_languages=["Python", "JavaScript"],
            frameworks=["FastAPI", "React"],
            graduation_year=2021,
            total_years_experience=3.0,
            experience_level="Mid Level",
            target_roles=["Full Stack Developer", "Python Backend Developer"]
        )
        user_prefs = {"preferred_role": "Python Backend Developer", "location": "Remote", "max_jobs": 3}
        queries = agent.plan_search_queries(profile, user_prefs)

        self.assertIsInstance(queries, list)
        self.assertGreaterEqual(len(queries), 2)
        self.assertTrue(any("Python" in q for q in queries))

        search_res = agent.search_jobs(queries, user_prefs)
        self.assertIn("raw_jobs", search_res)
        raw_jobs = search_res["raw_jobs"]
        self.assertGreater(len(raw_jobs), 0)
        self.assertIsInstance(raw_jobs[0], RawJobListing)

    def test_03_agent3_verification_tools_and_agent(self):
        """Test Agent 3: Job Verification Tool and Agent URL & eligibility audits."""
        # Test URL validation
        is_valid, msg = validate_job_url("https://careers.google.com/jobs/1234")
        self.assertTrue(is_valid)
        is_invalid, msg = validate_job_url("#")
        self.assertFalse(is_invalid)

        # Test experience extraction
        min_y, max_y, _ = extract_experience_bounds("Requires 3-5 years of experience in Java.")
        self.assertEqual(min_y, 3.0)
        self.assertEqual(max_y, 5.0)

        # Test fresher detection
        min_f, max_f, _ = extract_experience_bounds("Open for fresher candidates or entry-level engineers.")
        self.assertEqual(min_f, 0.0)

        # Test graduation batch extraction
        batches = extract_graduation_years("Eligible candidates from 2024 or 2025 batch only.")
        self.assertEqual(batches, [2024, 2025])

        # Test Agent 3 full audit
        agent = JobVerificationAgent()
        raw_list = [
            RawJobListing(
                id="j1",
                title="Python Engineer",
                company="DataTech",
                location="Remote",
                description="Seeking Python Developer with 2+ years experience. 2024 batch eligible.",
                url="https://datatech.com/jobs/python"
            ),
            # Duplicate
            RawJobListing(
                id="j2",
                title="Python Engineer",
                company="DataTech",
                location="Remote",
                description="Duplicate listing",
                url="https://datatech.com/jobs/python"
            )
        ]
        verified_jobs = agent.verify_jobs(raw_list)
        self.assertEqual(len(verified_jobs), 2)
        self.assertFalse(verified_jobs[0].is_duplicate)
        self.assertTrue(verified_jobs[1].is_duplicate)
        self.assertEqual(verified_jobs[0].min_experience_years, 2.0)
        self.assertEqual(verified_jobs[0].graduation_years_accepted, [2024])

    def test_04_agent4_matching_and_scoring(self):
        """Test Agent 4: Job Matching Agent compatibility and eligibility scoring."""
        agent = JobMatchingAgent()
        profile = CandidateProfile(
            name="Alexander Wang",
            technical_skills=["Java", "Spring Boot", "MySQL", "Docker", "REST API"],
            programming_languages=["Java", "Python"],
            frameworks=["Spring Boot"],
            graduation_year=2018,
            total_years_experience=5.0,
            experience_level="Senior",
            target_roles=["Java Backend Developer"]
        )
        raw_job = RawJobListing(
            id="j_test",
            title="Java Backend Developer",
            company="Enterprise Corp",
            location="Remote",
            description="Looking for Java Backend Developer with Spring Boot, MySQL, and Docker. 3-5 years experience.",
            skills=["Java", "Spring Boot", "MySQL", "Docker", "Kubernetes"],
            url="https://enterprise.com/job"
        )
        v_job = VerifiedJob(
            raw_job=raw_job,
            is_url_valid=True,
            is_duplicate=False,
            min_experience_years=3.0,
            max_experience_years=5.0,
            verification_status=VerificationStatus.VERIFIED
        )

        matched_jobs = agent.match_jobs(profile, [v_job], {"preferred_role": "Java Backend Developer"})
        self.assertEqual(len(matched_jobs), 1)
        match = matched_jobs[0]
        self.assertIsInstance(match, MatchedJob)
        self.assertGreater(match.match_score, 70)
        self.assertEqual(match.eligibility_status, EligibilityStatus.ELIGIBLE)
        self.assertIn("Java", match.matched_skills)
        self.assertIn("Kubernetes", match.missing_skills)

    def test_05_agent5_career_advisor(self):
        """Test Agent 5: Career Advisor Agent synthesis."""
        agent = CareerAdvisorAgent()
        profile = CandidateProfile(
            name="Alexander Wang",
            technical_skills=["Java", "Spring Boot"],
            programming_languages=["Java"],
            target_roles=["Java Backend Developer"]
        )
        raw_job = RawJobListing(
            id="rec_1",
            title="Senior Java Developer",
            company="Tech Corp",
            url="https://techcorp.com",
            skills=["Java", "Spring Boot", "Docker", "Kubernetes"]
        )
        v_job = VerifiedJob(raw_job=raw_job, verification_status=VerificationStatus.VERIFIED)
        matched_job = MatchedJob(
            verified_job=v_job,
            match_score=85,
            matched_skills=["Java", "Spring Boot"],
            missing_skills=["Docker", "Kubernetes"],
            eligibility_status=EligibilityStatus.ELIGIBLE,
            match_explanation="Solid alignment on core Java backend technologies."
        )

        advice = agent.formulate_advice(profile, [matched_job])
        self.assertIsInstance(advice, CareerAdvice)
        self.assertGreaterEqual(len(advice.priority_applications), 1)
        self.assertGreaterEqual(len(advice.systemic_skill_gaps), 1)
        self.assertIn("Docker", advice.technologies_to_learn)
        self.assertGreaterEqual(len(advice.resume_improvements), 1)

    def test_06_orchestrator_end_to_end(self):
        """Test Agent 6: MultiAgentOrchestrator full workflow execution."""
        orchestrator = MultiAgentOrchestrator()
        result = orchestrator.run(
            resume_source=self.sample_resume,
            user_preferences={"preferred_role": "Full Stack Developer", "location": "Remote", "max_jobs": 3},
            sort_by="Best match"
        )

        self.assertTrue(result.get("success"))
        self.assertIsNotNone(result.get("candidate_profile"))
        self.assertGreater(len(result.get("search_queries", [])), 0)
        self.assertGreater(len(result.get("raw_jobs", [])), 0)
        self.assertGreater(len(result.get("verified_jobs", [])), 0)
        self.assertGreater(len(result.get("matched_jobs", [])), 0)
        self.assertIsNotNone(result.get("career_advice"))
        self.assertGreaterEqual(len(result.get("execution_logs", [])), 5)

if __name__ == "__main__":
    unittest.main()
