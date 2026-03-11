from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

def rewrite_resume(text, job_description, company_name="", job_role=""):
    lines = text.split("\n")
    rewritten = []

    for line in lines:
        line_lower = line.lower()
        if any(word.lower() in line_lower for word in job_description.split()):
            rewritten.append(f"✅ {line} (optimized for ATS)")
        else:
            rewritten.append(line)

    header = f"Optimized Resume for {job_role} at {company_name}\n\n" if company_name or job_role else ""
    return header + "\n".join(rewritten)

@app.get("/")
def home():
    return {"message": "Resume Moderator API Running"}

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    company_name: str = Form(""),
    job_role: str = Form(""),
    job_description: str = Form(...)
):

    text = ""
    try:
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except:
        return JSONResponse({"error": "Could not read PDF"}, status_code=400)

    score, missing = calculate_ats_score(text, job_description)

    suggestions = [f'Include "{word}" in relevant sections' for word in missing]

    optimized_resume = rewrite_resume(text, job_description, company_name, job_role)

    return JSONResponse({
        "ats_score": score,
        "missing_keywords": missing,
        "improvement_suggestions": suggestions,
        "optimized_resume": optimized_resume[:1000],
        "resume_preview": text[:300]
    })