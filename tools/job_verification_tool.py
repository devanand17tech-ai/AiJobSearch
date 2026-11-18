"""
Job Verification Tool for URL validation, eligibility extraction, and scam/expiration detection.
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse

def validate_job_url(url: str) -> Tuple[bool, str]:
    """
    Validates whether the application URL is syntactically well-formed and legitimate.
    Returns (is_valid, reason).
    """
    if not url or url.strip() in ["#", "", "None", "null"]:
        return False, "Application URL is missing or placeholder"
    
    clean_url = url.strip()
    try:
        parsed = urlparse(clean_url)
        if not (parsed.scheme in ["http", "https"] and parsed.netloc):
            return False, "URL does not contain a valid http/https scheme or domain"
        
        # Check for placeholder or invalid domains
        if parsed.netloc.lower() in ["example.com", "localhost", "127.0.0.1", "test.com"]:
            # Note: Demo jobs might use example.com, which is valid for demo mode but flagged
            return True, "Demo/example domain"
            
        return True, "Valid external application URL"
    except Exception as e:
        return False, f"Malformed URL syntax: {str(e)}"

def extract_experience_bounds(text: str) -> Tuple[float, Optional[float], str]:
    """
    Extracts min and max experience years from job text.
    Returns (min_years, max_years, evidence_snippet).
    """
    lower = text.lower()

    # Check for fresher / entry level / 0 years explicitly
    if re.search(r'\b(fresher|entry[- ]level|intern|trainee|no experience required|0\s*years?)\b', lower):
        return 0.0, 1.0, "Identified as entry-level / fresher position (0-1 yrs)"

    # Pattern: "X to Y years" or "X-Y years"
    range_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:to|-|–)\s*(\d+(?:\.\d+)?)\s*years?', lower)
    if range_match:
        try:
            min_y = float(range_match.group(1))
            max_y = float(range_match.group(2))
            snippet = range_match.group(0)
            return min_y, max_y, f"Extracted requirement: {snippet}"
        except ValueError:
            pass

    # Pattern: "X+ years" or "at least X years" or "minimum X years"
    plus_match = re.search(r'(?:at least|minimum|min)?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?', lower)
    if plus_match:
        try:
            min_y = float(plus_match.group(1))
            snippet = plus_match.group(0)
            return min_y, None, f"Extracted requirement: {snippet}"
        except ValueError:
            pass

    return 0.0, None, "No explicit experience bounds specified in text"

def extract_graduation_years(text: str) -> List[int]:
    """
    Extracts graduation batch / year restrictions (e.g. 2023, 2024, 2025, 2026).
    """
    batches = []
    # Match patterns like: "2024 / 2025 batch", "2023 or 2024 passout", "Class of 2025"
    pattern = r'\b(202[0-9])\b\s*(?:batch|passout|graduates?|passouts?|candidates?|or|and|\/)?'
    matches = re.finditer(pattern, text, re.IGNORECASE)
    for m in matches:
        try:
            year = int(m.group(1))
            if 2018 <= year <= 2028 and year not in batches:
                batches.append(year)
        except ValueError:
            continue
    return sorted(batches)

def extract_deadline(text: str) -> Optional[str]:
    """
    Extracts application deadline date if explicitly mentioned in the text.
    """
    lower = text.lower()
    # Check for patterns like "deadline: DD/MM/YYYY", "apply before Nov 30, 2026", "last date: 2026-12-01"
    patterns = [
        r'(?:deadline|last date to apply|apply before|closing date)[:\s]+([a-zA-Z]+\s+\d{1,2},?\s+\d{4})',
        r'(?:deadline|last date to apply|apply before|closing date)[:\s]+(\d{4}-\d{2}-\d{2})',
        r'(?:deadline|last date to apply|apply before|closing date)[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})'
    ]
    for p in patterns:
        m = re.search(p, lower)
        if m:
            return m.group(1).strip()
    return None

def audit_job_listing(job_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs comprehensive rule-based verification audit of a raw job listing.
    """
    title = job_dict.get("title", "")
    company = job_dict.get("company", "")
    url = job_dict.get("url", "")
    description = job_dict.get("description", "")
    full_text = f"{title} {description} {job_dict.get('experience', '')}"

    flags = []
    evidence = {}

    # 1. URL validity
    is_url_valid, url_reason = validate_job_url(url)
    evidence["url_validation"] = url_reason
    if not is_url_valid:
        flags.append(f"Invalid URL: {url_reason}")

    # 2. Check for expired listings
    lower_desc = description.lower()
    is_expired = False
    if any(phrase in lower_desc for phrase in [
        "this job has expired",
        "job is closed",
        "no longer accepting applications",
        "position filled"
    ]):
        is_expired = True
        flags.append("Listing explicitly marked as closed or expired in description")

    # 3. Check for suspicious / unverifiable signals
    is_suspicious = False
    if not company or company.lower() in ["company confidential", "confidential", "unknown"]:
        flags.append("Hiring company is listed as confidential or anonymous")
    
    if len(description.strip()) < 50:
        flags.append("Description is unusually sparse or empty")

    # 4. Extract experience bounds
    min_exp, max_exp, exp_evidence = extract_experience_bounds(full_text)
    evidence["experience_evidence"] = exp_evidence

    # 5. Extract graduation years
    grad_years = extract_graduation_years(full_text)
    if grad_years:
        evidence["graduation_years"] = f"Eligible batches detected: {grad_years}"

    # 6. Extract deadline
    deadline = extract_deadline(full_text)
    if deadline:
        evidence["deadline"] = f"Application deadline: {deadline}"

    # 7. Synthesize status
    if is_expired:
        status = "EXPIRED"
    elif is_suspicious:
        status = "SUSPICIOUS"
    elif flags:
        status = "FLAGGED"
    else:
        status = "VERIFIED"

    # Build eligibility criteria bullets
    eligibility_criteria = []
    if min_exp == 0.0 and max_exp == 1.0:
        eligibility_criteria.append("Open to freshers and entry-level candidates (0-1 yrs)")
    elif min_exp > 0:
        exp_str = f"Requires at least {min_exp} years experience"
        if max_exp:
            exp_str += f" (up to {max_exp} years)"
        eligibility_criteria.append(exp_str)
    
    if grad_years:
        eligibility_criteria.append(f"Restricted to graduation batches: {', '.join(map(str, grad_years))}")
    
    if deadline:
        eligibility_criteria.append(f"Deadline: {deadline}")

    return {
        "is_url_valid": is_url_valid,
        "min_experience_years": min_exp,
        "max_experience_years": max_exp,
        "graduation_years_accepted": grad_years,
        "application_deadline": deadline,
        "verification_status": status,
        "verification_flags": flags,
        "verification_evidence": evidence,
        "eligibility_criteria": eligibility_criteria
    }
