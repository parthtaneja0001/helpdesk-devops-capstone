"""create tickets table

Revision ID: 0001
Revises:
Create Date: 2026-10-16 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

status = sa.Enum("open", "in_progress", "resolved", "closed", name="ticket_status")
priority = sa.Enum("low", "medium", "high", "urgent", name="ticket_priority")


def upgrade() -> None:
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("requester", sa.String(120), nullable=False),
        sa.Column("assignee", sa.String(120), nullable=True),
        sa.Column("status", status, nullable=False, server_default="open"),
        sa.Column("priority", priority, nullable=False, server_default="medium"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_tickets_id", "tickets", ["id"])
    op.create_index("ix_tickets_status", "tickets", ["status"])


def downgrade() -> None:
    op.drop_index("ix_tickets_status", table_name="tickets")
    op.drop_index("ix_tickets_id", table_name="tickets")
    op.drop_table("tickets")
    priority.drop(op.get_bind(), checkfirst=True)
    status.drop(op.get_bind(), checkfirst=True)
