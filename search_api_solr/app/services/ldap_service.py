"""
LDAP authentication service.

Binds with a service account to search the user, then re-binds with the user's own
credentials to verify the password. Only LDAPS (port 636) or StartTLS are permitted.
"""

import ssl

from ldap3 import AUTO_BIND_NO_TLS, SUBTREE, Connection, Server, Tls
from ldap3.core.exceptions import LDAPException

from app.core.logging import get_logger
from app.settings import settings

log = get_logger(__name__)


def _make_server() -> Server:
    tls = Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLS_CLIENT)
    return Server(settings.ldap_url, use_ssl=True, tls=tls, get_info=None)


def _search_user(conn: Connection, username: str) -> dict | None:
    """Returns first matching entry as dict, or None."""
    search_filter = settings.ldap_user_filter.format(username=username)
    conn.search(
        search_base=settings.ldap_base_dn,
        search_filter=search_filter,
        search_scope=SUBTREE,
        attributes=[
            settings.ldap_email_attr,
            settings.ldap_firstname_attr,
            settings.ldap_lastname_attr,
        ],
    )
    if not conn.entries:
        return None
    entry = conn.entries[0]
    return {
        "dn": entry.entry_dn,
        "email": str(entry[settings.ldap_email_attr].value or ""),
        "first_name": str(entry[settings.ldap_firstname_attr].value or ""),
        "last_name": str(entry[settings.ldap_lastname_attr].value or ""),
    }


def authenticate(username: str, password: str) -> dict:
    """
    Authenticates a user against the LDAP directory.

    Returns a dict with email, first_name, last_name on success.
    Raises ValueError with a safe message on failure (no credential details leaked).
    """
    if not settings.ldap_enabled:
        raise ValueError("LDAP authentication is not enabled")

    server = _make_server()

    # Step 1 — bind with service account to search for the user DN
    try:
        service_conn = Connection(
            server,
            user=settings.ldap_bind_dn,
            password=settings.ldap_bind_password,
            auto_bind=AUTO_BIND_NO_TLS,
            raise_exceptions=True,
        )
    except LDAPException as e:
        log.error("LDAP service account bind failed")
        raise ValueError("ldap_unavailable") from e

    user_info = _search_user(service_conn, username)
    service_conn.unbind()

    if not user_info:
        raise ValueError("ldap_invalid_credentials")

    # Step 2 — re-bind as the user to verify the password
    try:
        user_conn = Connection(
            server,
            user=user_info["dn"],
            password=password,
            auto_bind=AUTO_BIND_NO_TLS,
            raise_exceptions=True,
        )
        user_conn.unbind()
    except LDAPException as e:
        raise ValueError("ldap_invalid_credentials") from e

    if not user_info["email"]:
        raise ValueError("ldap_no_email")

    return user_info
