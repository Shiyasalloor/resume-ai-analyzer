from google import genai
from pydantic import BaseModel, Field
from typing import List
import streamlit as st
import os

# --------------------------------
# Structured output schema
# --------------------------------

class SkillAnalysis(BaseModel):
    skill: str
    status: str
    evidence: str

# --------------------------------
# ATS Analysis Schema
# --------------------------------

class ATSAnalysis(BaseModel):

    ats_score: int = Field(
        description="Overall ATS optimization score from 0 to 100"
    )

    keyword_score: int = Field(
        description="How well the resume contains important keywords from the job description, from 0 to 100"
    )

    skills_score: int = Field(
        description="How well the resume demonstrates the required skills, from 0 to 100"
    )

    experience_score: int = Field(
        description="How well the candidate's experience aligns with the role, from 0 to 100"
    )

    structure_score: int = Field(
        description="How clear, consistent, and ATS-friendly the resume structure is, from 0 to 100"
    )

    missing_keywords: List[str] = Field(
        description="Important job-description keywords that are missing or insufficiently demonstrated in the resume"
    )

class ResumeAnalysis(BaseModel):

    match_score: int = Field(
        description="Overall resume-job match score from 0 to 100"
    )

    matching_skills: List[str] = Field(
        description="Important skills from the job description that the candidate has"
    )

    missing_skills: List[str] = Field(
        description="Important skills from the job description that are missing or not demonstrated"
    )

    skill_analysis: List[SkillAnalysis] = Field(
        description="Analysis of important skills required by the job"
    )

    strengths: List[str] = Field(
        description="The strongest aspects of the candidate for this job"
    )

    recommendations: List[str] = Field(
        description="Specific recommendations to improve the resume for this job"
    )

    summary: str = Field(
        description="Short overall assessment of the candidate-job match"
    )
    
    ats_analysis: ATSAnalysis = Field(
        description="Detailed ATS optimization analysis of the resume"
    )
    
# --------------------------------
# Resume Rewrite Schema
# --------------------------------

class ResumeImprovement(BaseModel):
    section: str
    before: str
    after: str
    reason: str


class ResumeRewrite(BaseModel):
    improvements: List[ResumeImprovement]

def rewrite_resume(resume_text, job_description):
    prompt = f"""
    You are an expert resume writer and ATS optimization specialist.

    Analyze the candidate's resume against the target job description.

    Your task is to identify up to 5 weak, generic, vague, or poorly targeted
    resume bullet points and rewrite them to be stronger and more relevant
    to the target role.

    IMPORTANT:
    - Do not invent experience.
    - Do not invent technologies.
    - Do not invent metrics or achievements.
    - Preserve the candidate's actual experience.
    - Improve wording, clarity, impact, and job relevance.
    - Naturally incorporate relevant keywords from the job description
    ONLY when the candidate's experience supports them.

    Return ONLY valid JSON in this exact format:

    {{
    "improvements": [
        {{
        "section": "Experience",
        "before": "Original resume bullet",
        "after": "Improved resume bullet",
        "reason": "Why this version is stronger"
        }}
    ]
    }}

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ResumeRewrite,
        },
    )

    return ResumeRewrite.model_validate_json(
        response.text
    )


# --------------------------------
# Gemini client
# --------------------------------

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


# --------------------------------
# Analyze resume
# --------------------------------

def analyze_resume(resume_text, job_description):

    prompt = f"""
You are an expert technical recruiter and resume analyst.

Analyze the candidate's resume against the provided job description.

Your job is to determine how well the candidate matches the role.

IMPORTANT RULES:

1. Only use information explicitly present in the resume.
2. Do not invent skills, experience, education, or projects.
3. A skill should be considered "Strong" only when the resume provides
   clear evidence of experience with it.
4. A skill should be "Good" when there is reasonable evidence.
5. A skill should be "Weak" when it is mentioned but not strongly demonstrated.
6. A skill should be "Missing" when the job requires it and the resume
   does not demonstrate it.
7. Focus on important requirements rather than insignificant keywords.
8. Give a realistic match score from 0 to 100.
9. Recommendations must be specific and actionable.
10. Do not penalize the candidate for skills that are not important
    to the role.
11. Also evaluate the resume's ATS optimization.

ATS EVALUATION:

- ats_score: Overall ATS optimization from 0 to 100.
- keyword_score: Coverage of important job-specific keywords.
- skills_score: Coverage and evidence of required technical skills.
- experience_score: Relevance of the candidate's experience to the role.
- structure_score: Clarity and consistency of the resume structure.

ATS RULES:

- Do not reward keyword stuffing.
- Only count a keyword as strongly matched when the resume
  demonstrates relevant experience or knowledge.
- Do not invent keywords or experience.
- Missing keywords should contain only important job-related
  terms that are genuinely absent or insufficiently demonstrated.
- The ATS score should be realistic rather than automatically high.

-------------------------
RESUME
-------------------------

{resume_text}

-------------------------
JOB DESCRIPTION
-------------------------

{job_description}

-------------------------

Return the analysis using the required structured format.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ResumeAnalysis,
        },
    )

    return ResumeAnalysis.model_validate_json(response.text)