import os

from sqlalchemy import create_engine

engine = create_engine(os.getenv('DB_URL'), echo=True)

__all__ = [
    "engine"
]