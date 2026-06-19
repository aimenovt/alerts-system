"""create users and events tables

Revision ID: 20260526_0001
Revises:
Create Date: 2026-05-26 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260526_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


event_status = postgresql.ENUM(
    "queued",
    "processing",
    "processed",
    "failed",
    name="eventstatus",
    create_type=False,
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    event_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", event_status, nullable=False, server_default="queued"),
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_event_type"), "events", ["event_type"], unique=False)
    op.create_index(op.f("ix_events_status"), "events", ["status"], unique=False)
    op.create_index(op.f("ix_events_owner_id"), "events", ["owner_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_events_owner_id"), table_name="events")
    op.drop_index(op.f("ix_events_status"), table_name="events")
    op.drop_index(op.f("ix_events_event_type"), table_name="events")
    op.drop_table("events")
    event_status.drop(op.get_bind(), checkfirst=True)

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
