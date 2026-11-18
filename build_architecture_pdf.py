from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)


OUTPUT_FILE = "AI_Job_Search_Agent_Architecture_Guide.pdf"
PAGE_WIDTH, PAGE_HEIGHT = letter
INK = colors.HexColor("#172B3A")
TEAL = colors.HexColor("#087E8B")
MINT = colors.HexColor("#DDF3EF")
GOLD = colors.HexColor("#E3A72F")
PAPER = colors.HexColor("#F6F8F7")
MUTED = colors.HexColor("#526573")
LINE = colors.HexColor("#D7E0E2")


class WorkflowDiagram(Flowable):
    def __init__(self, width=7.1 * inch, height=3.65 * inch):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self):
        canvas = self.canv
        boxes = [
            ("1  USER INPUT", "Resume PDF + role, location, filters", TEAL),
            ("2  PERCEPTION", "PyMuPDF extracts readable resume text", INK),
            ("3  REASONING + PLAN", "OpenAI profile + targeted queries; local fallback", TEAL),
            ("4  JOB SEARCH", "Apify Actor + dataset, or labeled demo listings", INK),
            ("5  OBSERVE + NORMALIZE", "Map source fields; deduplicate listings", TEAL),
            ("6  DECIDE", "Rule-based match score, filters, ranking", INK),
            ("7  PRESENT", "Profile, query plan, ranked jobs, links, history", TEAL),
        ]
        box_w = self.width - 0.62 * inch
        box_h = 0.36 * inch
        gap = 0.105 * inch
        x = 0.31 * inch
        y = self.height - box_h
        for index, (title, detail, fill) in enumerate(boxes):
            canvas.setFillColor(fill)
            canvas.roundRect(x, y, box_w, box_h, 5, fill=1, stroke=0)
            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 8.2)
            canvas.drawString(x + 0.12 * inch, y + 0.225 * inch, title)
            canvas.setFont("Helvetica", 7.8)
            canvas.drawRightString(x + box_w - 0.12 * inch, y + 0.225 * inch, detail)
            if index < len(boxes) - 1:
                arrow_x = self.width / 2
                arrow_top = y - 0.01 * inch
                arrow_bottom = y - gap + 0.01 * inch
                canvas.setStrokeColor(GOLD)
                canvas.setLineWidth(1.5)
                canvas.line(arrow_x, arrow_top, arrow_x, arrow_bottom)
                canvas.line(arrow_x, arrow_bottom, arrow_x - 3, arrow_bottom + 4)
                canvas.line(arrow_x, arrow_bottom, arrow_x + 3, arrow_bottom + 4)
            y -= box_h + gap


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=27, leading=31, textColor=INK, alignment=TA_LEFT, spaceAfter=12,
))
styles.add(ParagraphStyle(
    name="Deck", parent=styles["Normal"], fontSize=12, leading=17,
    textColor=MUTED, spaceAfter=12,
))
styles.add(ParagraphStyle(
    name="Section", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=18, leading=22, textColor=INK, spaceBefore=4, spaceAfter=9,
))
styles.add(ParagraphStyle(
    name="Subsection", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=11.5, leading=14, textColor=TEAL, spaceBefore=8, spaceAfter=5,
))
styles.add(ParagraphStyle(
    name="BodySmall", parent=styles["BodyText"], fontSize=9.2, leading=13,
    textColor=INK, spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="BulletSmall", parent=styles["BodyText"], fontSize=9, leading=12.5,
    leftIndent=12, firstLineIndent=-8, textColor=INK, spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="TableHead", parent=styles["BodyText"], fontName="Helvetica-Bold",
    fontSize=8.2, leading=10, textColor=colors.white,
))
styles.add(ParagraphStyle(
    name="TableCell", parent=styles["BodyText"], fontSize=7.8, leading=10.4,
    textColor=INK,
))
styles.add(ParagraphStyle(
    name="Callout", parent=styles["BodyText"], fontName="Helvetica-Bold",
    fontSize=10.3, leading=15, textColor=INK, backColor=MINT,
    borderColor=TEAL, borderWidth=0.7, borderPadding=9, spaceBefore=6, spaceAfter=9,
))
styles.add(ParagraphStyle(
    name="Caption", parent=styles["BodyText"], fontSize=7.8, leading=10,
    textColor=MUTED, alignment=TA_CENTER, spaceBefore=3, spaceAfter=8,
))


def P(text, style="BodySmall"):
    return Paragraph(text, styles[style])


def bullet(text):
    return P("&#8226; " + text, "BulletSmall")


def make_table(rows, widths, header=True):
    table = Table(rows, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), INK),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
        ])
    table.setStyle(TableStyle(commands))
    return table


def on_page(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFillColor(INK)
        canvas.rect(0, PAGE_HEIGHT - 0.38 * inch, PAGE_WIDTH, 0.38 * inch, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(0.68 * inch, PAGE_HEIGHT - 0.245 * inch, "AI JOB SEARCH AGENT  /  ARCHITECTURE FIELD GUIDE")
    canvas.setStrokeColor(LINE)
    canvas.line(0.68 * inch, 0.55 * inch, PAGE_WIDTH - 0.68 * inch, 0.55 * inch)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(0.68 * inch, 0.36 * inch, "Implementation-grounded project explanation")
    canvas.drawRightString(PAGE_WIDTH - 0.68 * inch, 0.36 * inch, f"{doc.page}")
    canvas.restoreState()


doc = BaseDocTemplate(
    OUTPUT_FILE,
    pagesize=letter,
    rightMargin=0.68 * inch,
    leftMargin=0.68 * inch,
    topMargin=0.62 * inch,
    bottomMargin=0.75 * inch,
    title="AI Job Search Agent: Architecture and Data Flow",
    author="AI Job Search Agent Project Guide",
    subject="Architecture, data flow, integrations, and presentation notes",
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])

story = []

# Cover and one-minute overview
story.extend([
    Spacer(1, 0.35 * inch),
    P("PROJECT EXPLAINER  /  TECHNICAL WALKTHROUGH", "Subsection"),
    P("AI Job Search Agent", "CoverTitle"),
    P("Architecture, end-to-end data flow, integrations, scoring logic, and a presentation-ready talk track.", "Deck"),
    P("THE IDEA", "Subsection"),
    P("The application takes a candidate's PDF resume and search preferences, converts them into a structured profile and search plan, gathers job listings, estimates fit, and presents ranked recommendations with links. The Streamlit UI is the front door; a Python agent orchestrates the workflow.", "BodySmall"),
    P("A key distinction: this is a tool-using workflow with optional LLM reasoning, not an autonomous model that controls every decision. Resume parsing and match scoring are largely local Python logic; OpenAI improves profile/query interpretation and explanations; Apify supplies live listings.", "Callout"),
    WorkflowDiagram(),
    P("High-level flow based on the implemented pipeline in agent/agent.py.", "Caption"),
    P("ONE-SENTENCE SUMMARY", "Subsection"),
    P("“The user uploads a resume; the agent extracts and structures candidate data, plans targeted searches, retrieves and cleans listings, computes match scores, then filters and ranks the results for display.”", "Callout"),
    PageBreak(),
])

# Detailed flow
story.extend([
    P("1. End-to-End Data Flow", "Section"),
    P("The central orchestration method is <b>JobSearchAgent.run_pipeline()</b>. It runs these stages in order and records state transitions along the way.", "BodySmall"),
])
flow_rows = [
    [P("STAGE", "TableHead"), P("WHAT HAPPENS", "TableHead"), P("DATA PASSED FORWARD", "TableHead")],
    [P("1. Input / UI", "TableCell"), P("Streamlit accepts a PDF and preferences (role, location, work type, experience, result count). It also accepts optional API keys in the sidebar.", "TableCell"), P("Uploaded file + preference dictionary", "TableCell")],
    [P("2. Resume perception", "TableCell"), P("resume/parser.py uses PyMuPDF to extract text from each page, normalizes whitespace, and rejects unreadable/empty files.", "TableCell"), P("Clean plain-text resume", "TableCell")],
    [P("3. Candidate profile", "TableCell"), P("LLMClient parses text into profile fields. OpenAI is used if configured; otherwise regex/keyword heuristics provide a fallback.", "TableCell"), P("Name, skills, languages, frameworks, roles, experience level, etc.", "TableCell")],
    [P("4. Preference memory", "TableCell"), P("Safe search preferences are saved to user_preferences.json. Raw resume text is not written by this memory class.", "TableCell"), P("Role, location, work type, experience, salary/result settings", "TableCell")],
    [P("5. Search planning", "TableCell"), P("OpenAI proposes 3–5 query strings from profile + preferences. A local rule-based builder is used if the call is unavailable or fails.", "TableCell"), P("Search query list", "TableCell")],
    [P("6. Job acquisition", "TableCell"), P("JobSearchManager runs one Apify Actor search per query concurrently. Without usable live results it can use clearly labeled demo records.", "TableCell"), P("Raw listing dictionaries + source metadata", "TableCell")],
    [P("7. Normalize / deduplicate", "TableCell"), P("Normalizer maps differing source field names to a shared schema and removes duplicate URLs or matching title/company/location combinations.", "TableCell"), P("Consistent unique job records", "TableCell")],
    [P("8. Match / rank", "TableCell"), P("Matcher evaluates skills, role and location; optional OpenAI generates rationale. Ranker applies minimum score/location/remote filters and sort order.", "TableCell"), P("Ranked recommendation records", "TableCell")],
    [P("9. Present", "TableCell"), P("Streamlit displays profile, query plan, job cards, matched/missing skills, score, source, apply/view link, and execution history.", "TableCell"), P("User-facing results; user applies manually", "TableCell")],
]
story.append(make_table(flow_rows, [1.12 * inch, 3.45 * inch, 2.07 * inch]))
story.extend([
    Spacer(1, 9),
    P("Where the data goes", "Subsection"),
    bullet("The PDF is processed locally by PyMuPDF. If an OpenAI key is supplied, resume text (up to 8,000 characters in the profile prompt) is sent to OpenAI for profile extraction. Job descriptions and profile data are sent for optional match explanations."),
    bullet("Search terms and location are sent to the configured Apify Actor when an Apify token is supplied. The Actor's results are read from its Apify dataset."),
    bullet("The local JSON preference file stores a limited allowlist of search settings. It is not a resume database."),
    bullet("The app shows links to listings; it does not submit applications."),
    PageBreak(),
])

# Components and APIs
story.extend([
    P("2. Components and Why They Exist", "Section"),
    P("The code is organized by responsibility so the UI, orchestration, integrations, and decision logic are not all mixed into one file.", "BodySmall"),
])
component_rows = [
    [P("COMPONENT / FILE", "TableHead"), P("RESPONSIBILITY", "TableHead"), P("WHY THIS DESIGN", "TableHead")],
    [P("app.py (Streamlit)", "TableCell"), P("Web interface, upload, preferences, credentials, progress and results.", "TableCell"), P("Streamlit provides a quick Python-native interactive UI without building a separate frontend/API server.", "TableCell")],
    [P("agent/agent.py", "TableCell"), P("Coordinates the ordered workflow and owns pipeline results.", "TableCell"), P("Keeps workflow sequencing and error handling in one place.", "TableCell")],
    [P("agent/tools.py", "TableCell"), P("Thin tool registry/facade for resume, LLM, search, matcher and ranker methods.", "TableCell"), P("The orchestrator calls capabilities through clear methods instead of owning every implementation.", "TableCell")],
    [P("agent/state.py", "TableCell"), P("Enumerates stages and records timestamped history; captures FAILED state on exceptions.", "TableCell"), P("Makes progress inspectable and helps explain/debug a run.", "TableCell")],
    [P("resume/parser.py", "TableCell"), P("PDF-to-text extraction and basic cleaning/validation.", "TableCell"), P("Separates document handling from profile reasoning.", "TableCell")],
    [P("llm/client.py + prompts/", "TableCell"), P("OpenAI requests for structured profile, search query planning, and fit rationale, with local fallbacks for first two tasks.", "TableCell"), P("Centralizes model configuration and reusable prompt text; keeps app usable without an LLM key.", "TableCell")],
    [P("jobs/*", "TableCell"), P("Apify integration, concurrent searches, demo fallback, normalization and deduplication.", "TableCell"), P("Isolates external listing formats and API failure handling from scoring/UI.", "TableCell")],
    [P("matching/*", "TableCell"), P("Deterministic compatibility scoring and result filtering/sorting.", "TableCell"), P("Fast, inspectable decisions; avoids relying on LLM output for the whole ranking.", "TableCell")],
    [P("memory/memory.py", "TableCell"), P("Loads/saves selected search preferences as JSON.", "TableCell"), P("Remembers convenient non-resume settings across app runs.", "TableCell")],
]
story.append(make_table(component_rows, [1.55 * inch, 2.85 * inch, 2.24 * inch]))
story.extend([
    Spacer(1, 9),
    P("External APIs and libraries", "Subsection"),
])
api_rows = [
    [P("TOOL / API", "TableHead"), P("HOW THIS PROJECT USES IT", "TableHead"), P("WHY USE IT", "TableHead")],
    [P("PyMuPDF (pymupdf / fitz)", "TableCell"), P("Opens the uploaded PDF and extracts page text locally.", "TableCell"), P("Purpose-built PDF text extraction; no separate OCR service is called. Image-only scans may yield no text.", "TableCell")],
    [P("OpenAI API / Python SDK", "TableCell"), P("Calls chat.completions.create with configured model (default gpt-4o-mini). JSON response mode is requested for profile and match evaluation.", "TableCell"), P("Turns unstructured resume text into a schema and proposes flexible search queries / natural-language explanations.", "TableCell")],
    [P("Apify API / apify-client", "TableCell"), P("Calls client.actor(actor_id).call(run_input=...) and reads client.dataset(dataset_id).iterate_items(). Actor input varies by configured actor.", "TableCell"), P("Runs a hosted job-scraping Actor and provides its resulting dataset through a consistent client API.", "TableCell")],
    [P("Streamlit", "TableCell"), P("Renders the app, PDF uploader, controls, status and result cards.", "TableCell"), P("Fast way to deliver an interactive Python application for a demo/prototype.", "TableCell")],
    [P("python-dotenv", "TableCell"), P("Loads optional .env values for keys and configuration.", "TableCell"), P("Keeps local configuration out of source code; UI key entry is also supported.", "TableCell")],
]
story.append(make_table(api_rows, [1.42 * inch, 3.25 * inch, 1.97 * inch]))
story.extend([
    Spacer(1, 7),
    P("Configuration names: OPENAI_API_KEY, OPENAI_MODEL, APIFY_API_TOKEN, APIFY_ACTOR_ID, and APIFY_COUNTRY. The code's default Actor is misceres/indeed-scraper; country defaults to US. A different Actor may require a different input schema.", "BodySmall"),
    PageBreak(),
])

# Matching, fallbacks and state
story.extend([
    P("3. Decision Logic, Fallbacks, and State", "Section"),
    P("Match scores combine simple rules with optional language-model rationale. The ranking order is not delegated to OpenAI.", "BodySmall"),
    P("How the score is built", "Subsection"),
    bullet("Skills contribute up to 60 points, based on the fraction of evaluated job skills that overlap with candidate skills/languages/frameworks. If no skills are evaluated, the skill component uses a neutral 40."),
    bullet("Title alignment contributes 10–25 points: exact user target role (25), a profile preferred role (20), a title containing one of the first candidate skills (15), or a baseline (10)."),
    bullet("Location/workplace alignment contributes 10–15 points: a remote preference match or a preferred-location match gets 15; otherwise the baseline is 10."),
    bullet("The combined rule score is bounded to 35–99. If the optional LLM returns a numeric score, the code blends it as 70% rule score and 30% LLM score."),
    P("Important accuracy note: although the matcher returns an experience_match label, experience is not a separate numeric score component in the current implementation. The LLM may mention experience in its rationale, but the code's deterministic score is skills + title + location.", "Callout"),
    P("Fallback behavior", "Subsection"),
])
fallback_rows = [
    [P("DEPENDENCY / FAILURE", "TableHead"), P("WHAT THE APP DOES", "TableHead")],
    [P("No OpenAI key", "TableCell"), P("Uses regex/keyword resume extraction and locally constructed search query strings; match explanations become rule-based text.", "TableCell")],
    [P("OpenAI call fails", "TableCell"), P("Profile extraction and search planning catch errors and fall back. Match explanation failure returns no LLM evaluation, so a local rationale is used.", "TableCell")],
    [P("No Apify token", "TableCell"), P("Uses the built-in DEMO_JOB_DATABASE if demo fallback remains enabled. Demo listings are marked as demo data.", "TableCell")],
    [P("Apify yields no listings", "TableCell"), P("Falls back to demo listings so downstream matching/ranking remains demonstrable.", "TableCell")],
    [P("Invalid/blank PDF or pipeline exception", "TableCell"), P("Raises an error into run_pipeline, records FAILED in execution history, and returns success=False plus the error message.", "TableCell")],
]
story.append(make_table(fallback_rows, [1.65 * inch, 4.99 * inch]))
story.extend([
    P("State machine", "Subsection"),
    P("The run progresses through IDLE → RESUME_UPLOADED → RESUME_PARSED → PROFILE_CREATED → PLANNING_SEARCH → SEARCHING_JOBS → JOBS_RECEIVED → MATCHING → RANKING → COMPLETED. Any caught pipeline exception transitions to FAILED. Each transition records a timestamp and message; the UI presents the history as a progress/execution log.", "BodySmall"),
    P("Why a hybrid system?", "Subsection"),
    P("The design uses an LLM where language understanding helps (profile structuring, query variety, explanation) and ordinary Python where predictable behavior matters (PDF extraction, schema normalization, deduplication, weighted scoring and filters). This keeps the demo usable without paid API credentials and makes the main ranking easier to inspect.", "BodySmall"),
    PageBreak(),
])

# Presentation notes, run instructions, limitations
story.extend([
    P("4. How to Explain It", "Section"),
    P("A 60–90 second talk track", "Subsection"),
    P("“This project is a resume-to-job recommendation pipeline. The user starts in a Streamlit dashboard, uploads a PDF, and enters search preferences. PyMuPDF extracts resume text locally. The agent then asks an optional OpenAI model to structure the candidate profile and create targeted search queries; if no key is available, local heuristics keep the flow working. The job-search manager sends those queries to a configured Apify Actor, runs query searches concurrently, and reads the results from Apify's dataset. We normalize different listing formats and remove duplicates. A transparent rule-based matcher scores skill, title, and location fit, with an optional LLM explanation. Finally, a ranker applies filters and sorts the jobs, and the UI shows the recommendations and original links. The state machine records each stage. The system recommends jobs but never applies for the user.”", "Callout"),
    P("Questions you may be asked", "Subsection"),
])
qa_rows = [
    [P("QUESTION", "TableHead"), P("CLEAR ANSWER", "TableHead")],
    [P("Is this really an AI agent?", "TableCell"), P("It demonstrates an agent-style pipeline: a goal, input perception, LLM-assisted reasoning/planning, tool calls, observations, and ranking decisions. It is a bounded, pre-programmed workflow, not an open-ended autonomous agent loop.", "TableCell")],
    [P("Which model is used?", "TableCell"), P("The OPENAI_MODEL environment setting controls it; the code default is gpt-4o-mini. The OpenAI integration is optional.", "TableCell")],
    [P("Where do the jobs come from?", "TableCell"), P("From the configured Apify Actor when credentials are available. Otherwise, or when live search returns nothing, the app can use its built-in demo records.", "TableCell")],
    [P("How is a score calculated?", "TableCell"), P("Primarily rule-based: skills (up to 60), title (10–25), location/workplace (10–15), bounded to 35–99; an LLM score can optionally be blended 30% into that result.", "TableCell")],
    [P("Does it store or send my resume?", "TableCell"), P("PyMuPDF processes it locally, but when OpenAI is configured the extracted text is sent to OpenAI for profiling, and profile/job details may be sent for match explanations. Preference memory stores only selected preference fields. Avoid using real personal data in a public demo unless the handling is approved.", "TableCell")],
    [P("Can the agent apply to jobs?", "TableCell"), P("No. It displays the listing's URL for the user to open and apply manually.", "TableCell")],
]
story.append(make_table(qa_rows, [1.72 * inch, 4.92 * inch]))
story.extend([
    P("Limitations worth stating", "Subsection"),
    bullet("PDF text extraction is not OCR; scanned/image-only resumes can fail unless OCR is added."),
    bullet("Scraper Actor inputs and output fields vary by provider; changing APIFY_ACTOR_ID may require adapting run_input and normalization."),
    bullet("The current matching algorithm uses substring skill overlap and simple title/location rules; it is a useful prototype score, not a validated hiring assessment."),
    bullet("Searches are concurrent across query strings, but each Apify Actor call is synchronous and waits for completion."),
    P("Run commands", "Subsection"),
    P("From the project directory on Windows: <b>py -3.11 -m streamlit run app.py</b>. The CLI demonstration is <b>py -3.11 main.py</b>. Install dependencies first with <b>py -3.11 -m pip install -r requirements.txt</b>. OpenAI and Apify keys are optional for a demo run; without Apify, demo listings are used.", "BodySmall"),
    Spacer(1, 5),
    P("Code map: app.py; agent/agent.py; agent/tools.py; agent/state.py; resume/parser.py; llm/client.py; jobs/apify_client.py; jobs/job_search.py; jobs/normalizer.py; matching/matcher.py; matching/ranker.py; memory/memory.py; prompts/*.py.", "Caption"),
])

doc.build(story)
print(f"Created {OUTPUT_FILE}")