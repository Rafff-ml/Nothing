"""
SQLAlchemy ORM models for the OffPad application.
Defines the 'documents' table with all required fields.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base


class Document(Base):
    """
    Represents a single document/note in the system.
    Each document is uniquely identified and protected by a passkey.
    Text content is auto-saved.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    passkey = Column(String(255), unique=True, nullable=False, index=True)
    content = Column(Text, default="", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
