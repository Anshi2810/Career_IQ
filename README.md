# 🚀 AI Career & Placement Assistant — CareerIQ

### **Analyze. Match. Improve. Succeed.**

CareerIQ is a full-stack AI-powered placement assistant that transforms your resume into **skills intelligence, job matches, skill gaps, learning roadmaps, career guidance, and mock-interview feedback.**

## ✨ Features

* 📄 **Resume Analysis** — PDF, DOCX & TXT extraction
* 🧠 **NLP Skill Extraction** — identifies skills across 9 categories
* 🎯 **Job Matching** — TF-IDF + Cosine Similarity
* 🔍 **Skill Gap Analysis** — matched vs. missing skills
* 🗺️ **Learning Roadmap** — personalized & progress-tracked
* 🤖 **AI Career Mentor** — retrieval-grounded career guidance
* 🎤 **Mock Interviews** — question generation & response evaluation
* 🔐 **JWT Authentication** — protected REST APIs
* 📊 **Career Analytics** — career-readiness insights

## 🏗️ Architecture

```text
React/Vite
    ↓
FastAPI REST API
    ↓
NLP + TF-IDF Matching
    ↓
Role & Knowledge Corpus
    ↓
Career Insights
```

## 🛠️ Tech Stack

**Frontend:** React, Vite
**Backend:** Python, FastAPI
**AI/NLP:** NLP, TF-IDF, Cosine Similarity
**Documents:** PyMuPDF, python-docx
**Auth:** JWT
**Planned:** Gemini, SentenceTransformers, FAISS, MongoDB

## 🚀 Run Locally

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:JWT_SECRET_KEY="your-secret"
uvicorn app.main:app --reload --port 8000
```

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

## 🔄 Workflow

```text
Resume
  ↓
Skill Analysis
  ↓
Role Matching
  ↓
Skill Gaps
  ↓
Learning Roadmap
  ↓
Mock Interview
  ↓
Career Mentor
```

### 🎯 Goal

**Turn a static resume into an interactive, personalized career journey.**
