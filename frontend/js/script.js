const uploadPage = document.getElementById("resumeFile");
const analyzeBtn = document.getElementById("analyzeBtn");
const uploadResult = document.getElementById("uploadResult");

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB


// ===============================
// Resume File Selection
// ===============================

if (uploadPage) {

    uploadPage.addEventListener("change", function (event) {

        const file = event.target.files[0];
        const fileInfo = document.getElementById("fileInfo");
        const fileStatus = document.getElementById("fileStatus");

        if (!file) {
            return;
        }

        // PDF check
        if (file.type !== "application/pdf") {

            if (fileStatus) {
                fileStatus.textContent = "Please select a PDF file.";
            }

            uploadPage.value = "";
            return;
        }

        // 5MB check
        if (file.size > MAX_FILE_SIZE) {

            if (fileStatus) {
                fileStatus.textContent =
                    "File is too large. Maximum size is 5MB.";
            }

            uploadPage.value = "";
            return;
        }

        if (fileInfo) {
            fileInfo.textContent =
                `Selected file: ${file.name}`;
        }

        if (fileStatus) {
            fileStatus.textContent =
                "Resume selected successfully.";
        }

    });
}


// ===============================
// Analyze Resume
// ===============================

if (analyzeBtn) {

    analyzeBtn.addEventListener("click", async function () {

        const fileInput =
            document.getElementById("resumeFile");

        const file =
            fileInput ? fileInput.files[0] : null;

        const jobRole =
            document.getElementById("jobRole");


        // No file
        if (!file) {

            if (uploadResult) {
                uploadResult.textContent =
                    "Please choose a PDF file first.";
            }

            return;
        }


        // PDF validation
        if (file.type !== "application/pdf") {

            if (uploadResult) {
                uploadResult.textContent =
                    "Only PDF files are allowed.";
            }

            return;
        }


        // 5MB validation
        if (file.size > MAX_FILE_SIZE) {

            if (uploadResult) {
                uploadResult.textContent =
                    "Resume must be smaller than 5MB.";
            }

            return;
        }


        if (uploadResult) {
            uploadResult.textContent =
                `Analyzing ${file.name}...`;
        }


        analyzeBtn.disabled = true;
        analyzeBtn.textContent = "Analyzing...";


        const formData = new FormData();

        formData.append("resume", file);


        try {

            const response = await fetch(
                "http://localhost:5000/api/upload",
                {
                    method: "POST",
                    body: formData,
                }
            );


            const data = await response.json();


            if (!response.ok) {
                throw new Error(
                    data.error || "Upload failed"
                );
            }


            // Save analysis
            localStorage.setItem(
                "resumeAnalysis",
                JSON.stringify(data)
            );


            // Save selected job role
            if (jobRole) {

                localStorage.setItem(
                    "jobRole",
                    jobRole.value
                );

            }


            // Go to dashboard
            window.location.href =
                "dashboard.html";


        } catch (error) {

            console.error(
                "Resume upload error:",
                error
            );

            if (uploadResult) {

                uploadResult.textContent =
                    error.message ||
                    "Something went wrong while uploading.";

            }

        } finally {

            analyzeBtn.disabled = false;
            analyzeBtn.textContent =
                "Analyze Resume";

        }

    });
}


// ===============================
// Dashboard
// ===============================

const dashboardPage =
    document.getElementById("dashboardRoot");


function getStoredAnalysis() {

    const direct =
        localStorage.getItem("resumeAnalysis");


    if (direct) {

        try {

            return JSON.parse(direct);

        } catch (error) {

            console.error(
                "resumeAnalysis parse failed:",
                error
            );

        }

    }


    return null;
}


if (dashboardPage) {

    async function loadDashboard() {

        let storedAnalysis =
            getStoredAnalysis();


        // If localStorage is empty,
        // get latest analysis from backend.

        if (!storedAnalysis) {

            try {

                const response = await fetch(
                    "http://localhost:5000/api/dashboard"
                );

                const data =
                    await response.json();


                if (
                    response.ok &&
                    data &&
                    data.status === "success"
                ) {

                    storedAnalysis = data;

                    localStorage.setItem(
                        "resumeAnalysis",
                        JSON.stringify(data)
                    );

                }

            } catch (error) {

                console.error(
                    "Dashboard fetch failed:",
                    error
                );

            }

        }


        const analysis =
            storedAnalysis || {};


        // ===============================
        // Dashboard Elements
        // ===============================

        const resumeName =
            document.getElementById("resumeName");

        const pageCount =
            document.getElementById("pageCount");

        const skillCount =
            document.getElementById("skillCount");

        const atsScore =
            document.getElementById("atsScore");

        const jobMatch =
            document.getElementById("jobMatch");

        const skillsList =
            document.getElementById("skillsList");

        const suggestionsList =
            document.getElementById("suggestionsList");

        const missingSkillsList =
            document.getElementById("missingSkillsList");


        // ===============================
        // Selected Role
        // ===============================

        const selectedRole =
            localStorage.getItem("jobRole") ||
            "DevOps";


        // ===============================
        // Resume Name
        // ===============================

        if (resumeName) {

            resumeName.textContent =
                analysis.filename
                    ? `Analyzed: ${analysis.filename}`
                    : "Resume Analysis";

        }


        // ===============================
        // Pages
        // ===============================

        if (pageCount) {

            pageCount.textContent =
                analysis.pages
                    ? String(analysis.pages)
                    : "--";

        }


        // ===============================
        // Skills
        // ===============================

        const skills =
            Array.isArray(analysis.skills)
                ? analysis.skills
                : [];


        // ===============================
        // Required Skills by Role
        // ===============================

        const roleSkills = {

            DevOps: [
                "Docker",
                "Kubernetes",
                "Linux",
                "Git",
                "Terraform",
                "Ansible",
                "AWS",
                "Jenkins"
            ],

            Python: [
                "Python",
                "Flask",
                "Django",
                "MySQL",
                "Git"
            ],

            MERN: [
                "React",
                "Node.js",
                "MongoDB",
                "Express.js",
                "JavaScript"
            ],

            AIML: [
                "Python",
                "TensorFlow",
                "PyTorch",
                "Machine Learning",
                "Deep Learning"
            ]

        };


        const requiredSkills =
            roleSkills[selectedRole] || [];


        const missingSkills =
            requiredSkills.filter(
                skill => !skills.includes(skill)
            );


        // ===============================
        // Skill Count
        // ===============================

        if (skillCount) {

            skillCount.textContent =
                `${skills.length} Skills`;

        }


        // ===============================
        // ATS Score
        // ===============================

        if (atsScore) {

            atsScore.textContent =
                `${analysis.ats_score ?? 0} / 100`;

        }


        // ===============================
        // Job Match
        // ===============================

        if (jobMatch) {

            jobMatch.textContent =
                `${analysis.job_match ?? 0}%`;

        }


        // ===============================
        // Skills List
        // ===============================

        if (skillsList) {

            skillsList.innerHTML = "";


            if (skills.length > 0) {

                skills.forEach((skill) => {

                    const li =
                        document.createElement("li");

                    li.textContent = skill;

                    skillsList.appendChild(li);

                });

            } else {

                const li =
                    document.createElement("li");

                li.textContent =
                    "No skills detected.";

                skillsList.appendChild(li);

            }

        }


        // ===============================
        // Missing Skills
        // ===============================

        if (missingSkillsList) {

            missingSkillsList.innerHTML = "";


            if (missingSkills.length > 0) {

                missingSkills.forEach((skill) => {

                    const li =
                        document.createElement("li");

                    li.textContent = skill;

                    missingSkillsList.appendChild(li);

                });

            } else {

                const li =
                    document.createElement("li");

                li.textContent =
                    "No missing skills found.";

                missingSkillsList.appendChild(li);

            }

        }


        // ===============================
        // Suggestions
        // ===============================

        if (suggestionsList) {

            suggestionsList.innerHTML = "";


            const suggestions =
                Array.isArray(analysis.suggestions) &&
                analysis.suggestions.length
                    ? analysis.suggestions
                    : [
                        "Upload a resume to begin analysis."
                    ];


            suggestions.forEach((suggestion) => {

                const li =
                    document.createElement("li");

                li.textContent = suggestion;

                suggestionsList.appendChild(li);

            });

        }

    }


    loadDashboard();

}
