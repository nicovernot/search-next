import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core import security
from app.db.session import get_db
from app.models.auth_models import LdapLogin, Token, UserCreate, UserLogin, UserResponse
from app.models.user import User
from app.settings import settings

log = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Helpers ──────────────────────────────────────────────────────────────────

def _issue_token(user: User) -> Token:
    expires = timedelta(minutes=settings.access_token_expire_minutes)
    token = security.create_access_token(
        subject=user.id,
        expires_delta=expires,
        extra_claims={"email": user.email},
    )
    return Token(access_token=token, token_type="bearer")


def _provision_federated_user(
    db: Session,
    email: str,
    auth_provider: str,
) -> User:
    """
    Returns an existing user by email, or creates one with no password (just-in-time provisioning).
    Raises 409 if email already belongs to a local account and conflict strategy is 'reject'.
    """
    user = db.query(User).filter(User.email == email).first()
    if user:
        if user.auth_provider == "local" and settings.ldap_email_conflict_strategy == "reject":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="email_conflict_local_account",
            )
        # Sync provider on each login
        user.auth_provider = auth_provider
        db.commit()
        db.refresh(user)
        return user

    new_user = User(email=email, hashed_password=None, auth_provider=auth_provider, is_active=True)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ── Local auth ───────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already registered")

    new_user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        auth_provider="local",
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login_user(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()

    if not user or not user.hashed_password:
        # User doesn't exist or is a federated account with no local password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not security.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return _issue_token(user)


# ── LDAP auth ─────────────────────────────────────────────────────────────────

@router.post("/ldap/login", response_model=Token)
def ldap_login(credentials: LdapLogin, db: Session = Depends(get_db)):
    if not settings.ldap_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LDAP not enabled")

    from app.services import ldap_service

    try:
        user_info = ldap_service.authenticate(credentials.username, credentials.password)
    except ValueError as exc:
        detail = str(exc)
        if detail == "ldap_unavailable":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ldap_unavailable",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ldap_invalid_credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = _provision_federated_user(db, email=user_info["email"], auth_provider="ldap")
    return _issue_token(user)


# ── SSO / OIDC ───────────────────────────────────────────────────────────────

@router.get("/sso/login")
async def sso_login():
    if not settings.sso_oidc_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="SSO not enabled")

    from app.services import oidc_service

    try:
        url = await oidc_service.build_authorization_url()
    except Exception:
        log.exception("SSO authorization URL build failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="sso_unavailable",
        )
    return RedirectResponse(url, status_code=302)


@router.get("/sso/callback")
async def sso_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    if not settings.sso_oidc_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="SSO not enabled")

    from app.services import oidc_service

    try:
        user_info = await oidc_service.exchange_code(code, state)
    except ValueError as exc:
        log.warning("SSO callback error: %s", exc)
        error_redirect = f"{settings.frontend_url}?sso_error={exc}"
        return RedirectResponse(error_redirect, status_code=302)
    except Exception:
        log.exception("SSO callback unexpected error")
        error_redirect = f"{settings.frontend_url}?sso_error=sso_unavailable"
        return RedirectResponse(error_redirect, status_code=302)

    user = _provision_federated_user(db, email=user_info["email"], auth_provider="oidc")
    token = _issue_token(user)

    redirect_url = f"{settings.frontend_url}?auth_token={token.access_token}"
    return RedirectResponse(redirect_url, status_code=302)
