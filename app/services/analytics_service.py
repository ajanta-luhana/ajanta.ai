import csv
import io

from app.models import database as db

DAY = 86400


def summary(doc_count: int) -> dict:
    now = db.now()
    one = lambda sql, a=(): list(db.query(sql, a)[0].values())[0] or 0
    return {
        "total_messages": one("SELECT COUNT(*) FROM messages"),
        "last_24h": one("SELECT COUNT(*) FROM messages WHERE ts>?", (now - DAY,)),
        "last_7d": one("SELECT COUNT(*) FROM messages WHERE ts>?", (now - 7 * DAY,)),
        "avg_latency_ms": round(one("SELECT AVG(latency_ms) FROM messages")),
        "avg_confidence": round(one("SELECT AVG(confidence) FROM messages"), 2),
        "popular_intents": db.query("SELECT intent, COUNT(*) n FROM messages GROUP BY intent ORDER BY n DESC LIMIT 10"),
        "unsupported": db.query("SELECT question, ts FROM messages WHERE intent='UNKNOWN' OR grounded=0 ORDER BY ts DESC LIMIT 25"),
        "flagged": db.query("SELECT id, question, confidence FROM messages WHERE flagged=1 ORDER BY ts DESC LIMIT 25"),
        "feedback": {"up": one("SELECT COUNT(*) FROM feedback WHERE value=1"), "down": one("SELECT COUNT(*) FROM feedback WHERE value=-1")},
        "hire_requests": one("SELECT COUNT(*) FROM hire_requests"),
        "knowledge_documents": doc_count,
    }


def export_csv() -> str:
    """Anonymized: no question text, only metrics."""
    rows = db.query("SELECT ts,intent,grounded,flagged,confidence,latency_ms FROM messages ORDER BY ts")
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["ts", "intent", "grounded", "flagged", "confidence", "latency_ms"])
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()
