from sqlalchemy import text

from app.database import engine


def migrate_schema():
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(employee_skills)"))
        columns = [row[1] for row in result]
        if "skill_id" not in columns:
            conn.execute(text("ALTER TABLE employee_skills ADD COLUMN skill_id INTEGER"))
            conn.commit()

        result = conn.execute(text("PRAGMA table_info(conversation_messages)"))
        columns = [row[1] for row in result]
        if columns and "user_tag" not in columns:
            conn.execute(text("ALTER TABLE conversation_messages ADD COLUMN user_tag VARCHAR(100) NOT NULL DEFAULT 'default'"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_conversation_messages_user_tag ON conversation_messages (user_tag)"))
            conn.commit()
