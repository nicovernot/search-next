from fastapi import Cookie, Request
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.models.user import User
from app.settings import settings

logger = get_logger(__name__)

_COOKIE_NAME = "htmx_session"


def get_optional_hypermedia_user(
    request: Request,
    db: Session = None,
    htmx_session: str | None = Cookie(default=None, alias=_COOKIE_NAME),
) -> User | None:
    """Lit le JWT depuis le cookie htmx_session. Retourne None si absent ou invalide."""
    if not htmx_session:
        return None
    try:
        payload = jwt.decode(htmx_session, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        logger.debug("Invalid htmx_session cookie — ignoring")
        return None

    if db is None:
        return None
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user if (user and user.is_active) else None


def htmx_redirect_if_not_htmx(request: Request, path: str) -> RedirectResponse | None:
    """
    Redirige vers la page complète si la requête n'est pas HTMX.
    Utilisation : appeler en début d'endpoint fragment-only.
    """
    if request.headers.get("HX-Request") != "true":
        return RedirectResponse(url=path, status_code=302)
    return None
