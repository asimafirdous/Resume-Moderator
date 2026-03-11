let optimizedResumeGlobal = ""; 

async function analyzeResume() {

    const fileInput = document.getElementById("resume");
    const companyName = document.getElementById("companyName").value;
    const jobRole = document.getElementById("jobRole").value;
    const jobDescription = document.getElementById("jobDescription").value;

    const progressBar = document.getElementById("progressBar");
    const scoreText = document.getElementById("scoreText");
    const resultDiv = document.getElementById("result");
    const confirmDiv = document.getElementById("confirmDiv");
    const optimizedDiv = document.getElementById("optimizedResumeDiv");

    optimizedDiv.style.display = "none";
    confirmDiv.style.display = "none";

    if (fileInput.files.length === 0) {
        alert("Upload resume first");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("company_name", companyName);
    formData.append("job_role", jobRole);
    formData.append("job_description", jobDescription);

    resultDiv.innerHTML = "Analyzing resume...";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Server error");

        const data = await response.json();

        const score = data.ats_score;
        progressBar.style.width = score + "%";
        scoreText.innerHTML = "<h3>ATS Score: " + score + "%</h3>";

        let suggestionsHtml = "";
        data.improvement_suggestions.forEach(s => {
            suggestionsHtml += "<li>" + s + "</li>";
        });

        resultDiv.innerHTML = `
            <h3>Improvement Suggestions</h3>
            <ul>${suggestionsHtml}</ul>
        `;

        optimizedResumeGlobal = data.optimized_resume;

        confirmDiv.style.display = "block";

    } catch (error) {
        console.error(error);
        resultDiv.innerHTML = `
            <p style="color:red">
            Could not connect to backend. Please try again later.
            </p>
        `;
    }
}

function showOptimizedResume() {
    const optimizedDiv = document.getElementById("optimizedResumeDiv");
    const optimizedPre = document.getElementById("optimizedResume");
    optimizedPre.textContent = optimizedResumeGlobal;
    optimizedDiv.style.display = "block";
    optimizedDiv.scrollIntoView({ behavior: "smooth" });
}

function downloadResume() {
    if (!optimizedResumeGlobal) {
        alert("No optimized resume to download. Please analyze first.");
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const lines = optimizedResumeGlobal.split("\n");
    let y = 10;
    const lineHeight = 7;
    const pageHeight = doc.internal.pageSize.height;
    lines.forEach((line) => {
        if (y > pageHeight - 10) {  
            doc.addPage();
            y = 10;
        }
        doc.text(line, 10, y);
        y += lineHeight;
    });

    doc.save("Optimized_Resume.pdf");
}