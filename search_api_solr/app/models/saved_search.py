from sqlalchemy import Column, ForeignKey, Integer, String, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class SavedSearch(Base):
    """
    Modèle SQLAlchemy pour une recherche sauvegardée par un utilisateur.
    """
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    
    # query_json stocke l'état complet de la recherche (termes, filtres, etc.)
    query_json = Column(JSON, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relation avec le modèle User
    user = relationship("User", backref="saved_searches")
