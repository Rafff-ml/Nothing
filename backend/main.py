"""
OffPad - FastAPI Backend
Main application entry point. Defines all API routes and serves the frontend.
Run with: uvicorn backend.main:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from .database import engine, get_db, Base
from . import crud, schemas, models

# ---------------------------------------------------------------------------
# Create all database tables on startup (SQLite file is auto-created)
# ---------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="OffPad",
    description="Offline-first note-taking API with passkey protection",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS – allow the frontend (served from any origin during development)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Serve the frontend static files
# ---------------------------------------------------------------------------
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ---------------------------------------------------------------------------
# Frontend page routes
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def serve_home():
    """Serve the home / login page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/editor", include_in_schema=False)
async def serve_editor():
    """Serve the editor page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "editor.html"))


# ===================================================================
#  API ENDPOINTS
# ===================================================================

@app.post(
    "/documents/create",
    response_model=schemas.DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document",
)
def create_document(doc: schemas.DocumentAuth, db: Session = Depends(get_db)):
    """
    Create a new document with a unique passkey.
    Returns 409 if a document with the same passkey already exists.
    """
    existing = crud.get_document_by_passkey(db, doc.passkey)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A document with this passkey already exists.",
        )
    return crud.create_document(db, doc)


@app.post(
    "/documents/login",
    response_model=schemas.DocumentResponse,
    summary="Login to an existing document",
)
def login_document(creds: schemas.DocumentAuth, db: Session = Depends(get_db)):
    """
    Verify passkey and return the document if valid.
    Returns 401 if the passkey does not exist.
    """
    document = crud.get_document_by_passkey(db, creds.passkey)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid passkey.",
        )
    return document


@app.get(
    "/documents/{passkey}",
    response_model=schemas.DocumentResponse,
    summary="Get a document by passkey",
)
def get_document(passkey: str, db: Session = Depends(get_db)):
    """
    Retrieve a document's content.
    """
    document = crud.get_document_by_passkey(db, passkey)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid passkey.",
        )
    return document


@app.put(
    "/documents/{passkey}",
    response_model=schemas.DocumentResponse,
    summary="Update document content",
)
def update_document(
    passkey: str,
    payload: schemas.DocumentUpdate,
    db: Session = Depends(get_db),
):
    """
    Update the content of an existing document.
    """
    document = crud.get_document_by_passkey(db, passkey)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid passkey.",
        )
    updated = crud.update_document_content(db, passkey, payload.content)
    return updated
