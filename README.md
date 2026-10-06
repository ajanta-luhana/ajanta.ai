Ajanta AI

An interactive AI assistant that represents Ajanta Luhana, an AI Software Engineer. Visitors can ask about her experience, projects, certifications and skills, and get answers grounded in a verified knowledge base, with source citations. Built with Python, FastAPI and retrieval-augmented generation (RAG).

Live demo: add your Render link here

Show Image Add a screenshot at docs/screenshot.png.

Features
Chat UI with a 3D animated avatar, typing indicator and streamed answers
RAG pipeline: intent detection, BM25 retrieval, relevance threshold
Source citations on every personal answer
Hallucination guardrails: unsupported questions get a "not verified" reply, and prompt-injection attempts are refused
Optional LLM (any OpenAI-compatible API). Without a key, answers are extracted directly from the sources
Hire Ajanta form that matches a requirement against her verified skills and projects
Feedback buttons (thumbs up/down), copy, regenerate, voice input and read-aloud (browser Web Speech API)
Admin API: analytics, flagged answers, anonymized CSV export, re-index (protected by a token)
Rate limiting, input validation, Docker, GitHub Actions CI, automated tests
How it works
question
  -> intent detection (profile, experience, projects, skills, technical, ...)
  -> BM25 retrieval over knowledge/*.md (filtered by intent)
  -> relevance threshold (below it: "not verified" reply)
  -> LLM answer using only the retrieved sources (or extractive answer without a key)
  -> grounding check (personal answers must cite valid [S#] sources)
  -> streamed to the UI with source cards

If the grounding check fails, the answer is replaced with the fallback message and flagged in the admin analytics.

Project structure
app/
  api/        chat, hire, admin routes
  core/       config, security (rate limit, admin auth), logging
  llm/        prompts, guardrails, LLM provider
  rag/        chunking, ingestion, retriever
  services/   chat pipeline, hire matching, analytics
  models/     schemas, SQLite database
knowledge/    personal/, projects/, technical/ Markdown + metadata/sources.json
frontend/     index.html (chat UI), ajanta.jpg, privacy.html
scripts/      ingest.py (check the index), build_demo.py (static demo page)
tests/        pytest suite
Run locally

Requires Python 3.11+.

Windows (PowerShell)

powershell
pip install -r requirements.txt
$env:ADMIN_TOKEN = "test"
python -m uvicorn app.main:app

Mac / Linux

bash
pip install -r requirements.txt
ADMIN_TOKEN=test python -m uvicorn app.main:app

Open http://localhost:8000. Run the tests with pytest -q.

Docker: docker compose up --build

Configuration

Copy .env.example to .env.

Variable	Purpose
ADMIN_TOKEN	Bearer token for /api/admin/* (required for admin routes)
OPENAI_API_KEY	Optional. Enables LLM-written answers
OPENAI_MODEL, OPENAI_BASE_URL	Model and endpoint for any OpenAI-compatible API
CONTACT_EMAIL	Shown in fallback answers
ALLOWED_ORIGINS	CORS origins, set to your public URL
RATE_LIMIT_PER_MIN	Per-IP request limit (default 20)
DATABASE_PATH	SQLite file (default data/ajanta.db)
Updating the knowledge base

All answers come from the Markdown files in knowledge/. Edit a file, then run python -m scripts.ingest to check the index, or call POST /api/admin/reindex on a running server. Lines containing TODO are ignored.

API
Endpoint	Description
POST /api/chat	Streamed (SSE) chat answer with sources
POST /api/feedback	Thumbs up/down for an answer
POST /api/hire	Match a requirement against verified skills and projects
GET /api/health	Health check
GET /api/sources/{id}	Source metadata
GET /api/admin/analytics	Usage, flagged answers, feedback (Bearer token)
GET /api/admin/export	Anonymized CSV (Bearer token)
POST /api/admin/reindex	Rebuild the index (Bearer token)
Deploy (Render)
Build command: pip install -r requirements.txt
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Health check path: /api/health
Set ADMIN_TOKEN, CONTACT_EMAIL, ALLOWED_ORIGINS (and optionally OPENAI_API_KEY)
Limitations and roadmap
Retrieval is keyword-based (BM25). Semantic search with embeddings and a vector database (pgvector or Chroma) is the next step, and the retriever is isolated behind a search() method so it can be swapped in app/rag/retriever.py.
Data is stored in SQLite. On hosts with an ephemeral disk, analytics reset on redeploy. Move to PostgreSQL for persistence.
Not built yet: server-side speech-to-text and text-to-speech, email delivery for hire requests, reranking, an evaluation set, and observability tooling.
The avatar is an animated photo, not a lip-synced video.
Author

Ajanta Luhana. Email: ajantaluhana@gmail.com. LinkedIn. GitHub.
