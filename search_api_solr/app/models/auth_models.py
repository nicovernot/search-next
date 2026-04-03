from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    """Schéma pour la création d'un utilisateur"""
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    """Schéma pour la connexion"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schéma pour le token JWT retourné"""
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    """Schéma pour la réponse utilisateur (sans mot de passe)"""
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True
