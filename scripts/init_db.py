"""Initialize the application database schema from the current ORM models."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.schema import initialize_database


def main() -> None:
    initialize_database()
    print("Database schema initialized from ORM models.")


if __name__ == "__main__":
    main()
