from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings

# Création du moteur SQLAlchemy
# En mode développement, on peut ajouter echo=True pour voir les requêtes SQL
engine = create_engine(
    settings.database_url,
    # Indispensable pour SQLite mais pas pour Postgres, on le laisse pour la flexibilité
    # connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# SessionLocal est une classe de fabrique pour les sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency pour injecter la session de base de données dans les endpoints FastAPI.
    Assure que la session est fermée après chaque requête.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
