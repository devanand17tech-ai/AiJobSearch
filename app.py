import os
import streamlit as st
from dotenv import load_dotenv

from agent.agent import JobSearchAgent
from memory.memory import UserPreferenceMemory

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="AI Job Search Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium AI Product Look & Feel
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    /* Main container background & font styling */
    .stApp {
        background: #ffffff;
        color: #1f2937;
        font-family: 'DM Sans', sans-serif;
    }

    .block-container {
        max-width: 1380px;
        padding: 2.5rem 3rem 5rem;
    }

    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: 0;
    }

    [data-testid="stSidebar"] {
        background: #f7f9fc;
        border-right: 1px solid #e5e7eb;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #111827;
    }

    [data-testid="stFileUploader"] {
        border: 1px dashed #93c5fd;
        border-radius: 14px;
        background: #f8fbff;
        padding: 0.7rem;
    }

    [data-testid="stFileUploader"] section {
        border: 0;
        background: transparent;
    }

    div.stButton > button,
    div.stDownloadButton > button,
    div[data-testid="stLinkButton"] > a {
        border-radius: 9px;
        border: 1px solid #bfdbfe;
        font-weight: 700;
        transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
    }

    div.stButton > button:hover,
    div.stDownloadButton > button:hover,
    div[data-testid="stLinkButton"] > a:hover {
        transform: translateY(-1px);
        border-color: #2563eb;
        box-shadow: 0 5px 14px rgba(37, 99, 235, 0.14);
    }
    
    /* Header Gradient Banner */
    .main-header {
        background: #f1f6ff;
        padding: 2.6rem 2rem 2.3rem;
        border-radius: 14px;
        border: 1px solid #dbeafe;
        box-shadow: 0 8px 24px rgba(30, 64, 175, 0.08);
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .main-header h1 {
        font-size: clamp(2.2rem, 5vw, 3.8rem);
        font-weight: 800;
        background: linear-gradient(90deg, #1d4ed8 0%, #2563eb 48%, #0891b2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: #4b5563;
        font-size: 1.15rem;
        font-weight: 400;
        margin: 0;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: #ffffff;
        backdrop-filter: blur(10px);
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(78, 168, 222, 0.4);
    }

    /* Job Card Styling */
    .job-card {
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        border-left: 5px solid #2563eb;
        padding: 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.07);
    }
    
    .job-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.2rem;
    }

    .job-company {
        font-size: 1.05rem;
        color: #374151;
        font-weight: 600;
    }

    .job-meta {
        font-size: 0.9rem;
        color: #6b7280;
        margin: 0.5rem 0;
    }

    /* Match Score Badges */
    .score-badge-high {
        background: linear-gradient(90deg, #0e7490 0%, #15803d 100%);
        color: #ffffff;
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
    }
    
    .score-badge-med {
        background: linear-gradient(90deg, #b45309 0%, #c2410c 100%);
        color: #ffffff;
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
    }

    /* Skill Tags */
    .skill-tag-matched {
        background-color: rgba(72, 187, 120, 0.15);
        color: #68d391;
        border: 1px solid rgba(72, 187, 120, 0.3);
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.82rem;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
        display: inline-block;
    }

    .skill-tag-missing {
        background-color: rgba(229, 62, 62, 0.15);
        color: #fc8181;
        border: 1px solid rgba(229, 62, 62, 0.3);
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.82rem;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
        display: inline-block;
    }

    /* Notice Banner */
    .notice-unconfigured {
        background-color: rgba(237, 137, 54, 0.12);
        border: 1px solid rgba(237, 137, 54, 0.4);
        color: #fbd38d;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    
    .notice-live {
        background-color: rgba(72, 187, 120, 0.12);
        border: 1px solid rgba(72, 187, 120, 0.4);
        color: #9ae6b4;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }

    .demo-tag {
        background-color: #e53e3e;
        color: white;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State & Memory
if "memory" not in st.session_state:
    st.session_state.memory = UserPreferenceMemory()
if "agent_result" not in st.session_state:
    st.session_state.agent_result = None

memory_prefs = st.session_state.memory.get_preferences()

# Sidebar: Credentials & Customization
with st.sidebar:
    st.image("https://img.icons8.com/isometric-line/100/4ea8de/robot-2.png", width=70)
    st.title("Settings & APIs")
    
    st.markdown("### 🔑 API Configurations")
    
    openai_key_input = st.text_input(
        "OpenAI API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="Used for candidate profile understanding and match rationale."
    )
    
    apify_token_input = st.text_input(
        "Apify API Token",
        value=os.getenv("APIFY_API_TOKEN", ""),
        type="password",
        help="Used to fetch live job listings from web sources."
    )
    
    # Credentials Status Indicators
    openai_key_input = openai_key_input.strip()
    apify_token_input = apify_token_input.strip()
    has_openai = bool(openai_key_input and len(openai_key_input) > 5)
    has_apify = bool(apify_token_input and len(apify_token_input) > 5)
    
    st.markdown("**Status:**")
    st.markdown(f"- OpenAI LLM: {'🟢 Configured' if has_openai else '🟡 Heuristic Fallback'}")
    st.markdown(f"- Apify Live Scraper: {'🟢 Configured' if has_apify else '🔴 Not Configured'}")

    st.divider()

    st.markdown("### 🎯 Search Preferences")
    pref_role = st.text_input("Target Job Role", value=memory_prefs.get("preferred_role", ""), placeholder="e.g. Java Backend Developer")
    pref_location = st.text_input("Location", value=memory_prefs.get("location", ""), placeholder="e.g. Bangalore, Remote")
    pref_type = st.selectbox("Workplace Type", ["Any", "Remote Only", "Hybrid / Onsite"], index=0)
    pref_exp = st.selectbox("Experience Level", ["Any", "Junior (0-2 yrs)", "Mid (2-5 yrs)", "Senior (5+ yrs)"], index=0)
    max_jobs_slider = st.slider("Max Job Count per Query", min_value=3, max_value=15, value=5)
    
    st.divider()
    
    st.markdown("### 🎛️ Filter & Sort Results")
    min_score_filter = st.slider("Minimum Match Score (%)", min_value=0, max_value=90, value=0, step=5)
    sort_by_option = st.selectbox("Sort Recommendations By", ["Best match", "Newest"])

# Main Dashboard Header
st.markdown("""
<div class="main-header">
    <h1>AI Job Search Agent</h1>
    <p>Upload your resume. Let AI parse, match, and rank the best live job opportunities for you.</p>
</div>
""", unsafe_allow_html=True)

# Status Banner for Live Search Configuration
if has_apify:
    st.markdown("""
    <div class="notice-live">
        ✅ <b>Live Job Search Active:</b> Connected to Apify Job Sources API. Real listings will be fetched live!
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="notice-unconfigured">
        ⚠️ <b>Live job search is not configured.</b><br>
        <i>To search real live listings, add your <code>APIFY_API_TOKEN</code> in the sidebar. Demo mode is active so you can test the full agent pipeline.</i>
    </div>
    """, unsafe_allow_html=True)

# Main UI layout: Two columns (Resume Upload & Agent Execution)
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📄 Step 1: Upload Resume")
    uploaded_file = st.file_uploader("Upload candidate resume in PDF format", type=["pdf"])

    if uploaded_file is not None:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": f"{uploaded_file.size / 1024:.1f} KB"}
        
        # Validation checks
        if uploaded_file.size == 0:
            st.error("Uploaded PDF file is empty (0 bytes). Please select a valid resume.")
        elif uploaded_file.size > 10 * 1024 * 1024:  # 10 MB limit
            st.error("File size exceeds 10 MB limit.")
        else:
            st.success("Resume uploaded successfully.")

with col2:
    st.markdown("### 🚀 Step 2: Run Job Agent")
    st.markdown("The AI Agent will extract your skills, plan search queries, evaluate job fit, and rank recommendations.")
    
    run_button = st.button("🤖 Launch AI Agent Job Search", type="primary", use_container_width=True, disabled=(uploaded_file is None))

# Execution Logic
if run_button and uploaded_file is not None:
    st.divider()
    st.markdown("### ⚙️ Agent State & Progress Tracker")
    
    # Progress UI Container
    status_container = st.container()
    
    with status_container:
        agent = JobSearchAgent(openai_api_key=openai_key_input, apify_token=apify_token_input)
        
        user_prefs = {
            "preferred_role": pref_role,
            "location": pref_location,
            "job_type": pref_type,
            "experience_level": pref_exp,
            "max_jobs": max_jobs_slider
        }
        
        with st.spinner("Agent running workflow stages..."):
            result = agent.run_pipeline(
                resume_source=uploaded_file,
                user_preferences=user_prefs,
                sort_by=sort_by_option,
                min_score=min_score_filter
            )
            st.session_state.agent_result = result

# Display Results if available
if st.session_state.agent_result:
    res = st.session_state.agent_result
    
    if not res.get("success"):
        st.error(f"Execution Error: {res.get('error')}")
    else:
        # Display Agent History Log
        st.markdown("#### 📜 Execution History Log")
        history = res.get("history", [])
        cols = st.columns(len(history) if len(history) <= 6 else 6)
        for idx, entry in enumerate(history):
            col_idx = idx % 6
            with cols[col_idx]:
                st.caption(f"**{entry['state']}**")
                st.text(entry['timestamp'])

        st.divider()

        # Display Candidate Profile
        st.markdown("### 👤 Candidate Profile (Parsed by AI)")
        profile = res.get("profile", {})
        
        with st.expander("🔍 View Raw Extracted Resume Text"):
            st.text(res.get("resume_text", ""))

        prof_col1, prof_col2 = st.columns([1, 1])
        with prof_col1:
            st.markdown(f"**Name:** {profile.get('name', 'Candidate')}")
            st.markdown(f"**Experience Level:** {profile.get('experience_level', 'Not specified')}")
            st.markdown(f"**Preferred Roles:** {', '.join(profile.get('preferred_roles', []))}")
        with prof_col2:
            st.markdown("**Parsed Skills:**")
            skills_html = "".join([f'<span class="skill-tag-matched">{s}</span>' for s in profile.get("skills", [])])
            st.markdown(skills_html if skills_html else "No specific skills detected.", unsafe_allow_html=True)

        st.divider()

        # Display Search Plan
        st.markdown("### 🎯 Formulated Search Queries")
        search_plan = res.get("search_plan", [])
        st.info("The Agent dynamically generated the following search queries: " + " | ".join([f"`{q}`" for q in search_plan]))

        st.divider()

        # Recommended Jobs Section
        jobs = res.get("jobs", [])
        st.markdown(f"### 💼 Recommended Jobs ({len(jobs)} Opportunities)")
        metadata = res.get("metadata", {})
        if metadata.get("message"):
            st.info(metadata["message"])
        
        if not jobs:
            st.warning("No job opportunities matched the selected filters. Try lowering the minimum match score or expanding location preferences.")
        else:
            for job in jobs:
                match = job.get("match", {})
                score = match.get("score", 0)
                score_class = "score-badge-high" if score >= 80 else "score-badge-med"
                is_demo = job.get("is_demo", False)

                with st.container():
                    st.markdown(f"""
                    <div class="job-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <div class="job-title">{job.get('title')} {'<span class="demo-tag">DEMO DATA</span>' if is_demo else ''}</div>
                                <div class="job-company">🏢 {job.get('company')} &nbsp;|&nbsp; 📍 {job.get('location')}</div>
                            </div>
                            <div>
                                <span class="{score_class}">{score}% Match</span>
                            </div>
                        </div>
                        <div class="job-meta">
                            💼 <b>Type:</b> {job.get('job_type')} &nbsp;|&nbsp; 
                            💰 <b>Salary:</b> {job.get('salary')} &nbsp;|&nbsp; 
                            📅 <b>Posted:</b> {job.get('date_posted')} &nbsp;|&nbsp; 
                            🌐 <b>Source:</b> {job.get('source')}
                        </div>
                        <div style="margin-top: 0.8rem;">
                            <b>Why this job:</b> {match.get('reason')}
                        </div>
                        <div style="margin-top: 0.8rem;">
                            <b>Matched Skills:</b><br>
                            {"".join([f'<span class="skill-tag-matched">✓ {s}</span>' for s in match.get('matched_skills', [])]) or '<span style="color:#a0aec0;">None explicitly matched</span>'}
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <b>Missing Skills:</b><br>
                            {"".join([f'<span class="skill-tag-missing">• {s}</span>' for s in match.get('missing_skills', [])]) or '<span style="color:#a0aec0;">None</span>'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Apply Link Button
                    job_url = job.get("url", "#")
                    if job_url and job_url != "#":
                        st.link_button(f"🔗 Apply / View Job ({job.get('company')})", job_url)
                    else:
                        st.button("🔗 Apply Link Unavailable", disabled=True, key=f"btn_{job.get('title')}_{job.get('company')}")
                    
                    st.markdown("---")
