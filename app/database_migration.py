from sqlalchemy import text

from app.database import engine


def migrate_schema():
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(employee_skills)"))
        columns = [row[1] for row in result]
        if "skill_id" not in columns:
            conn.execute(text("ALTER TABLE employee_skills ADD COLUMN skill_id INTEGER"))
            conn.commit()
