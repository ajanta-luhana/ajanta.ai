from fastapi import APIRouter, Depends, Request

from app.core.security import rate_limit
from app.models.schemas import HireRequest
from app.services import hire_service

router = APIRouter()


@router.post("/hire", dependencies=[Depends(rate_limit)])
def hire(body: HireRequest, request: Request):
    result = hire_service.match(body, request.app.state.retriever)
    hire_service.save(body)
    # Email integration is Phase 2: send `body` to CONTACT_EMAIL via SMTP/provider here.
    return result
