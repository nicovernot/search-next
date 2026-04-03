from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.settings import settings

# Contexte pour le hachage des mots de passe (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    Génère un token JWT pour un sujet (généralement l'ID ou l'email de l'utilisateur).
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe en clair correspond à sa version hachée.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Génère un hash sécurisé pour un mot de passe.
    """
    return pwd_context.hash(password)
