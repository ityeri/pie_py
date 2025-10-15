import os

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

_engine: Engine = None
Base = declarative_base()
_Session: sessionmaker[Session]= None

def db_setup():
    global _engine, _Session
    _engine = create_engine(os.getenv('DB_URL'), echo=True)
    _Session = sessionmaker(bind=_engine, autoflush=False)

def get_engine() -> Engine:
    if _engine is None:
        RuntimeError("Engine is not been initialized")
    return _engine

def get_session_instance() -> Session:
    return _Session()


__all__ = [
    'get_engine',
    'get_session_instance',
    'Base',
    'db_setup',
]