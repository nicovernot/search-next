from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class User(Base):
    """
    Modèle SQLAlchemy pour l'utilisateur.
    """
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Optionnel: Prénom, Nom, Organisation, etc.
    # first_name = Column(String)
    # last_name = Column(String)
