"""Initial migration - create all tables

Revision ID: 001_initial
Revises:
Create Date: 2024-12-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create apps table
    op.create_table(
        "apps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bundle_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("mode", sa.VARCHAR(length=10), nullable=False, server_default="native"),
        sa.Column("casino_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("rate_delay_sec", sa.Integer(), nullable=False, server_default="180"),
        sa.Column("push_delay_sec", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("min_version", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("latest_version", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("update_mode", sa.VARCHAR(length=10), nullable=True),
        sa.Column("appstore_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_apps_bundle_id", "apps", ["bundle_id"], unique=True)

    # Create clients table
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("internal_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("app_id", sa.Integer(), nullable=False),
        sa.Column("app_version", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("language", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("timezone", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("region", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("att_status", sa.VARCHAR(length=20), nullable=False),
        sa.Column("idfa", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("appsflyer_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("push_token", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("sessions_count", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["app_id"], ["apps.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_clients_internal_id", "clients", ["internal_id"], unique=True)
    op.create_index("ix_clients_app_id", "clients", ["app_id"], unique=False)

    # Create events table
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("app_id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("event_ts", sa.DateTime(), nullable=False),
        sa.Column("props", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("app_version", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("received_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["app_id"], ["apps.id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_events_client_id", "events", ["client_id"], unique=False)
    op.create_index("ix_events_app_id", "events", ["app_id"], unique=False)
    op.create_index("ix_events_name", "events", ["name"], unique=False)

    # Create init_logs table
    op.create_table(
        "init_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("request_headers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("request_body", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("response_code", sa.Integer(), nullable=False),
        sa.Column("response_body", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_init_logs_client_id", "init_logs", ["client_id"], unique=False)


def downgrade() -> None:
    op.drop_table("init_logs")
    op.drop_table("events")
    op.drop_table("clients")
    op.drop_table("apps")
