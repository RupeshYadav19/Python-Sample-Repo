"""
database/database.py

Sets up the SQLAlchemy engine and session for SQLite.
The database file (users.db) is created automatically when the app starts.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings


# Create the SQLAlchemy engine.
# connect_args={"check_same_thread": False} is required for SQLite
# because FastAPI may use the same connection across multiple threads.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# SessionLocal is a factory for creating new database sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class that all SQLAlchemy models will inherit from."""
    pass


def create_tables() -> None:
    """Create all database tables if they don't already exist."""
    # Import models here so SQLAlchemy knows about them before creating tables.
    from app.database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
