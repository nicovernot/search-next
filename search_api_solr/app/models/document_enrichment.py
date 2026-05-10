from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func

from app.db.base_class import Base

EMBEDDING_DIM = 768  # multilingual-e5-large


class Discipline(Base):
    __tablename__ = "discipline"

    code = Column(String, primary_key=True)
    label_fr = Column(String, nullable=False)
    label_en = Column(String, nullable=False)
    parent_code = Column(String, ForeignKey("discipline.code"), nullable=True)


class DocumentEnrichment(Base):
    __tablename__ = "document_enrichment"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, nullable=False, index=True)
    model_version = Column(String, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)
    disciplines = Column(ARRAY(String), nullable=False, server_default="{}")
    discipline_source = Column(String, nullable=True)
    discipline_confidence = Column(Float, nullable=True)
    text_input = Column(String, nullable=True)
    computed_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("doc_id", "model_version", name="uq_doc_model"),
    )
