"""
OffPad - FastAPI Backend
Main application entry point. Defines all API routes and serves the frontend.
Run with: uvicorn backend.main:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

from .database import engine, get_db, Base
from . import crud, schemas, models
from .config import settings

# ---------------------------------------------------------------------------
# Create all database tables on startup (SQLite file is auto-created)
# ---------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)

# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="OffPad",
    description="Offline-first note-taking API with passkey protection",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# CORS – allow the frontend (served from any origin during development)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
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
@limiter.limit("5/minute")
def create_document(request: Request, doc: schemas.DocumentAuth, db: Session = Depends(get_db)):
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
@limiter.limit("5/minute")
def login_document(request: Request, creds: schemas.DocumentAuth, db: Session = Depends(get_db)):
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
    "/documents",
    response_model=schemas.DocumentResponse,
    summary="Get a document by passkey from header",
)
@limiter.limit("60/minute")
def get_document(request: Request, x_passkey: str = Header(...), db: Session = Depends(get_db)):
    """
    Retrieve a document's content.
    """
    document = crud.get_document_by_passkey(db, x_passkey)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid passkey.",
        )
    return document


@app.put(
    "/documents",
    response_model=schemas.DocumentResponse,
    summary="Update document content",
)
@limiter.limit("120/minute")
def update_document(
    request: Request,
    payload: schemas.DocumentUpdate,
    x_passkey: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Update the content of an existing document.
    """
    document = crud.get_document_by_passkey(db, x_passkey)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid passkey.",
        )
    updated = crud.update_document_content(db, x_passkey, payload.content)
    return updated
