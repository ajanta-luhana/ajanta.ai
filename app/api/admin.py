from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse

from app.core.security import require_admin
from app.services import analytics_service

router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])


@router.get("/analytics")
def analytics(request: Request):
    return analytics_service.summary(request.app.state.retriever.doc_count())


@router.get("/export", response_class=PlainTextResponse)
def export():
    return analytics_service.export_csv()


@router.post("/reindex")
def reindex(request: Request):
    return {"chunks": request.app.state.retriever.reindex()}
