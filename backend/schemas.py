"""
Pydantic schemas for request/response validation.
Separates input validation from ORM models for clean architecture.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# --- Request Schemas ---

class DocumentAuth(BaseModel):
    """Schema for creating or logging into a document."""
    passkey: str = Field(..., min_length=1, max_length=255, description="Passkey to protect and access the document")


class DocumentUpdate(BaseModel):
    """Schema for updating document content."""
    content: str = Field(default="", description="The document text content")


# --- Response Schemas ---

class DocumentResponse(BaseModel):
    """Schema returned after creating or retrieving a document."""
    id: int
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """Generic message response for simple operations."""
    message: str
