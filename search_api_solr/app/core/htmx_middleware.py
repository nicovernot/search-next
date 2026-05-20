from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)

_HX_HEADERS = (
    "hx-request", "hx-boosted", "hx-current-url",
    "hx-target", "hx-trigger", "hx-trigger-name",
)


class HtmxLoggingMiddleware(BaseHTTPMiddleware):
    """Log les headers HX-* sur les requêtes HTMX — dev uniquement."""

    async def dispatch(self, request: Request, call_next):
        if request.headers.get("hx-request") == "true":
            htmx_ctx = {
                h: request.headers[h]
                for h in _HX_HEADERS
                if h in request.headers
            }
            logger.debug(
                "HTMX request",
                extra={"context": {"path": request.url.path, "htmx": htmx_ctx}},
            )
        return await call_next(request)
