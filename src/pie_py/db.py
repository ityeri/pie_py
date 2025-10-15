import os

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import declarative_base

engine: Engine = None
Base = declarative_base()

def setup():
    global engine
    engine = create_engine(os.getenv('DB_URL'), echo=True)

__all__ = [
    "setup",
    "engine",
    "Base"
]