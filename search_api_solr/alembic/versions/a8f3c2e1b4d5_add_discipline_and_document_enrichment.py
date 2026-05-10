"""add discipline and document_enrichment tables

Revision ID: a8f3c2e1b4d5
Revises: b3e7f1a29d04
Create Date: 2026-05-10

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY

revision: str = "a8f3c2e1b4d5"
down_revision: Union[str, Sequence[str], None] = "b3e7f1a29d04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_EMBEDDING_DIM = 768  # multilingual-e5-large


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "discipline",
        sa.Column("code", sa.String(), primary_key=True, nullable=False),
        sa.Column("label_fr", sa.String(), nullable=False),
        sa.Column("label_en", sa.String(), nullable=False),
        sa.Column(
            "parent_code",
            sa.String(),
            sa.ForeignKey("discipline.code"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("code"),
    )

    op.create_table(
        "document_enrichment",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("doc_id", sa.String(), nullable=False),
        sa.Column("model_version", sa.String(), nullable=False),
        sa.Column(
            "disciplines",
            ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("discipline_source", sa.String(), nullable=True),
        sa.Column("discipline_confidence", sa.Float(), nullable=True),
        sa.Column("text_input", sa.Text(), nullable=True),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("doc_id", "model_version", name="uq_doc_model"),
    )
    op.create_index("ix_document_enrichment_id", "document_enrichment", ["id"])
    op.create_index(
        "ix_document_enrichment_doc_id", "document_enrichment", ["doc_id"]
    )

    # vector column requires pgvector extension — added via raw SQL after table creation
    op.execute(
        f"ALTER TABLE document_enrichment ADD COLUMN embedding vector({_EMBEDDING_DIM})"
    )
    # IVFFlat ANN index — lists = 100 calibrated for ~10k docs; revisit at scale (lists ≈ sqrt(n_docs))
    op.execute(
        "CREATE INDEX ix_document_enrichment_embedding_ivfflat "
        "ON document_enrichment USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    op.execute(
        "DROP INDEX IF EXISTS ix_document_enrichment_embedding_ivfflat"
    )
    op.drop_index("ix_document_enrichment_doc_id", table_name="document_enrichment")
    op.drop_index("ix_document_enrichment_id", table_name="document_enrichment")
    op.drop_table("document_enrichment")
    op.drop_table("discipline")
