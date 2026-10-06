# Ajanta AI

Ajanta AI is a production-ready personal AI assistant built with Python, RAG, vector search and LLM orchestration. It provides an interactive representation of Ajanta Luhana's professional profile, projects, technical skills and AI engineering knowledge, using retrieval-grounded generation, source citations and hallucination safeguards, with a recruiter-focused Hire Ajanta workflow and analytics.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # set ADMIN_TOKEN (and OPENAI_API_KEY if you want LLM answers)
uvicorn app.main:app --reload # open http://localhost:8000
pytest -q
```

Docker: `docker compose up --build`.

## Knowledge base

`knowledge/` is filled from the content of the portfolio at github.com/ajanta-luhana/ajanta-portfolio (experience, education, certifications, skills, projects, contact). Nothing else is assumed. To change an answer, edit the Markdown file and run `python -m scripts.ingest` (or `POST /api/admin/reindex`). Lines containing `TODO` are ignored at indexing.

Keep the portfolio and this folder in sync, since the portfolio is the source of truth.

## How it works

Intent detection → BM25 retrieval with intent-based filtering → relevance threshold → LLM answer (or extractive answer if no API key) → grounding validation (personal answers must carry valid `[S#]` citations) → streamed to the UI with source cards. Failed grounding falls back to the "not verified" message and is flagged in the admin dashboard.

## Endpoints

`POST /api/chat` (SSE) · `POST /api/feedback` · `POST /api/hire` · `GET /api/health` · `GET /api/sources/{id}` · admin (Bearer `ADMIN_TOKEN`): `GET /api/admin/analytics`, `GET /api/admin/export`, `POST /api/admin/reindex`

## Status against the requirements

| Area | Status |
|---|---|
| MVP (chat UI, FastAPI, RAG, citations, fallback, Hire flow, Docker, CI) | Done |
| Technical KB, admin analytics, feedback, hire matching, rate limiting, voice (browser-side) | Done |
| Pgvector / ChromaDB + embeddings | Not yet. Retriever is BM25 behind a `search()` interface; swap it in `app/rag/retriever.py` |
| PostgreSQL | Not yet. SQLite for now (`app/models/database.py`) |
| Server-side STT/TTS, email delivery, LangGraph, reranker, Langfuse | Phase 2 |
| 60-question evaluation set | Not yet. `tests/` has the unit and behaviour tests to extend |

## Deploy

Push to GitHub, connect Render/Railway, set the env vars from `.env.example`, mount a persistent disk at `/srv/data`. HTTPS is provided by the host. Set `ALLOWED_ORIGINS` to your public URL.
