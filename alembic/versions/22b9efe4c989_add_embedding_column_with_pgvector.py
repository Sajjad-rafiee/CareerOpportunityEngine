"""add embedding column with pgvector

Revision ID: 22b9efe4c989
Revises: 05fbe36f01df
Create Date: 2026-09-21 13:13:59.415321

"""
from typing import Sequence, Union

import pgvector.sqlalchemy
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '22b9efe4c989'
down_revision: Union[str, Sequence[str], None] = '05fbe36f01df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # روی یک دیتابیس تازه (مثلاً CI یا کلون جدید)، extension باید صریحاً
    # فعال بشه قبل از این‌که بشه از نوع vector استفاده کرد.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column(
        'opportunities',
        sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=384), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('opportunities', 'embedding')
