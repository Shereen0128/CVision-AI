from flask import Flask, request, jsonify
from flask_cors import CORS
from pypdf import PdfReader
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join("backend", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LAST_ANALYSIS = {
    "status": "idle",
    "filename": "",
    "pages": 0,
    "skills": [],
    "skill_count": 0,
    "skills_by_category": {},
    "ats_score": 0,
    "job_match": 0,
    "suggestions": [],
    "text": "",
}


# ==========================================
# MULTI-DOMAIN SKILLS DATABASE
# ==========================================

SKILLS = {
    "Programming": [
        "Python",
        "Java",
        "C++",
        "C#",
        "JavaScript",
        "TypeScript",
        "Go",
        "Rust",
        "PHP",
        "Ruby",
        "Kotlin",
        "Swift",
        "R",
        "Dart",
    ],
    "Web Development": [
        "HTML",
        "CSS",
        "React",
        "Angular",
        "Vue.js",
        "Next.js",
        "Node.js",
        "Express.js",
        "Django",
        "Flask",
        "Spring Boot",
        "Laravel",
        "Bootstrap",
        "Tailwind CSS",
    ],
    "AI / Machine Learning": [
        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",
        "TensorFlow",
        "PyTorch",
        "Scikit-learn",
        "Keras",
        "OpenCV",
        "NLP",
        "Natural Language Processing",
        "Computer Vision",
        "Neural Networks",
        "Transformers",
        "Hugging Face",
    ],
    "Data Science": [
        "Data Science",
        "Pandas",
        "NumPy",
        "Matplotlib",
        "Seaborn",
        "Jupyter",
        "Power BI",
        "Tableau",
        "Excel",
        "Statistics",
        "Data Analysis",
    ],
    "Databases": [
        "SQL",
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "SQLite",
        "Oracle",
        "Redis",
        "Firebase",
        "Microsoft SQL Server",
    ],
    "Cloud": [
        "AWS",
        "Amazon Web Services",
        "Azure",
        "Microsoft Azure",
        "Google Cloud",
        "GCP",
        "Cloud Computing",
        "EC2",
        "S3",
        "Lambda",
    ],
    "DevOps": [
        "Docker",
        "Kubernetes",
        "Jenkins",
        "Terraform",
        "Ansible",
        "Helm",
        "Linux",
        "Git",
        "GitHub",
        "GitLab",
        "GitHub Actions",
        "CI/CD",
        "CI CD",
        "Prometheus",
        "Grafana",
        "Elasticsearch",
        "Kibana",
        "Logstash",
        "ArgoCD",
    ],
    "Mobile Development": [
        "Android",
        "Android Studio",
        "Flutter",
        "React Native",
        "Kotlin",
        "Swift",
        "iOS",
        "Dart",
    ],
    "Cybersecurity": [
        "Cybersecurity",
        "Network Security",
        "Ethical Hacking",
        "Penetration Testing",
        "Kali Linux",
        "Wireshark",
        "SIEM",
        "SOC",
        "Burp Suite",
        "Metasploit",
        "Cryptography",
        "Firewall",
    ],
    "UI / UX & Design": [
        "UI/UX",
        "UI Design",
        "UX Design",
        "Figma",
        "Adobe XD",
        "Photoshop",
        "Illustrator",
        "Canva",
        "Wireframing",
        "Prototyping",
    ],
    "Tools & Software": [
        "Git",
        "GitHub",
        "GitLab",
        "Jira",
        "Trello",
        "Postman",
        "VS Code",
        "Visual Studio",
        "IntelliJ IDEA",
    ],
}

def normalize_text_for_matching(text):
    return "".join(ch.lower() for ch in text if ch.isalnum())


def generate_suggestions(skills):
    suggestions = []

    if len(skills) < 5:
        suggestions.append("Add more relevant technical skills.")

    if "Git" not in skills:
        suggestions.append("Consider adding Git or version control experience.")

    if "Docker" not in skills:
        suggestions.append("Consider adding Docker or containerization experience.")

    if "CI/CD" not in skills and "Jenkins" not in skills and "GitHub Actions" not in skills:
        suggestions.append("Highlight CI/CD experience or projects.")

    suggestions.append("Add measurable achievements to your resume.")
    suggestions.append("Improve resume keywords for your target job.")

    return suggestions


def calculate_dashboard_metrics(skills):
    if len(skills) >= 15:
        ats_score = 95
        job_match = 90
    elif len(skills) >= 10:
        ats_score = 88
        job_match = 82
    elif len(skills) >= 7:
        ats_score = 80
        job_match = 75
    elif len(skills) >= 4:
        ats_score = 70
        job_match = 65
    elif len(skills) > 0:
        ats_score = 60
        job_match = 55
    else:
        ats_score = 0
        job_match = 0

    return ats_score, job_match


def analyze_resume_file(file_path):
    reader = PdfReader(file_path)
    extracted_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"

    if not extracted_text.strip():
        raise ValueError("Could not extract text from this PDF.")

    normalized_text = normalize_text_for_matching(extracted_text)
    found_skills = []
    skills_by_category = {}

    for category, skills in SKILLS.items():
        category_skills = []
        for skill in skills:
            normalized_skill = normalize_text_for_matching(skill)
            if normalized_skill in normalized_text:
                if skill not in found_skills:
                    found_skills.append(skill)
                category_skills.append(skill)
        if category_skills:
            skills_by_category[category] = category_skills

    ats_score, job_match = calculate_dashboard_metrics(found_skills)
    suggestions = generate_suggestions(found_skills)

    return {
        "status": "success",
        "filename": os.path.basename(file_path),
        "pages": len(reader.pages),
        "text": extracted_text,
        "skills": found_skills,
        "skill_count": len(found_skills),
        "skills_by_category": skills_by_category,
        "ats_score": ats_score,
        "job_match": job_match,
        "suggestions": suggestions,
    }


@app.route("/")
def home():
    return "CVision AI Backend is Running!"


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "CVision AI backend is running."})


@app.route("/api/upload", methods=["POST"])
def upload_resume_api():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    safe_name = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, safe_name)
    file.save(file_path)

    try:
        global LAST_ANALYSIS
        analysis = analyze_resume_file(file_path)
        LAST_ANALYSIS = analysis
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({"error": "Failed to read PDF", "details": str(e)}), 500


@app.route("/upload-resume", methods=["POST"])
def upload_resume_legacy():
    return upload_resume_api()


@app.route("/api/dashboard", methods=["GET"])
def dashboard_data():
    if LAST_ANALYSIS.get("status") == "success":
        return jsonify(LAST_ANALYSIS), 200

    return jsonify({
        "status": "idle",
        "filename": "",
        "pages": 0,
        "skills": [],
        "skill_count": 0,
        "skills_by_category": {},
        "ats_score": 0,
        "job_match": 0,
        "suggestions": ["Upload a resume to begin analysis."],
    }), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
