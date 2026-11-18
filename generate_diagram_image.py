"""
Generates a crisp, high-resolution 16:9 (1920x1080) presentation-grade architecture
and data flow diagram for PowerPoint presentations.
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_architecture_diagram(output_path="architecture_diagram.png"):
    width = 1920
    height = 1080
    
    # 1. Canvas setup (Clean subtle gradient background)
    img = Image.new("RGB", (width, height), color="#0F172A") # Slate dark background for premium look
    draw = ImageDraw.Draw(img)

    # Try to load Windows system fonts or default
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 36)
        font_subtitle = ImageFont.truetype("arial.ttf", 20)
        font_header = ImageFont.truetype("arialbd.ttf", 22)
        font_sub = ImageFont.truetype("arialbd.ttf", 16)
        font_text = ImageFont.truetype("arial.ttf", 15)
        font_badge = ImageFont.truetype("arialbd.ttf", 13)
        font_small = ImageFont.truetype("arial.ttf", 13)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = font_title
        font_header = font_title
        font_sub = font_title
        font_text = font_title
        font_badge = font_title
        font_small = font_title

    # --- TOP HEADER ---
    draw.rectangle([(0, 0), (width, 100)], fill="#1E293B")
    draw.line([(0, 100), (width, 100)], fill="#334155", width=2)
    draw.text((60, 22), "MULTI-AGENT AI JOB SEARCH SYSTEM", fill="#60A5FA", font=font_title)
    draw.text((60, 65), "End-to-End System Architecture & Autonomous Agentic Data Flow (LangGraph + OpenAI + Pydantic)", fill="#94A3B8", font=font_subtitle)

    # Helper: Draw rounded card
    def draw_card(box, bg_color, border_color, border_width=2, radius=12):
        draw.rounded_rectangle(box, radius=radius, fill=bg_color, outline=border_color, width=border_width)

    # Helper: Draw Arrow
    def draw_arrow(start, end, color="#64748B", width=3):
        draw.line([start, end], fill=color, width=width)
        # arrowhead
        x2, y2 = end
        x1, y1 = start
        if x2 > x1: # pointing right
            draw.polygon([(x2, y2), (x2 - 10, y2 - 6), (x2 - 10, y2 + 6)], fill=color)
        elif y2 > y1: # pointing down
            draw.polygon([(x2, y2), (x2 - 6, y2 - 10), (x2 + 6, y2 - 10)], fill=color)
        elif x2 < x1: # pointing left
            draw.polygon([(x2, y2), (x2 + 10, y2 - 6), (x2 + 10, y2 + 6)], fill=color)
        elif y2 < y1: # pointing up
            draw.polygon([(x2, y2), (x2 - 6, y2 + 10), (x2 + 6, y2 + 10)], fill=color)

    # ==========================================
    # SECTION 1: USER INPUT & PREFERENCES (Left)
    # ==========================================
    user_box = (60, 140, 360, 480)
    draw_card(user_box, "#1E293B", "#38BDF8", border_width=2)
    draw.rectangle([(60, 140), (360, 190)], fill="#0284C7")
    draw.text((80, 153), "👤 USER INPUT LAYER", fill="#FFFFFF", font=font_header)

    draw.text((80, 210), "1. Resume File (PDF)", fill="#F8FAFC", font=font_sub)
    draw.text((80, 235), "• PyMuPDF text parsing\n• Page extraction\n• Unstructured text", fill="#94A3B8", font=font_text)

    draw.text((80, 310), "2. Search Preferences", fill="#F8FAFC", font=font_sub)
    draw.text((80, 335), "• Target Role (e.g. Java Dev)\n• Location (e.g. Remote/City)\n• Workplace (Remote/Hybrid)\n• Max Job Results", fill="#94A3B8", font=font_text)

    draw.text((80, 425), "3. Execution Trigger", fill="#F8FAFC", font=font_sub)
    draw.text((80, 450), "• Streamlit UI / CLI Runner", fill="#38BDF8", font=font_text)

    # ==========================================
    # SECTION 2: CENTRAL ORCHESTRATOR (Center Top)
    # ==========================================
    orch_box = (420, 140, 1460, 280)
    draw_card(orch_box, "#1E1B4B", "#818CF8", border_width=2)
    draw.rectangle([(420, 140), (1460, 190)], fill="#4F46E5")
    draw.text((440, 153), "⚙️ AGENT 6: CENTRAL ORCHESTRATOR (LangGraph StateGraph Engine)", fill="#FFFFFF", font=font_header)

    draw.text((440, 205), "Coordinates Autonomous Specialist Workflow via Shared State (AgentWorkflowState):", fill="#C7D2FE", font=font_sub)
    draw.text((440, 235), "• Directed Graph Transitions (Resume Analysis ➔ Job Search ➔ Verification ➔ Matching ➔ Career Advisor)\n• Real-Time Event Callbacks to Streamlit UI  |  Execution Trace Logs  |  Fault-Tolerant Exception Handling", fill="#A5B4FC", font=font_text)

    # Arrow from User to Orchestrator
    draw_arrow((360, 210), (420, 210), color="#38BDF8")

    # ==========================================
    # SECTION 3: THE 5 SPECIALIST AGENTS (Middle Row)
    # ==========================================
    agent_width = 280
    agent_height = 420
    y_agent = 330
    x_starts = [60, 360, 660, 960, 1260]

    agents_data = [
        {
            "num": "AGENT 1",
            "name": "Resume Analysis",
            "color": "#0284C7",
            "border": "#38BDF8",
            "tool": "Tool: PyMuPDF Parser",
            "prompt": "Prompt: RESUME_PARSER",
            "tasks": [
                "• Extracts raw text cleanly",
                "• Discovers tech skills & tools",
                "• Parses graduation batch year",
                "• Extracts total experience yrs",
                "• Identifies weak/missing skills"
            ],
            "output": "CandidateProfile (Pydantic)"
        },
        {
            "num": "AGENT 2",
            "name": "Job Search Agent",
            "color": "#0D9488",
            "border": "#2DD4BF",
            "tool": "Tool: Apify Job Scraper",
            "prompt": "Prompt: SEARCH_QUERY",
            "tasks": [
                "• Plans 4-6 targeted queries",
                "• Fresher & entry-level targeting",
                "• Queries live Apify actor",
                "• Demo fallback database",
                "• Collects titles, pay, & URLs"
            ],
            "output": "List[RawJobListing]"
        },
        {
            "num": "AGENT 3",
            "name": "Job Verification",
            "color": "#D97706",
            "border": "#FBBF24",
            "tool": "Tool: Verification Auditor",
            "prompt": "Prompt: VERIFICATION",
            "tasks": [
                "• Validates application URLs",
                "• URL & Composite deduplication",
                "• Extracts min/max exp bounds",
                "• Identifies grad-year batches",
                "• Flags expired & scam listings"
            ],
            "output": "List[VerifiedJob]"
        },
        {
            "num": "AGENT 4",
            "name": "Job Matching Agent",
            "color": "#7C3AED",
            "border": "#A78BFA",
            "tool": "Engine: 4-Factor Weighted",
            "prompt": "Prompt: MATCHING_EVAL",
            "tasks": [
                "• Skill Overlap Score (50 pts)",
                "• Experience Match (20 pts)",
                "• Title Fit (15 pts) & Loc (15 pts)",
                "• Status: Eligible/Marginal/Inelig",
                "• Transparent fit explanation"
            ],
            "output": "List[MatchedJob]"
        },
        {
            "num": "AGENT 5",
            "name": "Career Advisor Agent",
            "color": "#DB2777",
            "border": "#F472B6",
            "tool": "Engine: Market Gap Analyzer",
            "prompt": "Prompt: ADVISOR_PROMPT",
            "tasks": [
                "• Priority Application Queue",
                "• Systemic market skill gaps",
                "• Recommends tech roadmap",
                "• Concrete resume advice",
                "• Executive strategic summary"
            ],
            "output": "CareerAdvice (Pydantic)"
        }
    ]

    for i, a in enumerate(agents_data):
        x = x_starts[i]
        box = (x, y_agent, x + agent_width, y_agent + agent_height)
        draw_card(box, "#1E293B", a["border"], border_width=2)
        
        # Header banner
        draw.rectangle([(x, y_agent), (x + agent_width, y_agent + 45)], fill=a["color"])
        draw.text((x + 15, y_agent + 12), f"{a['num']}: {a['name']}", fill="#FFFFFF", font=font_sub)

        # Tool & Prompt pills
        draw.text((x + 15, y_agent + 60), a["tool"], fill="#E2E8F0", font=font_badge)
        draw.text((x + 15, y_agent + 85), a["prompt"], fill=a["border"], font=font_badge)
        draw.line([(x + 15, y_agent + 110), (x + agent_width - 15, y_agent + 110)], fill="#334155", width=1)

        # Responsibilities
        y_text = y_agent + 125
        for task in a["tasks"]:
            draw.text((x + 15, y_text), task, fill="#CBD5E1", font=font_text)
            y_text += 32

        # Output badge at bottom
        draw.rectangle([(x + 10, y_agent + agent_height - 55), (x + agent_width - 10, y_agent + agent_height - 15)], fill="#0F172A", outline=a["border"], width=1)
        draw.text((x + 18, y_agent + agent_height - 43), f"Output: {a['output']}", fill="#38BDF8", font=font_small)

        # Draw arrow to next agent
        if i < len(agents_data) - 1:
            draw_arrow((x + agent_width, y_agent + 200), (x_starts[i+1], y_agent + 200), color="#64748B", width=3)

    # Downward arrow from Orchestrator to Agent 1
    draw_arrow((600, 280), (600, 330), color="#818CF8", width=3)

    # ==========================================
    # SECTION 4: STREAMLIT UI & OUTPUT (Bottom)
    # ==========================================
    ui_box = (60, 780, 1860, 1020)
    draw_card(ui_box, "#0F172A", "#10B981", border_width=2)
    draw.rectangle([(60, 780), (1860, 825)], fill="#059669")
    draw.text((80, 793), "💻 STREAMLIT INTERACTIVE USER DASHBOARD (Presentation & Delivery Layer)", fill="#FFFFFF", font=font_header)

    tabs = [
        ("💼 Tab 1: Recommended Jobs", "Verified listings, match score badges (88%), eligibility status (Eligible), matched vs missing skills, & direct apply links."),
        ("🧭 Tab 2: Career Advisor Guidance", "Application priority queue (#1, #2), systemic market skill gaps, high-ROI tech roadmap, & resume optimization suggestions."),
        ("👤 Tab 3: Candidate Profile", "Extracted credentials, graduation year, target roles, weak skills, and formulated search queries."),
        ("📜 Tab 4: Agent Audit Trace Logs", "Complete chronological audit trail showing agent execution durations, status, and state transitions.")
    ]

    x_tab = 80
    tab_w = 420
    for title, desc in tabs:
        tbox = (x_tab, 845, x_tab + tab_w, 995)
        draw_card(tbox, "#1E293B", "#334155", border_width=1)
        draw.text((x_tab + 15, 860), title, fill="#34D399", font=font_sub)
        
        # Word wrap description
        lines = []
        words = desc.split()
        cur_line = []
        for w in words:
            if len(" ".join(cur_line + [w])) < 42:
                cur_line.append(w)
            else:
                lines.append(" ".join(cur_line))
                cur_line = [w]
        if cur_line:
            lines.append(" ".join(cur_line))
            
        y_d = 890
        for l in lines:
            draw.text((x_tab + 15, y_d), l, fill="#94A3B8", font=font_small)
            y_d += 20
            
        x_tab += 445

    # Connect Agent 5 to UI
    draw_arrow((1400, 750), (1400, 780), color="#F472B6", width=3)

    # Save to disk
    img.save(output_path, "PNG", quality=95)
    print(f"[Success] Architecture diagram saved at: {output_path}")

if __name__ == "__main__":
    create_architecture_diagram("architecture_diagram.png")
