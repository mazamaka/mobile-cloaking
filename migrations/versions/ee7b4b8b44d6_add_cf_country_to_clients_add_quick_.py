"""add cf_country to clients, add quick fields to init_logs

Revision ID: ee7b4b8b44d6
Revises: 69856230db0b
Create Date: 2026-03-16 15:27:22.426052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'ee7b4b8b44d6'
down_revision: Union[str, None] = '69856230db0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # clients: add cf_country
    op.add_column('clients', sa.Column('cf_country', sa.String(length=10), nullable=True))
    op.create_index(op.f('ix_clients_cf_country'), 'clients', ['cf_country'], unique=False)

    # init_logs: add quick-filter fields
    op.add_column('init_logs', sa.Column('ip', sa.String(length=45), nullable=True))
    op.add_column('init_logs', sa.Column('cf_country', sa.String(length=10), nullable=True))
    op.add_column('init_logs', sa.Column('bundle_id', sa.String(length=255), nullable=True))
    op.add_column('init_logs', sa.Column('result_mode', sa.String(length=10), nullable=True))
    op.create_index(op.f('ix_init_logs_cf_country'), 'init_logs', ['cf_country'], unique=False)
    op.create_index(op.f('ix_init_logs_bundle_id'), 'init_logs', ['bundle_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_init_logs_bundle_id'), table_name='init_logs')
    op.drop_index(op.f('ix_init_logs_cf_country'), table_name='init_logs')
    op.drop_column('init_logs', 'result_mode')
    op.drop_column('init_logs', 'bundle_id')
    op.drop_column('init_logs', 'cf_country')
    op.drop_column('init_logs', 'ip')
    op.drop_index(op.f('ix_clients_cf_country'), table_name='clients')
    op.drop_column('clients', 'cf_country')
