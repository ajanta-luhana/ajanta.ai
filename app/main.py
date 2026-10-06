from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import admin, chat, hire
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.models import database as db
from app.rag.retriever import Retriever

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


def create_app() -> FastAPI:
    s = get_settings()
    setup_logging()
    db.init_db(s.database_path)
    app = FastAPI(title="Ajanta AI", docs_url=None, redoc_url=None)
    app.state.retriever = Retriever(s.knowledge_dir)
    app.add_middleware(CORSMiddleware, allow_origins=s.allowed_origins, allow_methods=["GET", "POST"], allow_headers=["*"])

    @app.middleware("http")
    async def headers(request: Request, call_next):
        r = await call_next(request)
        r.headers["X-Content-Type-Options"] = "nosniff"
        r.headers["Referrer-Policy"] = "no-referrer"
        return r

    app.include_router(chat.router, prefix="/api")
    app.include_router(hire.router, prefix="/api")
    app.include_router(admin.router, prefix="/api")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "chunks": len(app.state.retriever.chunks)}

    @app.get("/api/sources/{source_id}")
    def source(source_id: str):
        c = app.state.retriever.get(source_id)
        if not c:
            raise HTTPException(404, "Unknown source")
        return {"id": c.id, "title": c.title, "category": c.category, "section": c.section, "url": c.url, "updated": c.meta.get("updated", "")}

    @app.get("/privacy")
    def privacy():
        return FileResponse(FRONTEND / "privacy.html")

    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
    return app


app = create_app()
