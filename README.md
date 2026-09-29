# AI Career & Placement Assistant · CareerIQ

**Analyze. Match. Improve. Succeed.** A presentation-ready full-stack placement companion that turns a resume into skills intelligence, role matches, actionable gaps, a learning journey, AI-grounded career advice, and mock-interview feedback.

## What works

- PDF, DOCX, and TXT resume upload with PyMuPDF/python-docx text extraction
- Pattern-driven NLP skill extraction across nine professional categories
- Resume completeness scoring and contextual improvement suggestions
- TF-IDF + cosine-similarity job ranking against seven seeded, realistic roles
- Skill-gap analysis built directly from required role skills
- Personalized, completion-tracked roadmap
- Mock interview question and scored feedback (relevance, depth, communication, completeness)
- Floating career mentor with retrieval-grounded fallback guidance
- JWT-protected REST API and responsive animated React interface

## Architecture

```text
React/Vite UI → FastAPI REST API → NLP extraction + TF-IDF matcher
                                    ↘ seeded role/knowledge corpus → grounded mentor
```

The app intentionally has a reliable offline mode: role data, retrieval corpus, user session data, and deterministic guidance work without keys or services. This makes it ideal for a demo. The service layer is isolated in `backend/app/services.py`; replace the mentor fallback with Gemini and persistence dictionaries with MongoDB repositories for production deployment.

## Run locally

Prerequisites: Python 3.10+ and Node 20+.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:JWT_SECRET_KEY="a-long-random-development-secret"
uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Create an account, then upload a resume. Use the dashboard, role matches, roadmap, interview, and mentor in that order for the strongest demo story.

## Environment

Copy `.env.example` to `.env` and supply secrets before deployment:

```env
MONGODB_URL=mongodb://localhost:27017/career_iq
GEMINI_API_KEY=your_key
JWT_SECRET_KEY=use-a-long-random-value
```

## API map

| Endpoint | Purpose |
| --- | --- |
| `POST /auth/signup`, `/auth/login` | account and JWT session |
| `POST /resume/analyze` | upload + extraction + scoring |
| `GET /jobs`, `/jobs/matches` | seeded roles and personalized ranks |
| `GET /skills/gap/{role_id}` | matched and missing skills |
| `GET /roadmap/{role_id}` | generated journey |
| `POST /roadmap/progress` | persist completion state |
| `POST /interview/start`, `/interview/evaluate` | mock interview flow |
| `POST /chat` | grounded mentor response |
| `GET /analytics` | career-readiness summary |

## Production extension points

1. Add `motor`/Mongo repositories for users, resumes, roadmaps, sessions, and chats.
2. Add SentenceTransformers + FAISS in a `rag/` package for large knowledge sets; the current small corpus uses deterministic lexical retrieval so the app always runs locally.
3. Implement a `GeminiProvider` that receives only retrieved context plus profile summary, and preserve the current response as an API-failure fallback.
4. Replace the minimal password demo store with bcrypt hashing before production.
