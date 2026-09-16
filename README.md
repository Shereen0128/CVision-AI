# CVision AI 🤖📄

CVision AI is an AI-powered resume analysis platform that analyzes resumes and provides intelligent career insights.

## 🚀 Live Demo

https://cvision-ai-frontend.onrender.com/

## 📌 Overview

CVision AI allows users to upload a PDF resume and receive an AI-generated analysis including:

- Detected career field
- Primary job role
- Professional summary
- ATS score
- Job match percentage
- Extracted skills
- Missing skills
- Experience summary
- Recommended career roles
- AI-powered improvement suggestions

The system is designed to work across different professional fields instead of being limited to a single career domain.

## ✨ Features

### 📄 Resume Upload
Upload a PDF resume directly through the web interface.

### 🤖 AI Resume Analysis
Uses AI to analyze resume content and generate meaningful career insights.

### 🎯 Field & Role Detection
Automatically identifies the candidate's professional field and most relevant role.

### 📊 ATS Score
Provides an estimated ATS compatibility score based on the resume content.

### 💼 Job Match
Estimates how well the resume matches the detected career direction.

### 🛠️ Skills Analysis
Identifies skills found in the resume and highlights missing or recommended skills.

### 📈 Career Recommendations
Suggests relevant roles and areas for improvement.

### 💡 AI Suggestions
Provides actionable recommendations to improve resume quality.

## 🏗️ System Workflow

```text
PDF Resume
     ↓
Text Extraction
     ↓
AI Resume Analysis
     ↓
Field & Role Detection
     ↓
Skills Analysis
     ↓
ATS & Job Match
     ↓
Career Recommendations
     ↓
Dashboard
🧰 Tech Stack
Frontend
HTML5
CSS3
JavaScript
Backend
Python
Flask
Flask-CORS
PyPDF
AI
OpenRouter API
AI-powered resume analysis
DevOps & Deployment
Docker
Git
GitHub
Render
📂 Project Structure
CVision-AI/
│
├── backend/
│   ├── app.py
│   └── requirements.txt
│
├── frontend/
│   ├── dashboard.html
│   ├── upload.html
│   ├── css/
│   └── js/
│
├── docker/
│   └── Dockerfile
│
├── .gitignore
└── README.md
⚙️ Local Setup
1. Clone the repository
git clone https://github.com/Shereen0128/CVision-AI.git
cd CVision-AI
2. Create a virtual environment
python -m venv .venv
3. Activate the environment

Windows:

.venv\Scripts\activate
4. Install dependencies
pip install -r backend/requirements.txt
5. Configure environment variables

Create a .env.local file inside the backend directory:

OPENROUTER_API_KEY=your_api_key_here
6. Run the backend
cd backend
python app.py

The backend will run on:

http://127.0.0.1:5000
🌐 Deployment

CVision AI is deployed using Render.

Frontend: Render
Backend: Render
Source Code: GitHub
🔐 Security

API keys and environment files are excluded from version control using .gitignore.

🎯 Project Goal

The goal of CVision AI is to provide an accessible AI-powered resume analysis tool that helps candidates understand their resume strengths, identify missing skills, improve ATS compatibility, and discover suitable career opportunities.

🔮 Future Improvements
Job description matching
Resume improvement suggestions
Resume rewriting
Multiple resume comparison
Job recommendation system
Advanced ATS analysis
Career roadmap generation
User accounts and saved analyses
👩‍💻 Developer

Shereen Hasnain

BS Computer Science
DevOps & Cloud Infrastructure Enthusiast

GitHub:
https://github.com/Shereen0128