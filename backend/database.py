"""
Database configuration module.
Creates the SQLite engine, session factory, and base class for ORM models.
The database file (offpad.db) is created automatically in the project root.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Check for DATABASE_URL environment variable (used by Render and other cloud providers)
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL is provided, fallback to local SQLite
if not DATABASE_URL:
    DATABASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'offpad.db')}"

# SQLAlchemy 1.4+ requires 'postgresql://' instead of 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite requires specific connect_args, Postgres does not
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session per request.
    Ensures the session is closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
