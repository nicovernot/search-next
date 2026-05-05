"""
OIDC/OAuth2 authentication service.

Implements the Authorization Code flow:
  1. build_authorization_url() → redirect to IdP
  2. exchange_code()           → token endpoint → ID token
  3. get_user_info()           → validated claims (email, name)

State is stored in Redis (TTL 10 min) for CSRF protection (NFR-004).
Falls back to in-memory dict when Redis is unavailable (development only).
"""

import secrets
from urllib.parse import urlencode

import httpx
from jose import JWTError
from jose import jwt as jose_jwt

from app.core.logging import get_logger
from app.settings import settings

log = get_logger(__name__)

# In-memory state store — used only when Redis is unavailable
_state_store: dict[str, bool] = {}

# Cached IdP configuration
_oidc_config_cache: dict | None = None


async def _get_oidc_config() -> dict:
    global _oidc_config_cache
    if _oidc_config_cache:
        return _oidc_config_cache
    url = f"{settings.sso_oidc_issuer.rstrip('/')}/.well-known/openid-configuration"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
    _oidc_config_cache = resp.json()
    return _oidc_config_cache


def _store_state(state: str) -> None:
    try:
        from app.services.cache_service import get_redis_client
        r = get_redis_client()
        if r:
            r.setex(f"oidc_state:{state}", 600, "1")
            return
    except Exception:  # noqa: S110
        log.debug("Redis unavailable for state store, using memory")
    _state_store[state] = True


def _validate_and_consume_state(state: str) -> bool:
    try:
        from app.services.cache_service import get_redis_client
        r = get_redis_client()
        if r:
            key = f"oidc_state:{state}"
            found = r.get(key)
            if found:
                r.delete(key)
                return True
            return False
    except Exception:  # noqa: S110
        log.debug("Redis unavailable for state validation, using memory")
    return _state_store.pop(state, False)


async def build_authorization_url() -> str:
    """Generates a state token, stores it, and returns the IdP redirect URL."""
    if not settings.sso_oidc_enabled:
        raise ValueError("SSO OIDC is not enabled")

    config = await _get_oidc_config()
    state = secrets.token_urlsafe(32)
    _store_state(state)

    params = {
        "response_type": "code",
        "client_id": settings.sso_oidc_client_id,
        "redirect_uri": settings.sso_oidc_redirect_uri,
        "scope": settings.sso_oidc_scopes,
        "state": state,
    }
    return f"{config['authorization_endpoint']}?{urlencode(params)}"


async def exchange_code(code: str, state: str) -> dict:
    """
    Validates state, exchanges authorization code for tokens, validates ID token.
    Returns user info dict with email (and optionally name).
    """
    if not _validate_and_consume_state(state):
        raise ValueError("oidc_invalid_state")

    config = await _get_oidc_config()

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            config["token_endpoint"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.sso_oidc_redirect_uri,
                "client_id": settings.sso_oidc_client_id,
                "client_secret": settings.sso_oidc_client_secret,
            },
            timeout=15,
        )
        if not resp.is_success:
            log.error("OIDC token exchange failed: HTTP %s", resp.status_code)
            raise ValueError("oidc_token_exchange_failed")
        token_data = resp.json()

    id_token = token_data.get("id_token")
    if not id_token:
        raise ValueError("oidc_no_id_token")

    # Fetch JWKS and validate ID token
    jwks_resp = await _fetch_jwks(config["jwks_uri"])
    claims = _validate_id_token(id_token, jwks_resp, config["issuer"])

    email = claims.get("email")
    if not email:
        raise ValueError("oidc_no_email_claim")

    return {
        "email": email,
        "first_name": claims.get("given_name", ""),
        "last_name": claims.get("family_name", ""),
        "sub": claims.get("sub", ""),
    }


async def _fetch_jwks(jwks_uri: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(jwks_uri, timeout=10)
        resp.raise_for_status()
    return resp.json()


def _validate_id_token(id_token: str, jwks: dict, expected_issuer: str) -> dict:
    try:
        claims = jose_jwt.decode(
            id_token,
            jwks,
            algorithms=["RS256", "ES256"],
            audience=settings.sso_oidc_client_id,
            issuer=expected_issuer,
        )
        return claims
    except JWTError as exc:
        log.warning("OIDC ID token validation failed: %s", exc)
        raise ValueError("oidc_invalid_token") from exc
