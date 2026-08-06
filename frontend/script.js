let optimizedResumeGlobal = "";

document.getElementById("resumeForm").addEventListener("submit", (event) => {
    event.preventDefault();
    analyzeResume();
});

function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = value;
    return element.innerHTML;
}

async function analyzeResume() {
    const fileInput = document.getElementById("resume");
    const companyName = document.getElementById("companyName").value.trim();
    const jobRole = document.getElementById("jobRole").value.trim();
    const jobDescription = document.getElementById("jobDescription").value.trim();
    const progressBar = document.getElementById("progressBar");
    const scoreText = document.getElementById("scoreText");
    const resultDiv = document.getElementById("result");
    const confirmDiv = document.getElementById("confirmDiv");
    const optimizedDiv = document.getElementById("optimizedResumeDiv");
    const analyzeButton = document.getElementById("analyzeButton");

    optimizedDiv.style.display = "none";
    confirmDiv.style.display = "none";
    progressBar.style.width = "0%";
    scoreText.innerHTML = "";

    if (fileInput.files.length === 0 || !jobDescription) {
        resultDiv.innerHTML = '<p class="error-message">Please upload your resume and add the job description.</p>';
        return;
    }

    const file = fileInput.files[0];
    if (!file.name.toLowerCase().endsWith(".pdf")) {
        resultDiv.innerHTML = '<p class="error-message">Please choose a PDF resume.</p>';
        return;
    }
    if (file.size > 4 * 1024 * 1024) {
        resultDiv.innerHTML = '<p class="error-message">Please choose a PDF smaller than 4 MB.</p>';
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("company_name", companyName);
    formData.append("job_role", jobRole);
    formData.append("job_description", jobDescription);

    resultDiv.innerHTML = '<p class="loading-message">Analyzing your resume…</p>';
    analyzeButton.disabled = true;
    analyzeButton.textContent = "Analyzing…";

    try {
        const response = await fetch("/api/analyze", { method: "POST", body: formData });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || data.error || "Unable to analyze the resume.");

        progressBar.style.width = `${data.ats_score}%`;
        scoreText.innerHTML = `<h2>ATS match: ${data.ats_score}%</h2>`;
        const suggestions = data.improvement_suggestions.map((suggestion) => `<li>${escapeHtml(suggestion)}</li>`).join("");
        resultDiv.innerHTML = `<h2>Keyword suggestions</h2>${suggestions ? `<ul>${suggestions}</ul>` : '<p class="success-message">Great match — no missing keywords were found.</p>'}`;
        optimizedResumeGlobal = data.optimized_resume;
        confirmDiv.style.display = "block";
    } catch (error) {
        console.error(error);
        resultDiv.innerHTML = `<p class="error-message">${escapeHtml(error.message || "Could not connect to the backend. Please try again.")}</p>`;
    } finally {
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analyze resume";
    }
}

function showOptimizedResume() {
    document.getElementById("optimizedResume").textContent = optimizedResumeGlobal;
    const optimizedDiv = document.getElementById("optimizedResumeDiv");
    optimizedDiv.style.display = "block";
    optimizedDiv.scrollIntoView({ behavior: "smooth", block: "start" });
}

function downloadResume() {
    if (!optimizedResumeGlobal) return;
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const lines = doc.splitTextToSize(optimizedResumeGlobal, 190);
    let y = 10;
    const lineHeight = 7;
    const pageHeight = doc.internal.pageSize.height;
    lines.forEach((line) => {
        if (y > pageHeight - 10) { doc.addPage(); y = 10; }
        doc.text(line, 10, y);
        y += lineHeight;
    });
    doc.save("Optimized_Resume.pdf");
}
