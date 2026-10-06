import hmac
import time
from collections import defaultdict, deque

from fastapi import Depends, Header, HTTPException, Request

from app.core.config import get_settings

_hits: dict[str, deque] = defaultdict(deque)


def rate_limit(request: Request) -> None:
    """Sliding-window limiter, per client IP. Swap for Redis when running >1 instance."""
    limit = get_settings().rate_limit_per_min
    ip = request.client.host if request.client else "unknown"
    now, window = time.time(), _hits[ip]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= limit:
        raise HTTPException(429, "Too many requests. Please wait a minute and try again.")
    window.append(now)


def require_admin(authorization: str = Header(default="")) -> None:
    token = get_settings().admin_token
    supplied = authorization.removeprefix("Bearer ").strip()
    if not token or not hmac.compare_digest(supplied, token):
        raise HTTPException(401, "Admin authentication required.")


def reset_rate_limits() -> None:
    _hits.clear()
