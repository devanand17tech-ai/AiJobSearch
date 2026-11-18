"""
Agent 3: Job Verification Agent
Audits raw listings for URL validity, duplicate removal, eligibility rules, and flags suspicious/expired items.
"""
import os
import json
import re
from typing import List, Dict, Any, Optional

from models.schemas import RawJobListing, VerifiedJob, VerificationStatus
from tools.job_verification_tool import audit_job_listing
from prompts.verification_prompt import VERIFICATION_SYSTEM_PROMPT, VERIFICATION_USER_PROMPT

class JobVerificationAgent:
    """
    Specialist agent responsible for validating and auditing raw job listings.
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
                print(f"[JobVerificationAgent] OpenAI client init failed: {e}")

    def is_llm_configured(self) -> bool:
        return bool(self.api_key and self.client is not None and len(self.api_key) > 5)

    def verify_jobs(self, raw_jobs: List[RawJobListing]) -> List[VerifiedJob]:
        """
        Audits all raw listings, performs deduplication, and returns verified job listings.
        """
        seen_urls = set()
        seen_composites = set()
        verified_results: List[VerifiedJob] = []

        for raw in raw_jobs:
            url_clean = raw.url.strip().lower()
            composite = f"{raw.title.strip().lower()}|{raw.company.strip().lower()}|{raw.location.strip().lower()}"

            is_duplicate = False
            # Deduplication check
            if url_clean and url_clean != "#" and url_clean in seen_urls:
                is_duplicate = True
            elif composite in seen_composites:
                is_duplicate = True

            if url_clean and url_clean != "#":
                seen_urls.add(url_clean)
            seen_composites.add(composite)

            if is_duplicate:
                # Mark as duplicate verified job and continue or record
                v_job = VerifiedJob(
                    raw_job=raw,
                    is_url_valid=(url_clean != "#"),
                    is_duplicate=True,
                    verification_status=VerificationStatus.FLAGGED,
                    verification_flags=["Duplicate listing detected across search queries"]
                )
                verified_results.append(v_job)
                continue

            # Perform audit on unique listing
            audit_result = self._audit_single_job(raw)

            # Map verification status enum
            raw_status = audit_result.get("verification_status", "VERIFIED").upper()
            try:
                v_status = VerificationStatus(raw_status)
            except ValueError:
                v_status = VerificationStatus.VERIFIED

            v_job = VerifiedJob(
                raw_job=raw,
                is_url_valid=audit_result.get("is_url_valid", True),
                is_duplicate=False,
                eligibility_criteria=audit_result.get("eligibility_criteria", []),
                min_experience_years=float(audit_result.get("min_experience_years", 0.0)),
                max_experience_years=audit_result.get("max_experience_years"),
                graduation_years_accepted=audit_result.get("graduation_years_accepted", []),
                application_deadline=audit_result.get("application_deadline"),
                verification_status=v_status,
                verification_flags=audit_result.get("verification_flags", []),
                verification_evidence=audit_result.get("verification_evidence", {})
            )
            verified_results.append(v_job)

        return verified_results

    def _audit_single_job(self, raw: RawJobListing) -> Dict[str, Any]:
        """Runs rule-based audit and optionally enhances via LLM if available."""
        # Baseline rule-based audit
        audit = audit_job_listing(raw.model_dump())

        # If LLM configured, use LLM reasoning to confirm eligibility & deadline extraction
        if self.is_llm_configured() and len(raw.description.strip()) > 50:
            try:
                prompt = VERIFICATION_USER_PROMPT.format(
                    title=raw.title,
                    company=raw.company,
                    location=raw.location,
                    salary=raw.salary,
                    experience=raw.experience,
                    url=raw.url,
                    description=raw.description[:2000]
                )
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": VERIFICATION_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                llm_audit = json.loads(response.choices[0].message.content.strip())

                # Blend LLM findings without inventing missing info
                if "min_experience_years" in llm_audit and isinstance(llm_audit["min_experience_years"], (int, float)):
                    audit["min_experience_years"] = float(llm_audit["min_experience_years"])
                if "max_experience_years" in llm_audit and isinstance(llm_audit["max_experience_years"], (int, float)):
                    audit["max_experience_years"] = float(llm_audit["max_experience_years"])
                if llm_audit.get("graduation_years_accepted"):
                    audit["graduation_years_accepted"] = list(set(audit.get("graduation_years_accepted", []) + llm_audit["graduation_years_accepted"]))
                if llm_audit.get("application_deadline") and llm_audit["application_deadline"] not in ["null", "None"]:
                    audit["application_deadline"] = str(llm_audit["application_deadline"])
                if llm_audit.get("eligibility_criteria"):
                    for crit in llm_audit["eligibility_criteria"]:
                        if crit not in audit["eligibility_criteria"]:
                            audit["eligibility_criteria"].append(crit)
                if llm_audit.get("verification_flags"):
                    for flag in llm_audit["verification_flags"]:
                        if flag not in audit["verification_flags"]:
                            audit["verification_flags"].append(flag)
                if llm_audit.get("verification_status") in ["FLAGGED", "SUSPICIOUS", "EXPIRED"]:
                    audit["verification_status"] = llm_audit["verification_status"]

            except Exception as e:
                print(f"[JobVerificationAgent Warning] LLM verification failed: {e}. Kept rule-based audit.")

        return audit
