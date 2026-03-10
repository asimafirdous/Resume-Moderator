from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
from ats_score import calculate_ats_score

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def rewrite_resume(text, job_description):
    # Split resume into lines
    lines = text.split("\n")
    rewritten = []

    for line in lines:
        line_lower = line.lower()
        # If line contains skills from job description, highlight it
        if any(word.lower() in line_lower for word in job_description.split()):
            rewritten.append(f"✅ {line} (optimized for ATS)")
        else:
            rewritten.append(line)

    return "\n".join(rewritten)

@app.get("/")
def home():
    return {"message": "Resume Moderator API Running"}

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...), job_description: str = Form(...)):

    text = ""

    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

    score, missing = calculate_ats_score(text, job_description)

    suggestions = []
    for word in missing:
        suggestions.append(f'Include "{word}" in relevant sections')

    optimized_resume = rewrite_resume(text, job_description)

    return {
        "ats_score": score,
        "missing_keywords": missing,
        "improvement_suggestions": suggestions,
        "optimized_resume": optimized_resume[:1000],  # preview first 1000 chars
        "resume_preview": text[:300]
    }