"""add users.personal_data_consent_at

Revision ID: a7c1d2e3f4b5
Revises: 1b3d9c6b4324
Create Date: 2026-10-04 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'a7c1d2e3f4b5'
down_revision: Union[str, None] = '1b3d9c6b4324'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('personal_data_consent_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('users', 'personal_data_consent_at')
