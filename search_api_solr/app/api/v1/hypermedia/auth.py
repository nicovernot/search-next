"""
Endpoints d'authentification pour le frontend hypermedia.
Échange un Bearer JWT (émis par /auth/login) contre un cookie HttpOnly,
ce qui permet aux formulaires HTMX de ne pas gérer de token en JS.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from pathlib import Path
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.models.user import User
from app.settings import settings

TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "templates" / "hypermedia"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

auth_router = APIRouter(tags=["hypermedia-auth"])
logger = get_logger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)

_COOKIE_NAME = "htmx_session"
_COOKIE_MAX_AGE = settings.access_token_expire_minutes * 60


def _decode_jwt(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("sub")
    except JWTError:
        return None


@auth_router.post(
    "/auth/session",
    response_class=HTMLResponse,
    summary="Échange un Bearer JWT contre un cookie HttpOnly htmx_session",
)
async def create_session(
    response: Response,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """
    Reçoit un Authorization: Bearer <jwt>, valide le token,
    pose un cookie HttpOnly htmx_session et retourne un fragment HTML de confirmation.
    Appelé par le JS du frontend après /auth/login.
    """
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")

    user_id = _decode_jwt(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    response.set_cookie(
        key=_COOKIE_NAME,
        value=credentials.credentials,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
        path="/api/v1/hypermedia",
    )
    logger.info("htmx_session cookie set", extra={"context": {"user_id": user_id}})
    return f'<span id="session-status" aria-live="polite">Connecté</span>'


@auth_router.delete(
    "/auth/session",
    response_class=HTMLResponse,
    summary="Supprime le cookie htmx_session (déconnexion)",
)
async def delete_session(response: Response):
    """Efface le cookie htmx_session."""
    response.delete_cookie(key=_COOKIE_NAME, path="/api/v1/hypermedia")
    logger.info("htmx_session cookie cleared")
    return '<span id="session-status" aria-live="polite">Déconnecté</span>'
