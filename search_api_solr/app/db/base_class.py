from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    Classe de base déclarative pour tous les modèles SQLAlchemy.
    Permet de générer automatiquement le nom de la table à partir du nom du modèle.
    """
    id: Any
    __name__: str

    # Génère __tablename__ automatiquement à partir du nom de la classe (en minuscules)
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
