from io import BytesIO

import pdfplumber
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from .ats_score import calculate_ats_score
except ImportError:  # Vercel runs this file as a standalone entry point.
    from ats_score import calculate_ats_score


app = FastAPI()
MAX_FILE_SIZE = 4 * 1024 * 1024
MAX_PAGES = 20

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://resume-moderator.vercel.app"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def rewrite_resume(text, job_description, company_name="", job_role=""):
    lines = text.split("\n")
    rewritten = []
    job_terms = {word.lower() for word in job_description.split()}

    for line in lines:
        if any(word.lower() in line.lower() for word in job_terms):
            rewritten.append(f"✓ {line} (matches the job description)")
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
    job_description: str = Form(...),
):
    if not job_description or len(job_description.strip()) < 10:
        raise HTTPException(status_code=422, detail="Please add a job description with at least 10 characters.")
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Please upload a PDF resume.")

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Please upload a PDF smaller than 4 MB.")

        text_parts = []
        with pdfplumber.open(BytesIO(contents)) as pdf:
            if len(pdf.pages) > MAX_PAGES:
                raise HTTPException(status_code=413, detail="Please upload a PDF with no more than 20 pages.")
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    text_parts.append(page_text)

        text = "\n".join(text_parts).strip()
        if not text:
            raise HTTPException(status_code=422, detail="No readable text was found. Please upload a text-based PDF.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read this PDF.")
    finally:
        await file.close()

    score, missing = calculate_ats_score(text, job_description)
    suggestions = [f'Include "{word}" in relevant sections' for word in missing]
    optimized_resume = rewrite_resume(text, job_description, company_name, job_role)

    return JSONResponse({
        "ats_score": score,
        "missing_keywords": missing,
        "improvement_suggestions": suggestions,
        "optimized_resume": optimized_resume[:5000],
        "resume_preview": text[:300],
    })
