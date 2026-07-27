"""Document vault router — upload, list, search, delete, process.

Supports drag-and-drop, multi-file upload, OCR status tracking,
semantic search, and metadata management.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.db.base import get_db
from app.db.models import OriginalDocument
from app.db.repository import Repository
from app.models.schemas import DocumentResponse
from app.services.document_processor import process_document

router = APIRouter()

DEFAULT_USER_ID = "default"


def _get_doc_repo(session: AsyncSession) -> Repository:
    return Repository(OriginalDocument, session)


def _get_upload_dir() -> Path:
    upload_dir = Path(settings.data_dir).expanduser() / "documents"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


# ══════════════════════════════════════════════════════════════
# UPLOAD
# ══════════════════════════════════════════════════════════════

@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Upload a single document. Automatically extracts text, categorizes, and embeds."""
    upload_dir = _get_upload_dir()
    doc_id = str(uuid.uuid4())

    # Validate file type
    allowed = settings.documents_allowed_types if hasattr(settings, "documents_allowed_types") else [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"]
    suffix = Path(file.filename or "unknown").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(status_code=400, detail=f"File type '{suffix}' not allowed. Allowed: {allowed}")

    # Save file
    safe_name = f"{doc_id}{suffix}"
    file_path = upload_dir / safe_name

    with open(file_path, "wb") as f:
        content = await file.read()
        if len(content) > 52428800:  # 50MB limit
            raise HTTPException(status_code=413, detail="File too large (max 50MB)")
        f.write(content)

    # Process document (text extraction, categorization, embedding)
    try:
        result = process_document(str(file_path), DEFAULT_USER_ID)
    except Exception:
        # Still save the doc even if processing fails
        result = {"text": "", "hash": "", "category": category or "other", "embedding_ids": []}

    # Determine category
    doc_category = category or result.get("category", "other")

    # Store in database
    repo = _get_doc_repo(db)
    doc = await repo.create({
        "id": doc_id,
        "file_path": str(file_path),
        "original_name": file.filename or "unknown",
        "mime_type": file.content_type,
        "file_size": len(content),
        "text_content": result.get("text", "")[:10000],  # Truncate for DB
        "category": doc_category,
        "embedding_ids": result.get("embedding_ids", []),
        "ocr_performed": False,
    })

    return doc


@router.post("/upload/multiple", status_code=201)
async def upload_multiple(
    files: list[UploadFile] = File(...),
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Upload multiple documents at once."""
    results = []
    errors = []

    for file in files:
        try:
            # Reuse single upload logic
            upload_dir = _get_upload_dir()
            doc_id = str(uuid.uuid4())
            suffix = Path(file.filename or "unknown").suffix.lower()
            safe_name = f"{doc_id}{suffix}"
            file_path = upload_dir / safe_name

            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            try:
                result = process_document(str(file_path), DEFAULT_USER_ID)
            except Exception:
                result = {"text": "", "hash": "", "category": "other", "embedding_ids": []}

            repo = _get_doc_repo(db)
            await repo.create({
                "id": doc_id,
                "file_path": str(file_path),
                "original_name": file.filename or "unknown",
                "mime_type": file.content_type,
                "file_size": len(content),
                "text_content": result.get("text", "")[:10000],
                "category": category or result.get("category", "other"),
                "embedding_ids": result.get("embedding_ids", []),
                "ocr_performed": False,
            })
            results.append({"id": doc_id, "name": file.filename, "status": "ok"})
        except Exception as e:
            errors.append({"name": file.filename, "error": str(e)})

    return {"uploaded": len(results), "errors": len(errors), "results": results, "errors_detail": errors}


# ══════════════════════════════════════════════════════════════
# LIST / GET / DELETE
# ══════════════════════════════════════════════════════════════

@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    category: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List documents with optional category filter."""
    repo = _get_doc_repo(db)
    filters = {"category": category} if category else None
    return await repo.list(filters=filters, limit=limit, offset=offset)


@router.get("/count")
async def count_documents(db: AsyncSession = Depends(get_db)):
    repo = _get_doc_repo(db)
    total = await repo.count()
    return {"total": total}


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    repo = _get_doc_repo(db)
    doc = await repo.get(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}", status_code=204)
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    repo = _get_doc_repo(db)
    doc = await repo.get(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete physical file
    file_path = Path(doc.file_path)
    if file_path.exists():
        file_path.unlink()

    await repo.delete(doc_id)


# ══════════════════════════════════════════════════════════════
# SEARCH
# ══════════════════════════════════════════════════════════════

@router.post("/search")
async def search_documents(
    query: str = Query(..., min_length=1),
    top_k: int = Query(default=5, le=20),
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Semantic search across documents using LanceDB embeddings."""
    from app.services.embeddings import find_similar

    results = find_similar(query, entity_type="document", top_k=top_k, threshold=0.3)

    # Enrich with document metadata
    repo = _get_doc_repo(db)
    enriched = []
    for r in results:
        doc = await repo.get(r["entity_id"])
        if doc:
            enriched.append({
                "document": {
                    "id": doc.id,
                    "name": doc.original_name,
                    "category": doc.category,
                },
                "similarity": r["similarity"],
                "text_preview": r["text"][:200],
            })

    return {"results": enriched, "query": query, "total": len(enriched)}
