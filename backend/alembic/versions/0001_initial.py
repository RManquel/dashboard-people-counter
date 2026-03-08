"""Initial migration: create events and occupancy_stats tables

Revision ID: 0001
Revises:
Create Date: 2024-03-10 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("device_id", sa.String(64), nullable=False, index=True),
        sa.Column("direction", sa.String(8), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "occupancy_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("people_inside", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("entries_today", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("exits_today", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Seed the single-row stats record
    op.execute("INSERT INTO occupancy_stats (id, people_inside, entries_today, exits_today) VALUES (1, 0, 0, 0)")


def downgrade() -> None:
    op.drop_table("occupancy_stats")
    op.drop_table("events")
