"""align agent runtime persistence with refactored runtime

Revision ID: 20260518_0003
Revises: 20260516_0002
Create Date: 2026-05-18
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260518_0003"
down_revision = "20260516_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("conversation_messages") as batch_op:
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            )
        )

    op.create_index(
        "ix_conversation_messages_session_created",
        "conversation_messages",
        ["session_id", "created_at"],
    )
    op.create_index(
        "ix_conversation_messages_user_session",
        "conversation_messages",
        ["user_tag", "session_id"],
    )
    op.create_index(
        "ix_agent_memories_user_created",
        "agent_memories",
        ["user_tag", "created_at"],
    )
    op.create_index(
        "ix_agent_memories_subject",
        "agent_memories",
        ["subject"],
    )
    op.create_index(
        "ix_agent_memories_active_expires",
        "agent_memories",
        ["is_active", "expires_at"],
    )
    op.create_index(
        "ix_memory_reminders_memory_id",
        "memory_reminders",
        ["memory_id"],
    )
    op.create_index(
        "ix_memory_reminders_trigger_status",
        "memory_reminders",
        ["trigger_at", "triggered"],
    )


def downgrade() -> None:
    op.drop_index("ix_memory_reminders_trigger_status", table_name="memory_reminders")
    op.drop_index("ix_memory_reminders_memory_id", table_name="memory_reminders")
    op.drop_index("ix_agent_memories_active_expires", table_name="agent_memories")
    op.drop_index("ix_agent_memories_subject", table_name="agent_memories")
    op.drop_index("ix_agent_memories_user_created", table_name="agent_memories")
    op.drop_index("ix_conversation_messages_user_session", table_name="conversation_messages")
    op.drop_index("ix_conversation_messages_session_created", table_name="conversation_messages")

    with op.batch_alter_table("conversation_messages") as batch_op:
        batch_op.drop_column("updated_at")
