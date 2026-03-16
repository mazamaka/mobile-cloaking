"""add geo_source to apps

Revision ID: 74e4a7af2157
Revises: 424fc4ccf9cd
Create Date: 2026-03-16 15:50:23.221154

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '74e4a7af2157'
down_revision: Union[str, None] = '424fc4ccf9cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('apps', sa.Column('geo_source', sa.String(length=15), nullable=False, server_default='cloudflare'))


def downgrade() -> None:
    op.drop_column('apps', 'geo_source')
