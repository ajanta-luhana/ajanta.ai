from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.core.security import rate_limit
from app.models import database as db
from app.models.schemas import ChatRequest, FeedbackRequest
from app.services.chat_service import chat

router = APIRouter()


@router.post("/chat", dependencies=[Depends(rate_limit)])
async def chat_endpoint(body: ChatRequest, request: Request):
    history = [t.model_dump() for t in body.history]
    return StreamingResponse(chat(request.app.state.retriever, body.message.strip(), history),
                             media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.post("/feedback", dependencies=[Depends(rate_limit)])
def feedback(body: FeedbackRequest):
    db.execute("INSERT INTO feedback(message_id,value,ts) VALUES(?,?,?)", (body.message_id, body.value, db.now()))
    return {"ok": True}
