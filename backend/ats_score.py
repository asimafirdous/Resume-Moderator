def calculate_ats_score(resume_text, job_description):

    resume_words = set(resume_text.lower().split())
    job_words = set(job_description.lower().split())
    matched = resume_words.intersection(job_words)
    score = round(len(matched) / len(job_words) * 100, 2) if job_words else 100
    missing = list(job_words - resume_words)
    return score, missing

def optimize_resume_for_ats(original_resume, missing_keywords, company_name="", job_role=""):
    lines = original_resume.split("\n")
    optimized_lines = []

    # Flag sections
    career_idx = -1
    skills_idx = -1
    projects_idx = -1
    education_idx = -1

    for i, line in enumerate(lines):
        lower = line.lower()
        if "career summary" in lower:
            career_idx = i
        elif "technical skills" in lower or "skills" in lower:
            skills_idx = i
        elif "projects" in lower:
            projects_idx = i
        elif "education" in lower:
            education_idx = i

    if career_idx != -1 and company_name and job_role:
        lines[career_idx+1] = f"{lines[career_idx+1]} Applying for {job_role} at {company_name}."

    if missing_keywords:
        if skills_idx != -1:
            idx = skills_idx + 1
            while idx < len(lines) and lines[idx].strip() != "":
                idx += 1
            lines.insert(idx, " • " + " • ".join(missing_keywords))
        else:
            lines.append("\nSuggested Keywords for ATS: " + ", ".join(missing_keywords))

    optimized_resume = "\n".join(lines)
    return optimized_resume