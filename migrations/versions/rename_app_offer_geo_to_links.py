"""Rename app_offer_geo table to links

Revision ID: rename_aog_links
Revises: 251443eb8f5e
Create Date: 2024-12-27

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'rename_aog_links'
down_revision: Union[str, None] = '251443eb8f5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename table
    op.rename_table('app_offer_geo', 'links')

    # Rename unique constraint
    op.execute('ALTER TABLE links RENAME CONSTRAINT uq_app_offer_geo_app_geo TO uq_link_app_geo')

    # Rename indexes (if any exist with old naming)
    # Note: SQLAlchemy auto-generates index names, so we rename them too
    op.execute('ALTER INDEX IF EXISTS ix_app_offer_geo_app_id RENAME TO ix_links_app_id')
    op.execute('ALTER INDEX IF EXISTS ix_app_offer_geo_offer_id RENAME TO ix_links_offer_id')
    op.execute('ALTER INDEX IF EXISTS ix_app_offer_geo_geo_id RENAME TO ix_links_geo_id')
    op.execute('ALTER INDEX IF EXISTS ix_app_offer_geo_is_active RENAME TO ix_links_is_active')


def downgrade() -> None:
    # Rename indexes back
    op.execute('ALTER INDEX IF EXISTS ix_links_is_active RENAME TO ix_app_offer_geo_is_active')
    op.execute('ALTER INDEX IF EXISTS ix_links_geo_id RENAME TO ix_app_offer_geo_geo_id')
    op.execute('ALTER INDEX IF EXISTS ix_links_offer_id RENAME TO ix_app_offer_geo_offer_id')
    op.execute('ALTER INDEX IF EXISTS ix_links_app_id RENAME TO ix_app_offer_geo_app_id')

    # Rename unique constraint back
    op.execute('ALTER TABLE links RENAME CONSTRAINT uq_link_app_geo TO uq_app_offer_geo_app_geo')

    # Rename table back
    op.rename_table('links', 'app_offer_geo')
