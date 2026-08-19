# ResumeAI – AI Resume Analyzer

ResumeAI is an AI-powered resume analysis platform that evaluates a candidate's resume against a target job description.

## Features

- 📄 PDF Resume Upload
- 🤖 AI-powered Resume Analysis
- 🎯 Job Match Score
- 📊 Skill Match Breakdown
- ⚠️ Missing Skills Detection
- 🎯 ATS Optimization Score
- ✨ AI Resume Rewriter
- 📄 Downloadable PDF Analysis Report

## Tech Stack

- Python
- Streamlit 
- Google Gemini API
- Pydantic
- PyPDF2
- ReportLab

## How It Works

1. Upload a resume in PDF format.
2. Enter the target job description.
3. ResumeAI extracts the resume text.
4. Gemini analyzes the resume against the job description.
5. The system generates:
   - Overall match score
   - Matching skills
   - Missing skills
   - Skill-level analysis
   - ATS optimization score
   - Improvement recommendations
6. The AI Resume Rewriter suggests stronger versions of weak resume statements.
7. Users can download the complete analysis as a PDF report.

## Running Locally

Install the dependencies:

```bash
pip install -r requirements.txt