Ajanta AI

An interactive AI assistant representing Ajanta Luhana, an AI Software Engineer. It answers questions about her experience, projects, certifications, skills, and technical expertise using a verified knowledge base with source citations.

Built with Python, FastAPI, RAG, BM25 retrieval, and an optional OpenAI-compatible LLM.

Features
Interactive chat UI with animated avatar, streaming responses, typing indicator, voice input, and read-aloud
RAG pipeline with intent detection, BM25 retrieval, relevance thresholds, and source citations
Hallucination protection with "not verified" fallbacks and prompt-injection detection
Optional LLM integration; works without an API key using extractive answers
Hire Ajanta feature for matching requirements with verified skills and projects
Feedback, copy, and regenerate controls
Admin API for analytics, flagged responses, CSV export, and knowledge-base reindexing
Rate limiting, input validation, Docker support, CI, and automated tests
How It Works
Question
   ↓
Intent Detection
   ↓
BM25 Retrieval from knowledge/
   ↓
Relevance Check
   ↓
LLM / Extractive Answer
   ↓
Grounding & Citation Check
   ↓
Streamed Response with Sources

Unsupported or poorly grounded answers are replaced with a "not verified" response and flagged for review.

Project Structure
app/
├── api/        # Chat, hire & admin routes
├── core/       # Configuration, security & logging
├── llm/        # Prompts, guardrails & LLM provider
├── rag/        # Ingestion, chunking & retrieval
├── services/   # Chat, hiring & analytics
└── models/     # Schemas & database

knowledge/      # Verified personal, project & technical knowledge
frontend/       # Chat UI & static pages
scripts/        # Ingestion & demo utilities
tests/          # Automated tests
Run Locally

Requires Python 3.11+.

Windows
pip install -r requirements.txt
$env:ADMIN_TOKEN = "test"
python -m uvicorn app.main:app
macOS / Linux
pip install -r requirements.txt
ADMIN_TOKEN=test python -m uvicorn app.main:app

Open http://localhost:8000

Run tests:

pytest -q

Or with Docker:

docker compose up --build
Configuration

Copy .env.example to .env.

Variable	Purpose
ADMIN_TOKEN	Authentication for admin routes
OPENAI_API_KEY	Optional LLM access
OPENAI_MODEL	LLM model
OPENAI_BASE_URL	OpenAI-compatible endpoint
CONTACT_EMAIL	Contact shown in fallback responses
ALLOWED_ORIGINS	CORS configuration
RATE_LIMIT_PER_MIN	Per-IP request limit
DATABASE_PATH	SQLite database path
Knowledge Base

All personal answers are grounded in Markdown files under knowledge/.

After updating the knowledge base:

python -m scripts.ingest

Or use:

POST /api/admin/reindex
API
Endpoint	Description
POST /api/chat	Streamed chat responses with sources
POST /api/feedback	Submit answer feedback
POST /api/hire	Match requirements with verified skills
GET /api/health	Health check
GET /api/sources/{id}	Source metadata
GET /api/admin/analytics	Analytics and flagged answers
GET /api/admin/export	Anonymized CSV export
POST /api/admin/reindex	Rebuild knowledge index
Deployment

Designed for Render.

Build:  pip install -r requirements.txt
Start:  uvicorn app.main:app --host 0.0.0.0 --port $PORT
Health: /api/health

Configure ADMIN_TOKEN, CONTACT_EMAIL, ALLOWED_ORIGINS, and optionally OPENAI_API_KEY.

Roadmap
Semantic search with embeddings and a vector database
PostgreSQL for persistent analytics
Reranking and evaluation framework
Server-side speech-to-text / text-to-speech
Email delivery for hire requests
Observability and monitoring
Lip-synced avatar
Author

Ajanta Luhana — AI Software Engineer
Email: ajantaluhana@gmail.com
LinkedIn · GitHub
