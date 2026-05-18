"""Database schema initialization utilities."""

from app.agent.models import *  # noqa: F403 - register agent runtime ORM tables
from app.database import Base, engine
from app.models import *  # noqa: F403 - register business ORM tables


def initialize_database() -> None:
    """Create all registered ORM tables when they do not exist."""

    Base.metadata.create_all(bind=engine)


__all__ = ["initialize_database"]
