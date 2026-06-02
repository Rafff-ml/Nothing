"""
CRUD (Create, Read, Update, Delete) operations for the documents table.
All database interactions are encapsulated here for clean separation of concerns.
"""

from sqlalchemy.orm import Session
from . import models, schemas
from .config import settings
from datetime import datetime, timezone
import hashlib

def hash_passkey(passkey: str) -> str:
    """Return a PBKDF2-HMAC-SHA256 hash of the passkey using the secret pepper as salt."""
    return hashlib.pbkdf2_hmac(
        'sha256',
        passkey.encode("utf-8"),
        settings.SECRET_PEPPER.encode("utf-8"),
        600000
    ).hex()


def get_document_by_passkey(db: Session, passkey: str) -> models.Document | None:
    """Retrieve a document by its unique passkey. Returns None if not found."""
    hashed = hash_passkey(passkey)
    return db.query(models.Document).filter(
        models.Document.passkey == hashed
    ).first()


def create_document(db: Session, doc: schemas.DocumentAuth) -> models.Document:
    """
    Create a new document with the given passkey.
    Content starts empty. Timestamps are set automatically by the database.
    """
    db_document = models.Document(
        passkey=hash_passkey(doc.passkey),
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

