"""add geo_id FK to clients

Revision ID: 424fc4ccf9cd
Revises: ee7b4b8b44d6
Create Date: 2026-03-16 15:42:19.815859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '424fc4ccf9cd'
down_revision: Union[str, None] = 'ee7b4b8b44d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('clients', sa.Column('geo_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_clients_geo_id'), 'clients', ['geo_id'], unique=False)
    op.create_foreign_key('fk_clients_geo_id', 'clients', 'geos', ['geo_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_clients_geo_id', 'clients', type_='foreignkey')
    op.drop_index(op.f('ix_clients_geo_id'), table_name='clients')
    op.drop_column('clients', 'geo_id')
