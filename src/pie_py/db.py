import os

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine

engine: Engine = None

def setup():
    global engine
    engine = create_engine(os.getenv('DB_URL'), echo=True)

__all__ = [
    "setup",
    "engine"
]