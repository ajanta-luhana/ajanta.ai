import json
import re
import time
from collections.abc import AsyncIterator

from app.core.config import get_settings
from app.core.logging import event
from app.llm import guardrails as g
from app.llm.prompts import SYSTEM, build_user_prompt
from app.llm.provider import llm_available, stream_completion
from app.models import database as db
from app.rag.retriever import Retriever


def _snippet(t: str, n: int = 220) -> str:
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


def _extractive(sources: list[dict]) -> str:
    """No-LLM mode: answer directly from the best sources, still cited."""
    n = 2
    if len(sources) > 2 and (sources[0]["category"] == "projects" or sum(len(x["text"]) for x in sources[:4]) < 900):
        n = min(4, len(sources))  # short sections (skills) or project overviews: show more
    return "\n\n".join(f"**{s['title']}**: {_snippet(s['text'], 380)} [S{i+1}]" for i, s in enumerate(sources[:n]))


def sse(obj: dict) -> str:
    return f"data: {json.dumps(obj)}\n\n"


async def chat(retriever: Retriever, message: str, history: list[dict]) -> AsyncIterator[str]:
    s, t0 = get_settings(), time.time()
    intent = "UNKNOWN" if g.looks_like_injection(message) else g.detect_intent(message)
    personal = g.is_personal(intent)
    hits = [] if intent in ("UNKNOWN", "HIRE_AJANTA") else retriever.search(message, intent, s.top_k)
    hits = [(c, r) for c, r in hits if r >= s.relevance_threshold]
    sources = [{"id": c.id, "title": c.title, "category": c.category, "section": c.section, "url": c.url,
                "confidence": r, "snippet": _snippet(c.text), "text": c.text} for c, r in hits]
    public = [{k: v for k, v in x.items() if k != "text"} for x in sources]
    confidence = max((x["confidence"] for x in sources), default=0.0)
    yield sse({"type": "meta", "intent": intent})

    answer, grounded, send_full = "", True, True
    if intent == "HIRE_AJANTA":
        answer = "Great, let's see if Ajanta is a fit. Use the **Hire Ajanta** form to tell me the role and scope, and I'll match it against the verified profile."
    elif intent == "UNKNOWN" or (personal and not sources):
        answer, grounded = g.FALLBACK + (f" Email: {s.contact_email}" if s.contact_email else ""), False
    else:
        try:
            if llm_available():
                send_full = False
                async for tok in stream_completion(SYSTEM.format(fallback=g.FALLBACK), build_user_prompt(message, sources, history)):
                    answer += tok
                    yield sse({"type": "token", "text": tok})
                if personal and not g.validate_grounding(answer, len(sources)):
                    grounded, send_full, answer = False, True, g.FALLBACK
            else:
                answer = _extractive(sources) if personal else _extractive(sources) + "\n\n*General explanation, not a claim about Ajanta.*"
        except Exception as e:  # provider failure -> graceful degrade
            event("llm_error", error=type(e).__name__)
            answer, send_full = (_extractive(sources) if sources else g.FALLBACK), True
    if send_full:
        yield sse({"type": "replace", "text": answer})

    flagged = int(personal and (not grounded or confidence < 0.5))
    latency = int((time.time() - t0) * 1000)
    mid = db.execute(
        "INSERT INTO messages(ts,intent,question,grounded,flagged,confidence,latency_ms,sources) VALUES(?,?,?,?,?,?,?,?)",
        (db.now(), intent, message[:300], int(grounded), flagged, confidence, latency, ",".join(x["id"] for x in sources)))
    event("chat", intent=intent, grounded=grounded, latency_ms=latency, n_sources=len(sources))
    yield sse({"type": "done", "message_id": mid, "sources": public if grounded else [], "intent": intent})
