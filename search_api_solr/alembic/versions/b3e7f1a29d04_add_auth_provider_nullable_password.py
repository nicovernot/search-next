"""Add auth_provider, make hashed_password nullable

Revision ID: b3e7f1a29d04
Revises: 52562d213c85
Create Date: 2026-04-19 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = 'b3e7f1a29d04'
down_revision: str | Sequence[str] | None = '52562d213c85'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # hashed_password becomes nullable for federated users (LDAP/SSO)
    op.alter_column('user', 'hashed_password', existing_type=sa.String(), nullable=True)

    # auth_provider identifies the authentication source
    op.add_column('user', sa.Column('auth_provider', sa.String(), nullable=True))
    op.execute("UPDATE \"user\" SET auth_provider = 'local' WHERE auth_provider IS NULL")
    op.alter_column('user', 'auth_provider', existing_type=sa.String(), nullable=False)


def downgrade() -> None:
    op.drop_column('user', 'auth_provider')

    # Restore NOT NULL constraint — rows with null password must be handled manually before downgrading
    op.alter_column('user', 'hashed_password', existing_type=sa.String(), nullable=False)
