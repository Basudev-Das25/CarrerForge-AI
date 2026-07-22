"""Document processor — extracts text, performs OCR, generates metadata and embeddings."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from app.config.settings import settings
from app.services.embeddings import store_embedding

logger = logging.getLogger("careerforge.docproc")


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        text_parts = []

        for page in doc:
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(page_text)
            else:
                # Fallback to OCR for image-only pages
                logger.info("docproc.ocr.page", page=page.number + 1)
                ocr_text = _ocr_page(page)
                if ocr_text:
                    text_parts.append(ocr_text)

        doc.close()
        return "\n\n".join(text_parts)

    except ImportError:
        logger.error("docproc.pymupdf.missing")
        raise RuntimeError("PyMuPDF is required for PDF processing. Install with: pip install pymupdf")


def _ocr_page(page) -> str:
    """Perform OCR on a single PDF page using Tesseract."""
    try:
        import pytesseract
        from PIL import Image
        import io

        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(img)
    except ImportError:
        logger.warning("docproc.tesseract.missing")
        return ""


def compute_file_hash(file_path: str) -> str:
    """Compute SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def categorize_document(text: str, filename: str) -> str:
    """Heuristic document categorization based on content and filename."""
    lower_name = filename.lower()
    lower_text = text.lower()[:2000]  # First 2000 chars

    if any(kw in lower_name for kw in ["resume", "cv", "curriculum"]):
        return "resume"
    if any(kw in lower_name for kw in ["certificate", "cert", "diploma"]):
        return "certificate"
    if any(kw in lower_name for kw in ["reference", "recommendation", "ref"]):
        return "reference"

    # Content-based heuristics
    if any(kw in lower_text for kw in ["experience", "employment", "work history"]):
        return "resume"
    if any(kw in lower_text for kw in ["certify", "certification", "this is to certify"]):
        return "certificate"
    if any(kw in lower_text for kw in ["recommend", "reference letter"]):
        return "reference"

    return "other"


def process_document(file_path: str, user_id: str) -> dict:
    """Full document processing pipeline.

    1. Extract text (PDF → text, with OCR fallback)
    2. Compute file hash for deduplication
    3. Categorize the document
    4. Generate embeddings for semantic chunks
    5. Return processed metadata

    Returns dict with: text, hash, category, embedding_ids
    """
    path = Path(file_path)
    logger.info("docproc.start", file=str(path))

    # Step 1: Extract text
    if path.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(str(path))
    elif path.suffix.lower() in (".txt", ".md"):
        text = path.read_text(encoding="utf-8")
    else:
        text = ""

    # Step 2: File hash
    file_hash = compute_file_hash(str(path))

    # Step 3: Categorize
    category = categorize_document(text, path.name)

    # Step 4: Chunk and embed
    embedding_ids = []
    if text.strip():
        chunks = _chunk_text(text)
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) > 20:  # Skip tiny chunks
                eid = store_embedding(
                    entity_type="document",
                    entity_id=file_hash,
                    text=chunk,
                    tags=f"{category},{path.name}",
                )
                embedding_ids.append(eid)

    logger.info(
        "docproc.complete",
        file=str(path),
        category=category,
        chunks=len(embedding_ids),
    )

    return {
        "text": text,
        "hash": file_hash,
        "category": category,
        "embedding_ids": embedding_ids,
        "char_count": len(text),
        "chunk_count": len(embedding_ids),
    }


def _chunk_text(text: str, max_chars: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks for embedding."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start + overlap >= len(text):
            break
    return chunks
