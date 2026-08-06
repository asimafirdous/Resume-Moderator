import re


# These words carry little meaning for a keyword comparison. The list is
# intentionally modest so role-specific terms remain in the analysis.
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "in", "is", "it", "of", "on", "or", "that", "the", "this", "to",
    "with", "will", "you", "your", "we", "our", "their", "they", "has",
    "have", "using", "work", "working", "ability", "responsible",
}


def extract_keywords(text):
    """Return meaningful, normalized terms while preserving their order."""
    terms = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}", text.lower())
    normalized_terms = [term.strip(".-") for term in terms]
    return [term for term in normalized_terms if term and term not in STOP_WORDS]


def calculate_ats_score(resume_text, job_description):
    resume_words = set(extract_keywords(resume_text))
    job_keywords = extract_keywords(job_description)
    unique_keywords = list(dict.fromkeys(job_keywords))

    if not unique_keywords:
        return 0, []

    matched = [word for word in unique_keywords if word in resume_words]
    score = round((len(matched) / len(unique_keywords)) * 100, 2)
    missing = [word for word in unique_keywords if word not in resume_words]
    return score, missing
