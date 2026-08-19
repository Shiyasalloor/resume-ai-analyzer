import streamlit as st
import textwrap

from pdf_parser import extract_text_from_pdf
from ai_analyzer import analyze_resume, rewrite_resume

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

def render_html(html):
    html = "\n".join(
        line.lstrip()
        for line in html.splitlines()
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )
    
def generate_pdf_report(analysis):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=15,
        leading=19,
        spaceBefore=14,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=7,
    )

    small_style = ParagraphStyle(
        "ReportSmall",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=12,
    )

    story = []

    # ----------------------------------------------------
    # HEADER
    # ----------------------------------------------------

    story.append(
        Paragraph(
            "RESUMEAI",
            title_style
        )
    )

    story.append(
        Paragraph(
            "AI-Powered Resume Analysis Report",
            subtitle_style
        )
    )

    # ----------------------------------------------------
    # SCORE SUMMARY
    # ----------------------------------------------------

    ats = analysis.ats_analysis

    score_data = [
        [
            Paragraph("<b>Overall Match</b>", body_style),
            Paragraph("<b>ATS Score</b>", body_style),
        ],
        [
            Paragraph(
                f"<font size='22'><b>{analysis.match_score}%</b></font>",
                body_style,
            ),
            Paragraph(
                f"<font size='22'><b>{ats.ats_score}/100</b></font>",
                body_style,
            ),
        ],
    ]

    score_table = Table(
        score_data,
        colWidths=[80 * mm, 80 * mm],
    )

    score_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.whitesmoke,
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                colors.lightgrey,
            ),
            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.lightgrey,
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER",
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                10,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                10,
            ),
        ])
    )

    story.append(score_table)
    story.append(Spacer(1, 12))

    # ----------------------------------------------------
    # AI ASSESSMENT
    # ----------------------------------------------------

    story.append(
        Paragraph(
            "AI Assessment",
            heading_style
        )
    )

    story.append(
        Paragraph(
            analysis.summary,
            body_style
        )
    )

    # ----------------------------------------------------
    # SKILLS
    # ----------------------------------------------------

    story.append(
        Paragraph(
            "Skills Analysis",
            heading_style
        )
    )

    skill_data = [
        [
            Paragraph("<b>Skill</b>", small_style),
            Paragraph("<b>Status</b>", small_style),
            Paragraph("<b>Evidence</b>", small_style),
        ]
    ]

    for item in analysis.skill_analysis:

        skill_data.append([
            Paragraph(
                item.skill,
                small_style
            ),
            Paragraph(
                item.status,
                small_style
            ),
            Paragraph(
                item.evidence,
                small_style
            ),
        ])

    skill_table = Table(
        skill_data,
        colWidths=[
            38 * mm,
            30 * mm,
            92 * mm,
        ],
        repeatRows=1,
    )

    skill_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey,
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.grey,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP",
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
        ])
    )

    story.append(skill_table)

    # ----------------------------------------------------
    # MATCHING SKILLS
    # ----------------------------------------------------

    story.append(
        Paragraph(
            "Matching Skills",
            heading_style
        )
    )

    for skill in analysis.matching_skills:

        story.append(
            Paragraph(
                f"• {skill}",
                body_style
            )
        )

    # ----------------------------------------------------
    # MISSING SKILLS
    # ----------------------------------------------------

    story.append(
        Paragraph(
            "Missing Skills",
            heading_style
        )
    )

    for skill in analysis.missing_skills:

        story.append(
            Paragraph(
                f"• {skill}",
                body_style
            )
        )

    # ----------------------------------------------------
    # ATS ANALYSIS
    # ----------------------------------------------------

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "ATS Optimization",
            heading_style
        )
    )

    ats_data = [
        ["Metric", "Score"],
        ["Keyword Match", f"{ats.keyword_score}%"],
        ["Skills Coverage", f"{ats.skills_score}%"],
        ["Experience Relevance", f"{ats.experience_score}%"],
        ["Resume Structure", f"{ats.structure_score}%"],
        ["Overall ATS Score", f"{ats.ats_score}/100"],
    ]

    ats_table = Table(
        ats_data,
        colWidths=[
            100 * mm,
            55 * mm,
        ],
    )

    ats_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey,
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
            (
                "ALIGN",
                (1, 0),
                (1, -1),
                "CENTER",
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
        ])
    )

    story.append(ats_table)

    # ----------------------------------------------------
    # MISSING KEYWORDS
    # ----------------------------------------------------

    if ats.missing_keywords:

        story.append(
            Paragraph(
                "Important Missing Keywords",
                heading_style
            )
        )

        for keyword in ats.missing_keywords:

            story.append(
                Paragraph(
                    f"• {keyword}",
                    body_style
                )
            )

    # ----------------------------------------------------
    # STRENGTHS
    # ----------------------------------------------------

    story.append(
        Paragraph(
            "Candidate Strengths",
            heading_style
        )
    )

    for strength in analysis.strengths:

        story.append(
            Paragraph(
                f"✓ {strength}",
                body_style
            )
        )

    # ----------------------------------------------------
    # RECOMMENDATIONS
    # ----------------------------------------------------

    story.append(
        Paragraph(
            "Recommendations",
            heading_style
        )
    )

    for index, recommendation in enumerate(
        analysis.recommendations,
        start=1
    ):

        story.append(
            Paragraph(
                f"{index}. {recommendation}",
                body_style
            )
        )

    # ----------------------------------------------------
    # BUILD PDF
    # ----------------------------------------------------

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()
# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResumeAI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- APP ---------- */

    .stApp {
        background:
            radial-gradient(
                circle at 15% 5%,
                rgba(99, 102, 241, 0.16),
                transparent 25%
            ),
            radial-gradient(
                circle at 90% 10%,
                rgba(139, 92, 246, 0.13),
                transparent 25%
            ),
            #080b14;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    /* ---------- HIDE DEFAULT ---------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* ---------- HEADINGS ---------- */

    h1 {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -2px !important;
        color: #f8fafc !important;
    }

    h2 {
        color: #f8fafc !important;
    }

    h3 {
        color: #f8fafc !important;
    }

    /* ---------- HERO ---------- */

    .hero-small {
        color: #a5b4fc;
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 0.8rem;
    }

    .hero-description {
        color: #94a3b8;
        font-size: 1.05rem;
        line-height: 1.7;
        max-width: 720px;
        margin-bottom: 2rem;
    }

    /* ---------- CARDS ---------- */

    .card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 18px;
        padding: 1.4rem;
        margin-bottom: 1rem;
    }

    .card-title {
        font-size: 1rem;
        font-weight: 750;
        color: #f8fafc;
        margin-bottom: 0.3rem;
    }

    .card-subtitle {
        color: #64748b;
        font-size: 0.8rem;
        margin-bottom: 1rem;
    }

    /* ---------- SCORE ---------- */

    .score-card {
        background:
            radial-gradient(
                circle at 80% 20%,
                rgba(99, 102, 241, 0.20),
                transparent 40%
            ),
            rgba(15, 23, 42, 0.85);

        border: 1px solid rgba(129, 140, 248, 0.22);
        border-radius: 22px;
        padding: 2rem;
        text-align: center;
    }

    .score-label {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .score-number {
        font-size: 5rem;
        font-weight: 850;
        line-height: 1.1;
        color: #a5b4fc;
        margin: 0.4rem 0;
    }

    .score-text {
        color: #cbd5e1;
        font-size: 0.9rem;
    }

    /* ---------- SKILLS ---------- */

    .skill {
        display: inline-block;
        padding: 7px 11px;
        border-radius: 9px;
        margin: 4px;
        font-size: 0.78rem;
        font-weight: 650;
    }

    .skill-match {
        background: rgba(16, 185, 129, 0.10);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.18);
    }

    .skill-missing {
        background: rgba(239, 68, 68, 0.09);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.16);
    }

    /* ---------- RECOMMENDATIONS ---------- */

    .recommendation {
        background: rgba(30, 41, 59, 0.55);
        border: 1px solid rgba(148, 163, 184, 0.09);
        border-radius: 12px;
        padding: 12px 14px;
        margin: 8px 0;
        color: #cbd5e1;
        font-size: 0.85rem;
        line-height: 1.5;
    }

    /* ---------- STATUS ---------- */

    .status {
        display: inline-block;
        padding: 6px 11px;
        border-radius: 999px;
        background: rgba(16, 185, 129, 0.10);
        border: 1px solid rgba(16, 185, 129, 0.20);
        color: #6ee7b7;
        font-size: 0.75rem;
        font-weight: 700;
    }

    /* ---------- BUTTON ---------- */

    .stButton > button {
        width: 100%;
        min-height: 50px;
        border-radius: 12px;
        border: none;
        background: linear-gradient(
            135deg,
            #4f46e5,
            #7c3aed
        );
        color: white;
        font-size: 1rem;
        font-weight: 750;
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        box-shadow:
            0 0 25px rgba(99, 102, 241, 0.35);
        transform: translateY(-1px);
    }

    /* ---------- INPUTS ---------- */

    [data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.55);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 14px;
        padding: 0.5rem;
    }

    textarea {
        background: rgba(15, 23, 42, 0.55) !important;
        color: #e2e8f0 !important;
        border-radius: 12px !important;
    }

    /* ---------- EXPANDER ---------- */

    [data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(148, 163, 184, 0.10);
        border-radius: 14px;
    }

    /* ---------- DIVIDER ---------- */

    hr {
        border-color: rgba(148, 163, 184, 0.10) !important;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        color: #475569;
        font-size: 0.75rem;
        padding-top: 3rem;
    }
    
    /* ========================================================
    SKILL MATCH BREAKDOWN
    ======================================================== */

    .skill-breakdown {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.10);
        border-radius: 20px;
        padding: 24px;
        margin-top: 25px;
    }

    .breakdown-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }

    .breakdown-title {
        color: #f8fafc;
        font-size: 17px;
        font-weight: 750;
    }

    .breakdown-subtitle {
        color: #64748b;
        font-size: 12px;
        margin-bottom: 24px;
    }

    .skill-row {
        margin-bottom: 18px;
    }

    .skill-row-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 7px;
    }

    .skill-name {
        color: #e2e8f0;
        font-size: 13px;
        font-weight: 600;
    }

    .skill-score {
        color: #a5b4fc;
        font-size: 12px;
        font-weight: 750;
    }

    .skill-track {
        width: 100%;
        height: 7px;
        background: #1e293b;
        border-radius: 999px;
        overflow: hidden;
    }

    .skill-progress {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(
            90deg,
            #6366f1,
            #a78bfa
        );
        box-shadow: 0 0 12px rgba(129, 140, 248, 0.35);
    }

    .skill-progress-good {
        background: linear-gradient(
            90deg,
            #10b981,
            #34d399
        );
    }

    .skill-progress-weak {
        background: linear-gradient(
            90deg,
            #f59e0b,
            #fbbf24
        );
    }

    .skill-progress-missing {
        background: linear-gradient(
            90deg,
            #ef4444,
            #f87171
        );
    }
    
    .rewrite-card {
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(129, 140, 248, 0.15);
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 14px;
    }

    .before-label {
        color: #64748b;
        font-size: 11px;
        font-weight: 750;
        letter-spacing: 1px;
    }

    .after-label {
        color: #6ee7b7;
        font-size: 11px;
        font-weight: 750;
        letter-spacing: 1px;
    }
    
    /* ========================================================
    ATS OPTIMIZATION
    ======================================================== */

    .ats-card {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(129, 140, 248, 0.14);
        border-radius: 20px;
        padding: 26px;
        margin-top: 25px;
    }

    .ats-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 28px;
    }

    .ats-title {
        color: #f8fafc;
        font-size: 17px;
        font-weight: 750;
    }

    .ats-subtitle {
        color: #64748b;
        font-size: 12px;
        margin-top: 5px;
    }

    .ats-score {
        color: #a5b4fc;
        font-size: 34px;
        font-weight: 800;
    }

    .ats-score span {
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
    }

    .ats-metrics {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px 30px;
    }

    .ats-metric-top {
        display: flex;
        justify-content: space-between;
        color: #cbd5e1;
        font-size: 12px;
        margin-bottom: 7px;
    }

    .ats-metric-top strong {
        color: #a5b4fc;
    }

    .ats-track {
        width: 100%;
        height: 7px;
        background: #1e293b;
        border-radius: 999px;
        overflow: hidden;
    }

    .ats-progress {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(
            90deg,
            #6366f1,
            #a78bfa
        );
        box-shadow: 0 0 12px rgba(129, 140, 248, 0.3);
    }

    @media (max-width: 700px) {

        .ats-metrics {
            grid-template-columns: 1fr;
        }

        .ats-header {
            align-items: flex-start;
        }

    }
    
    /* ========================================================
    DOWNLOAD REPORT
    ======================================================== */

    .report-download {
        margin-top: 25px;
        padding: 24px;
        border-radius: 20px;
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(129, 140, 248, 0.14);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    '<div class="hero-small">✦ RESUMEAI</div>',
    unsafe_allow_html=True,
)

st.title("Know exactly how your resume fits the role.")

st.markdown(
    """
    <div class="hero-description">
        AI-powered resume intelligence that compares your experience
        against a specific job description and tells you exactly
        where you stand — and what to improve before applying.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# INPUT AREA
# ============================================================

left, right = st.columns(2, gap="large")


with left:

    st.markdown(
        """
        <div class="card">
            <div class="card-title">📄 Your Resume</div>
            <div class="card-subtitle">
                Upload your resume in PDF format
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    resume = st.file_uploader(
        "Upload Resume",
        type=["pdf"],
        label_visibility="collapsed",
    )


with right:

    st.markdown(
        """
        <div class="card">
            <div class="card-title">🎯 Target Role</div>
            <div class="card-subtitle">
                Paste the job description you want to target
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    job_description = st.text_area(
        "Job Description",
        placeholder=(
            "Paste the complete job description here..."
        ),
        height=180,
        label_visibility="collapsed",
    )


st.write("")


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "✦  Analyze My Resume",
    type="primary",
):

    if resume is None:

        st.warning(
            "Please upload your resume first."
        )

    elif not job_description.strip():

        st.warning(
            "Please paste the job description first."
        )

    else:

        with st.spinner(
            "🤖 AI is analyzing your resume..."
        ):

            try:

                # Extract PDF text
                resume_text = extract_text_from_pdf(
                    resume
                )

                if not resume_text:

                    st.error(
                        "Could not extract text from the PDF."
                    )

                    st.stop()

                # Gemini analysis
                analysis = analyze_resume(
                    resume_text,
                    job_description,
                )

                # Persist results
                st.session_state.analysis = analysis
                st.session_state.resume_text = resume_text
                st.session_state.job_description = job_description
                
                st.success(
                    "Analysis completed successfully."
                )

            except Exception as e:

                st.error(
                    f"Analysis failed: {e}"
                )


# ============================================================
# RESULTS
# ============================================================

if "analysis" in st.session_state:

    analysis = st.session_state.analysis

    st.divider()

    # --------------------------------------------------------
    # RESULT HEADER
    # --------------------------------------------------------

    header_left, header_right = st.columns(
        [4, 1]
    )

    with header_left:

        st.header("Your AI Analysis")

    with header_right:

        st.markdown(
            '<div class="status">● AI Analysis Complete</div>',
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    score = max(
        0,
        min(
            100,
            int(analysis.match_score),
        ),
    )

    if score >= 80:

        score_message = (
            "Excellent alignment with this role."
        )

    elif score >= 65:

        score_message = (
            "Strong potential with some areas to improve."
        )

    elif score >= 50:

        score_message = (
            "Moderate alignment. Your resume needs some improvements."
        )

    else:

        score_message = (
            "There are significant gaps for this role."
        )


    score_col, stats_col = st.columns(
        [1.7, 1],
        gap="large",
    )


    with score_col:

        render_html(
            f"""
            <div class="score-card">
                <div class="score-label">
                    Overall Match
                </div>

                <div class="score-number">
                    {score}%
                </div>

                <div class="score-text">
                    {score_message}
                </div>
            </div>
            """
        )

    with stats_col:

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Matching Skills",
                len(
                    analysis.matching_skills
                ),
            )

        with c2:

            st.metric(
                "Skill Gaps",
                len(
                    analysis.missing_skills
                ),
            )

        c3, c4 = st.columns(2)

        with c3:

            st.metric(
                "Strengths",
                len(
                    analysis.strengths
                ),
            )

        with c4:

            st.metric(
                "Recommendations",
                len(
                    analysis.recommendations
                ),
            )


    # --------------------------------------------------------
    # AI ASSESSMENT
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="card">
            <div class="card-title">
                🧠 AI Assessment
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        analysis.summary,
        icon="🧠",
    )


    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    skills_left, skills_right = st.columns(
        2,
        gap="large",
    )


    with skills_left:

        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    🟢 Skills You Bring
                </div>
                <div class="card-subtitle">
                    Skills found in your resume that match the role
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if analysis.matching_skills:

            html = ""

            for skill in analysis.matching_skills:

                html += (
                    f'<span class="skill skill-match">'
                    f'✓ {skill}'
                    f'</span>'
                )

            st.markdown(
                html,
                unsafe_allow_html=True,
            )

        else:

            st.caption(
                "No strong matching skills identified."
            )


    with skills_right:

        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    🔴 Skills To Strengthen
                </div>
                <div class="card-subtitle">
                    Important requirements not clearly demonstrated
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if analysis.missing_skills:

            html = ""

            for skill in analysis.missing_skills:

                html += (
                    f'<span class="skill skill-missing">'
                    f'+ {skill}'
                    f'</span>'
                )

            st.markdown(
                html,
                unsafe_allow_html=True,
            )

        else:

            st.caption(
                "No significant skill gaps identified."
            )

    # --------------------------------------------------------
    # SKILL MATCH BREAKDOWN
    # --------------------------------------------------------

    skill_rows = ""

    for item in analysis.skill_analysis:

        status = item.status.lower().strip()

        # Convert the AI's qualitative assessment
        # into a visual match percentage.
        if "strong" in status:
            skill_score = 100
            progress_class = "skill-progress-good"

        elif "good" in status:
            skill_score = 85
            progress_class = "skill-progress-good"

        elif "weak" in status:
            skill_score = 55
            progress_class = "skill-progress-weak"

        else:
            skill_score = 20
            progress_class = "skill-progress-missing"

        skill_rows += f"""
        <div class="skill-row">

            <div class="skill-row-top">

                <div class="skill-name">
                    {item.skill}
                </div>

                <div class="skill-score">
                    {skill_score}%
                </div>

            </div>

            <div class="skill-track">

                <div
                    class="skill-progress {progress_class}"
                    style="width:{skill_score}%"
                ></div>

            </div>

        </div>
        """


    render_html(
        f"""
        <div class="skill-breakdown">

            <div class="breakdown-header">

                <div class="breakdown-title">
                    📊 Skill Match Breakdown
                </div>

            </div>

            <div class="breakdown-subtitle">
                How strongly your resume demonstrates the skills
                required for this role.
            </div>

            {skill_rows}

        </div>
        """
    )
    
    # --------------------------------------------------------
    # ATS OPTIMIZATION
    # --------------------------------------------------------

    ats = analysis.ats_analysis

    render_html(
        f"""
        <div class="ats-card">

            <div class="ats-header">

                <div>
                    <div class="ats-title">
                        🎯 ATS Optimization
                    </div>

                    <div class="ats-subtitle">
                        How well your resume is optimized for
                        automated screening systems.
                    </div>
                </div>

                <div class="ats-score">
                    {ats.ats_score}
                    <span>/100</span>
                </div>

            </div>


            <div class="ats-metrics">

                <div class="ats-metric">

                    <div class="ats-metric-top">
                        <span>Keyword Match</span>
                        <strong>{ats.keyword_score}%</strong>
                    </div>

                    <div class="ats-track">
                        <div
                            class="ats-progress"
                            style="width:{ats.keyword_score}%"
                        ></div>
                    </div>

                </div>


                <div class="ats-metric">

                    <div class="ats-metric-top">
                        <span>Skills Coverage</span>
                        <strong>{ats.skills_score}%</strong>
                    </div>

                    <div class="ats-track">
                        <div
                            class="ats-progress"
                            style="width:{ats.skills_score}%"
                        ></div>
                    </div>

                </div>


                <div class="ats-metric">

                    <div class="ats-metric-top">
                        <span>Experience Relevance</span>
                        <strong>{ats.experience_score}%</strong>
                    </div>

                    <div class="ats-track">
                        <div
                            class="ats-progress"
                            style="width:{ats.experience_score}%"
                        ></div>
                    </div>

                </div>


                <div class="ats-metric">

                    <div class="ats-metric-top">
                        <span>Resume Structure</span>
                        <strong>{ats.structure_score}%</strong>
                    </div>

                    <div class="ats-track">
                        <div
                            class="ats-progress"
                            style="width:{ats.structure_score}%"
                        ></div>
                    </div>

                </div>

            </div>

        </div>
        """
    )
    # --------------------------------------------------------
    # STRENGTHS + RECOMMENDATIONS
    # --------------------------------------------------------

    st.write("")

    strengths_col, recommendations_col = st.columns(
        2,
        gap="large",
    )


    with strengths_col:

        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    💪 Your Strengths
                </div>
                <div class="card-subtitle">
                    What makes your profile valuable for this role
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for strength in analysis.strengths:

            st.markdown(
                f"""
                <div class="recommendation">
                    ✓ &nbsp; {strength}
                </div>
                """,
                unsafe_allow_html=True,
            )


    with recommendations_col:

        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    🎯 What You Should Improve
                </div>
                <div class="card-subtitle">
                    AI-generated actions before you apply
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for i, recommendation in enumerate(
            analysis.recommendations,
            start=1,
        ):

            st.markdown(
                f"""
                <div class="recommendation">
                    <strong>{i}.</strong>
                    &nbsp; {recommendation}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------
    # AI RESUME REWRITER
    # --------------------------------------------------------

    st.write("")

    render_html(
        """
        <div class="card">

            <div class="card-title">
                ✨ AI Resume Rewriter
            </div>

            <div class="card-subtitle">
                Improve weak resume statements and tailor them
                to your target role without inventing experience.
            </div>

        </div>
        """
    )

    rewrite_col1, rewrite_col2 = st.columns(
        [3, 1],
        gap="large"
    )

    with rewrite_col1:

        st.caption(
            "The AI will identify up to 5 areas where your resume "
            "could be clearer, stronger, or better aligned with the job."
        )

    with rewrite_col2:

        rewrite_clicked = st.button(
            "✨ Rewrite My Resume",
            key="rewrite_resume_button"
        )


    if rewrite_clicked:

        if (
            "resume_text" not in st.session_state
            or not st.session_state.resume_text
        ):

            st.warning(
                "Please analyze your resume first."
            )

        else:

            with st.spinner(
                "✨ AI is improving your resume..."
            ):

                try:

                    rewritten = rewrite_resume(
                        st.session_state.resume_text,
                        job_description
                    )

                    st.session_state.rewritten_resume = rewritten

                except Exception as e:

                    st.error(
                        f"Resume rewriting failed: {e}"
                    )


    # --------------------------------------------------------
    # DISPLAY REWRITES
    # --------------------------------------------------------

    # --------------------------------------------------------
    # DISPLAY AI RESUME IMPROVEMENTS
    # --------------------------------------------------------

    if "rewritten_resume" in st.session_state:

        improvements = (
            st.session_state
            .rewritten_resume
            .improvements
        )

        if improvements:

            render_html(
                """
                <div class="card">

                    <div class="card-title">
                        ✨ AI Resume Improvements
                    </div>

                    <div class="card-subtitle">
                        Job-specific suggestions to make your resume
                        clearer, stronger, and more relevant.
                    </div>

                </div>
                """
            )

            for index, item in enumerate(
                improvements,
                start=1
            ):

                render_html(
                    f"""
                    <div class="recommendation">

                        <div style="
                            color:#a5b4fc;
                            font-size:12px;
                            font-weight:750;
                            margin-bottom:12px;
                        ">
                            IMPROVEMENT {index}
                            · {item.section}
                        </div>


                        <div style="
                            color:#64748b;
                            font-size:10px;
                            font-weight:750;
                            letter-spacing:1px;
                            margin-bottom:6px;
                        ">
                            BEFORE
                        </div>

                        <div style="
                            color:#cbd5e1;
                            font-size:13px;
                            line-height:1.7;
                            padding:12px;
                            background:rgba(30,41,59,0.55);
                            border-radius:10px;
                            margin-bottom:14px;
                        ">
                            {item.before}
                        </div>


                        <div style="
                            color:#6ee7b7;
                            font-size:10px;
                            font-weight:750;
                            letter-spacing:1px;
                            margin-bottom:6px;
                        ">
                            AFTER
                        </div>

                        <div style="
                            color:#f8fafc;
                            font-size:13px;
                            line-height:1.7;
                            padding:12px;
                            background:rgba(16,185,129,0.08);
                            border:1px solid rgba(16,185,129,0.15);
                            border-radius:10px;
                            margin-bottom:14px;
                        ">
                            {item.after}
                        </div>


                        <div style="
                            color:#64748b;
                            font-size:11px;
                            line-height:1.6;
                        ">
                            💡 {item.reason}
                        </div>

                    </div>
                    """
                )

        else:

            st.info(
                "No major resume improvements were identified."
            )
    # --------------------------------------------------------
    # DETAILED SKILL ANALYSIS
    # --------------------------------------------------------

    st.write("")

    st.subheader("🔍 Detailed Skill Analysis")

    st.caption(
        "See why the AI classified each skill the way it did."
    )


    for item in analysis.skill_analysis:

        status = item.status.lower()

        if "strong" in status:

            icon = "🟢"

        elif "good" in status:

            icon = "🔵"

        elif "weak" in status:

            icon = "🟡"

        else:

            icon = "🔴"

        with st.expander(
            f"{icon}  {item.skill}  ·  {item.status}"
        ):

            st.write(
                item.evidence
            )

    
    # --------------------------------------------------------
    # DOWNLOAD REPORT
    # --------------------------------------------------------

    if "analysis" in st.session_state:

        st.write("")

        render_html(
            """
            <div class="card">

                <div class="card-title">
                    📄 Download Your Analysis
                </div>

                <div class="card-subtitle">
                    Save your complete AI resume analysis,
                    ATS evaluation, skills, and recommendations
                    as a PDF report.
                </div>

            </div>
            """
        )

        pdf_data = generate_pdf_report(
            st.session_state.analysis
        )

        st.download_button(
            label="⬇️ Download Analysis Report",
            data=pdf_data,
            file_name="ResumeAI_Analysis_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # --------------------------------------------------------
    # EXTRACTED RESUME
    # --------------------------------------------------------

    st.write("")

    with st.expander(
        "📄 View extracted resume text"
    ):

        st.text(
            st.session_state.resume_text
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        ResumeAI · AI-powered career intelligence
        <br>
        Built with Python · Streamlit · Gemini
    </div>
    """,
    unsafe_allow_html=True,
)