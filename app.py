import os
import streamlit as st
from dotenv import load_dotenv

from agent.agent import JobSearchAgent
from memory.memory import UserPreferenceMemory

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="Multi-Agent AI Job Search System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Multi-Agent Dashboard
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    .stApp {
        background: #ffffff;
        color: #1f2937;
        font-family: 'DM Sans', sans-serif;
    }

    .block-container {
        max-width: 1400px;
        padding: 2.2rem 3rem 5rem;
    }

    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: -0.01em;
    }

    [data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }

    [data-testid="stFileUploader"] {
        border: 2px dashed #93c5fd;
        border-radius: 12px;
        background: #f8fbff;
        padding: 0.8rem;
    }

    div.stButton > button,
    div.stDownloadButton > button,
    div[data-testid="stLinkButton"] > a {
        border-radius: 8px;
        font-weight: 600;
        transition: all 160ms ease;
    }

    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        padding: 2.4rem 2rem 2rem;
        border-radius: 16px;
        border: 1px solid #bfdbfe;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.07);
        margin-bottom: 1.8rem;
        text-align: center;
    }

    .main-header h1 {
        font-size: clamp(2rem, 4vw, 3.2rem);
        font-weight: 800;
        background: linear-gradient(90deg, #1e40af 0%, #2563eb 50%, #0284c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.4rem;
    }

    .main-header p {
        color: #475569;
        font-size: 1.1rem;
        margin: 0;
    }

    /* Metrics Grid */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
        margin-bottom: 1.8rem;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        text-align: center;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #1e40af;
        margin-bottom: 0.2rem;
        font-family: 'Space Grotesk', sans-serif;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Agent Status Card */
    .agent-pipeline-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 0.8rem;
        margin: 1.2rem 0 1.8rem;
    }

    .agent-status-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.9rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .agent-status-box.active {
        border-color: #3b82f6;
        background: #eff6ff;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.12);
    }

    .agent-name {
        font-weight: 700;
        font-size: 0.92rem;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }

    .agent-state-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .status-success { background: #dcfce7; color: #15803d; }
    .status-running { background: #dbeafe; color: #1d4ed8; }
    .status-pending { background: #f1f5f9; color: #64748b; }
    .status-failed { background: #fee2e2; color: #b91c1c; }

    /* Job Card Styling */
    .job-card {
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #2563eb;
        padding: 1.4rem;
        margin-bottom: 1.3rem;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
    }

    .job-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }

    .job-company {
        font-size: 1.05rem;
        color: #334155;
        font-weight: 600;
    }

    .job-meta {
        font-size: 0.88rem;
        color: #64748b;
        margin: 0.6rem 0;
    }

    /* Badges */
    .score-badge {
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.92rem;
        color: #ffffff;
        display: inline-block;
    }
    .score-high { background: linear-gradient(90deg, #059669 0%, #10b981 100%); }
    .score-med { background: linear-gradient(90deg, #d97706 0%, #f59e0b 100%); }
    .score-low { background: linear-gradient(90deg, #64748b 0%, #94a3b8 100%); }

    .badge-pill {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 14px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-left: 0.4rem;
    }
    .badge-verified { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .badge-flagged { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .badge-eligible { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
    .badge-marginal { background: #fef9c3; color: #854d0e; border: 1px solid #fef08a; }
    .badge-ineligible { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

    /* Skills Tags */
    .skill-tag-matched {
        background: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        font-size: 0.82rem;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
        display: inline-block;
        font-weight: 500;
    }

    .skill-tag-missing {
        background: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        font-size: 0.82rem;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
        display: inline-block;
        font-weight: 500;
    }

    .demo-tag {
        background-color: #ef4444;
        color: white;
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: bold;
        text-transform: uppercase;
    }

    /* Advisor Cards */
    .advisor-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #0284c7;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State & Memory
if "memory" not in st.session_state:
    st.session_state.memory = UserPreferenceMemory()
if "agent_result" not in st.session_state:
    st.session_state.agent_result = None

memory_prefs = st.session_state.memory.get_preferences()

# Sidebar: Configurations & Search Controls
with st.sidebar:
    st.title("🤖 Multi-Agent Settings")
    
    st.markdown("### 🔑 API Credentials")
    openai_key_input = st.text_input(
        "OpenAI API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="Powers LLM reasoning across candidate profiling, verification, matching, and career advice."
    ).strip()
    
    apify_token_input = st.text_input(
        "Apify API Token",
        value=os.getenv("APIFY_API_TOKEN", ""),
        type="password",
        help="Enables live job scraping via Apify actors (Indeed, Google Jobs, etc.)."
    ).strip()
    
    has_openai = bool(openai_key_input and len(openai_key_input) > 5)
    has_apify = bool(apify_token_input and len(apify_token_input) > 5)
    
    st.markdown("**Status:**")
    st.markdown(f"- OpenAI Engine: {'🟢 Configured' if has_openai else '🟡 Heuristic Fallback'}")
    st.markdown(f"- Apify Live Scraper: {'🟢 Configured' if has_apify else '🟡 Demo Job Source'}")

    st.divider()

    st.markdown("### 🎯 Search Preferences")
    pref_role = st.text_input("Target Role", value=memory_prefs.get("preferred_role", ""), placeholder="e.g. Java Backend Developer")
    pref_location = st.text_input("Location", value=memory_prefs.get("location", ""), placeholder="e.g. Bangalore, Remote")
    pref_type = st.selectbox("Workplace Type", ["Any", "Remote Only", "Hybrid / Onsite"], index=0)
    pref_exp = st.selectbox("Experience Level", ["Any", "Entry Level / Fresher (0-1 yrs)", "Junior (1-3 yrs)", "Mid (3-5 yrs)", "Senior (5+ yrs)"], index=0)
    max_jobs_slider = st.slider("Max Results Per Query", min_value=3, max_value=15, value=5)
    
    st.divider()
    
    st.markdown("### 🎛️ Filter & Sort")
    min_score_filter = st.slider("Min Match Score (%)", min_value=0, max_value=90, value=0, step=5)
    sort_by_option = st.selectbox("Sort By", ["Best match", "Newest"])

# Main Header Banner
st.markdown("""
<div class="main-header">
    <h1>Multi-Agent AI Job Search System</h1>
    <p>Autonomous 6-Agent Architecture: Resume Perception • Discovery • Verification • Explainable Matching • Strategic Advisory</p>
</div>
""", unsafe_allow_html=True)

# Apify Status Notice
if has_apify:
    st.info("✅ **Live Job Discovery Active:** Connected to Apify Live Scraper. Active web listings will be queried.")
else:
    st.warning("⚠️ **Live Job Search Not Configured:** Add your `APIFY_API_TOKEN` in the sidebar to search live web listings. Running in demo fallback mode so you can experience the full multi-agent workflow.")

# Two Column Layout: Resume Upload & Agent Launcher
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📄 Step 1: Upload Candidate Resume")
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])

    if uploaded_file is not None:
        if uploaded_file.size == 0:
            st.error("Uploaded PDF is empty (0 bytes).")
        elif uploaded_file.size > 10 * 1024 * 1024:
            st.error("PDF exceeds 10MB limit.")
        else:
            st.success(f"Resume loaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

with col2:
    st.markdown("### 🚀 Step 2: Launch Multi-Agent Workflow")
    st.markdown("The 6 autonomous specialist agents will parse your resume, search listings, audit URLs & eligibility, score compatibility, and generate strategic career advice.")
    run_button = st.button("🚀 Start Multi-Agent Job Search", type="primary", use_container_width=True, disabled=(uploaded_file is None))

# Execution Logic
if run_button and uploaded_file is not None:
    st.divider()
    st.markdown("### ⚙️ Multi-Agent Live Execution Status")

    agent_status_placeholder = st.empty()

    agent = JobSearchAgent(openai_api_key=openai_key_input, apify_token=apify_token_input)
    user_prefs = {
        "preferred_role": pref_role,
        "location": pref_location,
        "job_type": pref_type,
        "experience_level": pref_exp,
        "max_jobs": max_jobs_slider
    }

    with st.status("🤖 Multi-Agent Orchestrator coordinating specialists...", expanded=True) as status_box:
        st.write("🟢 **Agent 1: Resume Analysis Agent** extracting technical competencies, education, and graduation batch...")
        st.write("🟢 **Agent 2: Job Search Agent** generating intelligent queries and querying job sources...")
        st.write("🟢 **Agent 3: Job Verification Agent** auditing URLs, deduplicating, and extracting eligibility constraints...")
        st.write("🟢 **Agent 4: Job Matching Agent** evaluating transparent multi-factor compatibility scores...")
        st.write("🟢 **Agent 5: Career Advisor Agent** synthesizing priority application queue and learning roadmap...")

        result = agent.run_pipeline(
            resume_source=uploaded_file,
            user_preferences=user_prefs,
            sort_by=sort_by_option,
            min_score=min_score_filter
        )
        st.session_state.agent_result = result
        status_box.update(label="✅ Multi-Agent Job Search Completed Successfully!", state="complete", expanded=False)

# Results Display
if st.session_state.agent_result:
    res = st.session_state.agent_result

    if not res.get("success") and not res.get("candidate_profile"):
        st.error(f"Execution Error: {res.get('errors') or res.get('error')}")
    else:
        profile = res.get("profile", {})
        jobs = res.get("jobs", [])
        v_summary = res.get("verification_summary", {})
        advice = res.get("career_advice")
        execution_logs = res.get("execution_logs", [])

        st.divider()

        # 1. Summary Metrics Grid
        total_discovered = len(res.get("verified_jobs", [])) or len(jobs)
        verified_legit = v_summary.get("verified_legitimate", len(jobs))
        flagged_count = v_summary.get("flagged", 0)
        top_score = jobs[0].get("match", {}).get("score", 0) if jobs else 0

        st.markdown(f"""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-value">{total_discovered}</div>
                <div class="metric-label">Total Jobs Discovered</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{verified_legit}</div>
                <div class="metric-label">Verified Legitimate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{flagged_count}</div>
                <div class="metric-label">Flagged Warnings</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{top_score}%</div>
                <div class="metric-label">Top Match Score</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Live Agent Execution Grid
        st.markdown("#### 🤖 Specialist Agent Pipeline Status")
        agent_names = [
            ("Resume Analysis Agent", "Extracted skills & profile"),
            ("Job Search Agent", f"Queried {len(res.get('search_plan', []))} variations"),
            ("Job Verification Agent", f"Audited {total_discovered} listings"),
            ("Job Matching Agent", f"Evaluated compatibility"),
            ("Career Advisor Agent", "Synthesized career roadmap"),
            ("Orchestrator Agent", "Maintained state & coordination")
        ]
        
        agent_cols = st.columns(6)
        for idx, (aname, adesc) in enumerate(agent_names):
            with agent_cols[idx]:
                st.markdown(f"""
                <div class="agent-status-box active">
                    <div class="agent-name">Agent {idx+1}</div>
                    <div style="font-size:0.8rem; color:#475569; margin-bottom:0.3rem;">{aname}</div>
                    <span class="agent-state-badge status-success">COMPLETED</span>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # 3. Main Multi-Tab Interface
        tab_jobs, tab_advisor, tab_profile, tab_trace = st.tabs([
            "💼 Recommended Jobs",
            "🧭 Career Advisor Guidance",
            "👤 Candidate Profile & Queries",
            "📜 Agent Audit & Trace Logs"
        ])

        # TAB 1: RECOMMENDED JOBS
        with tab_jobs:
            st.markdown(f"### 💼 Recommended & Verified Jobs ({len(jobs)} Opportunities)")
            
            if not jobs:
                st.warning("No job opportunities matched the selected filters. Lower your minimum match score or expand your location settings.")
            else:
                for idx, job in enumerate(jobs, 1):
                    match = job.get("match", {})
                    verified = job.get("verified", {})
                    score = match.get("score", 0)
                    score_class = "score-high" if score >= 80 else ("score-med" if score >= 65 else "score-low")
                    is_demo = job.get("is_demo", False)

                    v_status = verified.get("status", "VERIFIED")
                    v_badge_class = "badge-verified" if v_status == "VERIFIED" else "badge-flagged"

                    eligibility = match.get("eligibility_status", "Eligible")
                    elig_class = "badge-eligible" if eligibility == "Eligible" else ("badge-marginal" if eligibility == "Marginal" else "badge-ineligible")

                    with st.container():
                        st.markdown(f"""
                        <div class="job-card">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div>
                                    <div class="job-title">{job.get('title')} {'<span class="demo-tag">DEMO DATA</span>' if is_demo else ''}</div>
                                    <div class="job-company">🏢 {job.get('company')} &nbsp;|&nbsp; 📍 {job.get('location')}</div>
                                </div>
                                <div style="text-align: right;">
                                    <span class="score-badge {score_class}">{score}% Match</span>
                                    <div>
                                        <span class="badge-pill {v_badge_class}">Audit: {v_status}</span>
                                        <span class="badge-pill {elig_class}">{eligibility}</span>
                                    </div>
                                </div>
                            </div>
                            <div class="job-meta">
                                💼 <b>Type:</b> {job.get('job_type')} &nbsp;|&nbsp; 
                                💰 <b>Salary:</b> {job.get('salary')} &nbsp;|&nbsp; 
                                📅 <b>Posted:</b> {job.get('date_posted')} &nbsp;|&nbsp; 
                                🌐 <b>Source:</b> {job.get('source')}
                            </div>
                            <div style="margin-top: 0.6rem; font-size: 0.95rem; color: #1e293b;">
                                <b>Why this job matches:</b> {match.get('reason')}
                            </div>
                            <div style="margin-top: 0.6rem;">
                                <b>Matched Skills:</b><br>
                                {"".join([f'<span class="skill-tag-matched">✓ {s}</span>' for s in match.get('matched_skills', [])]) or '<span style="color:#94a3b8; font-size:0.85rem;">None explicitly matched</span>'}
                            </div>
                            <div style="margin-top: 0.4rem;">
                                <b>Missing Skills:</b><br>
                                {"".join([f'<span class="skill-tag-missing">• {s}</span>' for s in match.get('missing_skills', [])]) or '<span style="color:#10b981; font-size:0.85rem;">No missing skills identified!</span>'}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Action bar for apply link & verification details
                        c_apply, c_details = st.columns([1, 3])
                        with c_apply:
                            job_url = job.get("url", "#")
                            if job_url and job_url != "#":
                                st.link_button(f"🔗 Direct Application Link", job_url, use_container_width=True)
                            else:
                                st.button("🔗 Apply Link Unavailable", disabled=True, key=f"btn_{idx}")
                        
                        with c_details:
                            with st.expander("🔍 View Verification Evidence & Details"):
                                st.write(f"**Experience Requirement:** Min {verified.get('min_exp', 0)} years")
                                if verified.get("criteria"):
                                    st.write(f"**Extracted Eligibility Criteria:** {', '.join(verified.get('criteria', []))}")
                                if verified.get("deadline"):
                                    st.write(f"**Application Deadline:** {verified.get('deadline')}")
                                if verified.get("flags"):
                                    st.warning(f"Audit Flags: {', '.join(verified.get('flags', []))}")

                        st.markdown("---")

        # TAB 2: CAREER ADVISOR GUIDANCE
        with tab_advisor:
            st.markdown("### 🧭 Strategic Career Advisor Recommendations")
            
            if advice:
                advice_dict = advice.model_dump() if hasattr(advice, "model_dump") else advice
                
                # Executive Summary
                st.info(f"💡 **Executive Talent Assessment:**\n\n{advice_dict.get('executive_summary', '')}")
                
                adv_col1, adv_col2 = st.columns([1, 1])

                with adv_col1:
                    st.markdown("#### 🎯 Priority Application Queue")
                    st.caption("Apply to these positions first based on verified legitimacy and compatibility.")
                    
                    priority_apps = advice_dict.get("priority_applications", [])
                    if not priority_apps:
                        st.write("No priority applications identified.")
                    for app in priority_apps:
                        urgency = app.get("apply_urgency", "Normal")
                        urgency_badge = "🔴 High Urgency" if urgency == "High" else "🟡 Medium Urgency"
                        st.markdown(f"""
                        <div class="advisor-box">
                            <div style="display:flex; justify-content:space-between;">
                                <b>#{app.get('priority_rank')} {app.get('title')}</b>
                                <span style="font-size:0.8rem; font-weight:700;">{urgency_badge}</span>
                            </div>
                            <div style="font-size:0.85rem; color:#475569;">🏢 {app.get('company')} | Match: {app.get('match_score')}%</div>
                            <div style="font-size:0.88rem; margin-top:0.4rem;">{app.get('reason_to_apply_first')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if app.get("url") and app.get("url") != "#":
                            st.link_button(f"Apply to {app.get('company')}", app.get("url"), key=f"adv_btn_{app.get('job_id')}")

                with adv_col2:
                    st.markdown("#### 📊 Systemic Market Skill Gaps")
                    st.caption("Skills missing most frequently across active market listings.")
                    
                    for gap in advice_dict.get("systemic_skill_gaps", []):
                        st.markdown(f"""
                        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:0.8rem; margin-bottom:0.6rem;">
                            <div style="display:flex; justify-content:space-between;">
                                <b>{gap.get('skill_name')}</b>
                                <span style="color:#dc2626; font-size:0.82rem; font-weight:700;">Required in {gap.get('demand_frequency')} listings</span>
                            </div>
                            <div style="font-size:0.85rem; color:#334155; margin-top:0.3rem;">{gap.get('learning_recommendation')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("#### 🚀 Recommended Technologies to Learn")
                    tech_html = "".join([f'<span class="skill-tag-matched" style="background:#e0f2fe; color:#0369a1; border-color:#bae6fd;">{t}</span>' for t in advice_dict.get("technologies_to_learn", [])])
                    st.markdown(tech_html if tech_html else "No new technologies needed.", unsafe_allow_html=True)

                    st.markdown("#### 📝 Resume Optimization Tips")
                    for tip in advice_dict.get("resume_improvements", []):
                        st.markdown(f"- ✍️ {tip}")

        # TAB 3: CANDIDATE PROFILE & QUERIES
        with tab_profile:
            st.markdown("### 👤 Candidate Profile (Agent 1 Output)")
            
            p_col1, p_col2 = st.columns([1, 1])
            with p_col1:
                st.markdown(f"**Candidate Name:** {profile.get('name', 'Candidate')}")
                st.markdown(f"**Graduation Year:** {profile.get('graduation_year', 'Not specified')}")
                st.markdown(f"**Experience Level:** {profile.get('experience_level', 'Not specified')}")
                st.markdown(f"**Estimated Experience:** {profile.get('total_years_experience', 0)} years")
                st.markdown(f"**Target Roles:** {', '.join(profile.get('preferred_roles', []))}")
            
            with p_col2:
                st.markdown("**Core Skills:**")
                skills_html = "".join([f'<span class="skill-tag-matched">{s}</span>' for s in profile.get("skills", [])])
                st.markdown(skills_html if skills_html else "No specific skills detected.", unsafe_allow_html=True)

                if profile.get("weak_or_missing_skills"):
                    st.markdown("**Identified Weak / Missing Skills for Role:**")
                    weak_html = "".join([f'<span class="skill-tag-missing">{s}</span>' for s in profile.get("weak_or_missing_skills", [])])
                    st.markdown(weak_html, unsafe_allow_html=True)

            st.divider()

            st.markdown("### 🎯 Formulated Search Queries (Agent 2 Output)")
            search_plan = res.get("search_plan", [])
            st.info("The Job Search Agent dynamically generated these query variations: " + " | ".join([f"`{q}`" for q in search_plan]))

            with st.expander("🔍 View Extracted Resume Plain Text"):
                st.text(res.get("resume_text", ""))

        # TAB 4: AGENT AUDIT & TRACE LOGS
        with tab_trace:
            st.markdown("### 📜 Traceable Multi-Agent Execution History")
            st.caption("Chronological event log maintaining observability across all 6 specialist agents.")
            
            history = res.get("history", [])
            for entry in history:
                st.markdown(f"**`[{entry.get('timestamp')}]` {entry.get('state')}** — {entry.get('message')}")
