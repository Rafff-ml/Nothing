"""
CRUD (Create, Read, Update, Delete) operations for the documents table.
All database interactions are encapsulated here for clean separation of concerns.
"""

from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timezone


def get_document_by_passkey(db: Session, passkey: str) -> models.Document | None:
    """Retrieve a document by its unique passkey. Returns None if not found."""
    return db.query(models.Document).filter(
        models.Document.passkey == passkey
    ).first()


def create_document(db: Session, doc: schemas.DocumentAuth) -> models.Document:
    """
    Create a new document with the given passkey.
    Content starts empty. Timestamps are set automatically by the database.
    """
    db_document = models.Document(
        passkey=doc.passkey,
        content="",
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def update_document_content(db: Session, passkey: str, content: str) -> models.Document | None:
    """
    Update the text content of an existing document.
    Also updates the 'updated_at' timestamp.
    """
    document = get_document_by_passkey(db, passkey)
    if document:
        document.content = content
        document.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(document)
    return document
