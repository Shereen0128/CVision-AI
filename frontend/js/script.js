const API_BASE_URL = "http://127.0.0.1:5000";

function getElement(id) {
    return document.getElementById(id);
}

function setText(id, value, fallback = "—") {
    const element = getElement(id);
    if (!element) return;

    element.textContent =
        value !== undefined && value !== null && value !== ""
            ? value
            : fallback;
}

function renderList(id, items, emptyMessage = "None found") {
    const element = getElement(id);
    if (!element) return;

    element.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
        const li = document.createElement("li");
        li.textContent = emptyMessage;
        element.appendChild(li);
        return;
    }

    items.forEach(item => {
        const li = document.createElement("li");

        if (typeof item === "string") {
            li.textContent = item;
        } else {
            li.textContent =
                item.name ||
                item.title ||
                item.role ||
                item.skill ||
                JSON.stringify(item);
        }

        element.appendChild(li);
    });
}

function renderAnalysis(data) {
    setText("detectedField", data.field, "Not identified");
    setText("primaryRole", data.primary_role, "Not identified");
    setText("resumeSummary", data.summary, "No summary available.");

    setText(
        "atsScore",
        data.ats_score !== undefined ? `${data.ats_score} / 100` : "0 / 100"
    );

    setText(
        "jobMatch",
        data.job_match !== undefined ? `${data.job_match}%` : "0%"
    );

    setText(
        "skillCount",
        data.skill_count !== undefined ? `${data.skill_count} Skills` : "0 Skills"
    );

    setText("pageCount", data.pages !== undefined ? data.pages : "--");

    renderList("skillsList", data.skills, "No skills detected.");
    renderList(
        "missingSkillsList",
        data.missing_skills,
        "No major missing skills identified."
    );

    setText(
        "experienceSummary",
        data.experience_summary,
        "No experience summary available."
    );

    renderList(
        "recommendedRolesList",
        data.recommended_roles,
        "No recommended roles available."
    );

    renderList(
        "suggestionsList",
        data.suggestions,
        "No suggestions available."
    );
}

async function analyzeResume(file) {
    if (!file) {
        alert("Please select a PDF file.");
        return;
    }

    const uploadResult = getElement("uploadResult");
    const analyzeBtn = getElement("analyzeBtn");

    if (uploadResult) {
        uploadResult.textContent = "Uploading and analyzing...";
    }

    if (analyzeBtn) {
        analyzeBtn.disabled = true;
    }

    const formData = new FormData();
    formData.append("resume", file);

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/upload`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        console.log("Backend response:", data);

        if (!response.ok) {
            throw new Error(
                data.error ||
                data.details ||
                "Resume analysis failed."
            );
        }

        localStorage.setItem(
            "resumeAnalysis",
            JSON.stringify(data)
        );

        if (data.primary_role) {
            localStorage.setItem("jobRole", data.primary_role);
        }

        renderAnalysis(data);
        alert("Resume uploaded and analyzed successfully!");
        document.location.href = "dashboard.html";

    } catch (error) {
        console.error("Upload error:", error);
        if (uploadResult) {
            uploadResult.textContent = "Upload failed. Please try again.";
        }
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
        }
        alert(error.message || "Resume analysis failed.");
    }
}

function setupUpload() {
    const fileInput = getElement("resumeFile");
    const analyzeBtn = getElement("analyzeBtn");

    if (!fileInput) {
        console.error("resumeFile not found.");
        return;
    }

    if (analyzeBtn) {
        analyzeBtn.addEventListener("click", function () {
            const file = fileInput.files[0];

            if (!file) {
                alert("Please select your resume PDF first.");
                return;
            }

            analyzeResume(file);
        });
    }

    fileInput.addEventListener("change", function () {
        const file = this.files[0];
        const fileStatus = getElement("fileStatus");

        if (!fileStatus) return;

        fileStatus.textContent = file
            ? `Selected file: ${file.name}`
            : "No file selected.";
    });
}

function loadSavedAnalysis() {
    try {
        const saved = localStorage.getItem("resumeAnalysis");

        if (!saved) return;

        const data = JSON.parse(saved);
        renderAnalysis(data);

    } catch (error) {
        console.error("Saved analysis error:", error);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    setupUpload();
    loadSavedAnalysis();
});