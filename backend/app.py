from flask import Flask, request, jsonify
from flask_cors import CORS
from pypdf import PdfReader
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import json
import urllib.request
import urllib.error

load_dotenv(os.path.join(os.path.dirname(__file__), ".env.local"))

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join("backend", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LAST_ANALYSIS = {
    "status": "idle",
    "filename": "",
    "pages": 0,
    "field": "",
    "primary_role": "",
    "summary": "",
    "skills": [],
    "skill_count": 0,
    "skills_by_category": {},
    "missing_skills": [],
    "ats_score": 0,
    "job_match": 0,
    "experience_summary": "",
    "suggestions": [],
    "recommended_roles": [],
    "text": "",
}


# ==========================================
# OPENROUTER AI
# ==========================================

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "nex-agi/nex-n2.5-mini:free"

def analyze_with_openrouter(resume_text):
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not configured.")

    prompt = f"""
You are an expert AI resume analyzer.

Analyze the following resume carefully.

IMPORTANT:
- The resume can belong to ANY professional field.
- Do NOT assume the field is DevOps, MERN, Python, or AI/ML.
- It can be technical or non-technical.
- Automatically identify the candidate's actual field and likely primary role.
- Analyze the resume based on that field.
- Do not invent skills, experience, education, or achievements.
- Give realistic ATS and job-match scores from 0 to 100.

Return ONLY valid JSON.
Do not use markdown.
Do not add explanations outside the JSON.

Required JSON structure:

{{
  "field": "main professional field",
  "primary_role": "most suitable primary role",
  "summary": "short professional summary of the candidate",
  "skills": ["skill 1", "skill 2"],
  "skills_by_category": {{
    "category": ["skill 1", "skill 2"]
  }},
  "missing_skills": ["skill 1", "skill 2"],
  "ats_score": 0,
  "job_match": 0,
  "experience_summary": "short summary of experience",
  "suggestions": [
    "specific improvement 1",
    "specific improvement 2",
    "specific improvement 3"
  ],
  "recommended_roles": [
    "role 1",
    "role 2",
    "role 3"
  ]
}}

Rules:
- "field" should describe the actual domain, for example:
  Software Engineering, DevOps, Marketing, Finance, HR, Education,
  Healthcare, Graphic Design, Sales, Accounting, etc.
- "primary_role" should be the strongest role suggested by the resume.
- "skills" should contain skills actually found or clearly supported by the resume.
- "missing_skills" should contain useful skills commonly expected for the identified primary role but not clearly present in the resume.
- "ats_score" should reflect resume quality, structure, keywords, clarity, and relevance.
- "job_match" should reflect how strongly the resume matches the identified primary role.
- Keep suggestions practical and resume-focused.

RESUME:

{resume_text}
"""

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional resume analysis AI. Always return valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 2500
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        OPENROUTER_API_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://cvision-ai-frontend.onrender.com",
            "X-Title": "CVision AI"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            response_data = response.read().decode("utf-8")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        raise ValueError(
            f"OpenRouter API error {e.code}: {error_body[:500]}"
        )

    except urllib.error.URLError as e:
        raise ValueError(
            f"Could not connect to OpenRouter: {str(e)}"
        )

    result = json.loads(response_data)

    try:
        ai_content = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise ValueError("Invalid response received from OpenRouter.")

    # Remove accidental markdown code fences if the model adds them
    ai_content = ai_content.strip()

    if ai_content.startswith("```"):
        ai_content = ai_content.replace("```json", "", 1)
        ai_content = ai_content.replace("```", "", 1)
        ai_content = ai_content.strip()

    try:
        analysis = json.loads(ai_content)
    except json.JSONDecodeError:
        raise ValueError("OpenRouter returned invalid JSON.")

    return analysis


# ==========================================
# PDF TEXT EXTRACTION
# ==========================================

def extract_resume_text(file_path):
    reader = PdfReader(file_path)
    extracted_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text += text + "\n"

    if not extracted_text.strip():
        raise ValueError("Could not extract text from this PDF.")

    return extracted_text, len(reader.pages)


# ==========================================
# NORMALIZE AI RESULT
# ==========================================

def normalize_analysis(ai_analysis, filename, pages, resume_text):
    skills = ai_analysis.get("skills", [])
    skills_by_category = ai_analysis.get("skills_by_category", {})
    missing_skills = ai_analysis.get("missing_skills", [])
    suggestions = ai_analysis.get("suggestions", [])
    recommended_roles = ai_analysis.get("recommended_roles", [])

    if not isinstance(skills, list):
        skills = []

    if not isinstance(skills_by_category, dict):
        skills_by_category = {}

    if not isinstance(missing_skills, list):
        missing_skills = []

    if not isinstance(suggestions, list):
        suggestions = []

    if not isinstance(recommended_roles, list):
        recommended_roles = []

    try:
        ats_score = int(ai_analysis.get("ats_score", 0))
    except (TypeError, ValueError):
        ats_score = 0

    try:
        job_match = int(ai_analysis.get("job_match", 0))
    except (TypeError, ValueError):
        job_match = 0

    ats_score = max(0, min(100, ats_score))
    job_match = max(0, min(100, job_match))

    return {
        "status": "success",
        "filename": filename,
        "pages": pages,

        "field": str(ai_analysis.get("field", "Not identified")),
        "primary_role": str(
            ai_analysis.get("primary_role", "Not identified")
        ),

        "summary": str(
            ai_analysis.get("summary", "")
        ),

        "skills": skills,
        "skill_count": len(skills),
        "skills_by_category": skills_by_category,

        "missing_skills": missing_skills,

        "ats_score": ats_score,
        "job_match": job_match,

        "experience_summary": str(
            ai_analysis.get("experience_summary", "")
        ),

        "suggestions": suggestions,
        "recommended_roles": recommended_roles,

        "text": resume_text,
    }


# ==========================================
# ROUTES
# ==========================================

@app.route("/")
def home():
    return "CVision AI Backend is Running!"


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "CVision AI backend is running."
    })


@app.route("/api/upload", methods=["POST"])
def upload_resume_api():

    if "resume" not in request.files:
        return jsonify({
            "error": "No file uploaded"
        }), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({
            "error": "No file selected"
        }), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "error": "Only PDF files are supported."
        }), 400

    safe_name = secure_filename(file.filename)

    if not safe_name:
        return jsonify({
            "error": "Invalid filename."
        }), 400

    file_path = os.path.join(UPLOAD_FOLDER, safe_name)

    try:
        file.save(file_path)

        # Extract resume text
        resume_text, pages = extract_resume_text(file_path)

        # Send resume to OpenRouter AI
        ai_analysis = analyze_with_openrouter(resume_text)

        # Prepare final response
        analysis = normalize_analysis(
            ai_analysis,
            safe_name,
            pages,
            resume_text
        )

        global LAST_ANALYSIS
        LAST_ANALYSIS = analysis

        return jsonify(analysis), 200

    except Exception as e:
        return jsonify({
            "error": "Resume analysis failed.",
            "details": str(e)
        }), 500


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
        "field": "",
        "primary_role": "",
        "summary": "",
        "skills": [],
        "skill_count": 0,
        "skills_by_category": {},
        "missing_skills": [],
        "ats_score": 0,
        "job_match": 0,
        "experience_summary": "",
        "suggestions": [
            "Upload a resume to begin AI analysis."
        ],
        "recommended_roles": []
    }), 200


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
