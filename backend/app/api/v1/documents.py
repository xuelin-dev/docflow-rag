"""Document management endpoints."""

from uuid import UUID

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, DbSession

router = APIRouter()


class DocumentResponse(BaseModel):
    """Document metadata response."""
    id: UUID
    namespace_id: UUID
    title: str
    doc_type: str
    source_url: str | None = None
    file_size_bytes: int | None = None
    status: str = "pending"
    chunk_count: int = 0
    metadata: dict = {}


class DocumentListResponse(BaseModel):
    """Paginated document list."""
    documents: list[DocumentResponse]
    total: int
    page: int = 1
    page_size: int = 20


class DocumentUpdateRequest(BaseModel):
    """Document metadata update."""
    title: str | None = None
    metadata: dict | None = None


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    db: DbSession,
    user: CurrentUser,
    file: UploadFile = File(...),
    namespace: str = Form(default="default"),
    title: str | None = Form(default=None),
) -> DocumentResponse:
    """Upload a document for parsing, chunking, and indexing.

    Accepts PDF, Markdown, HTML, and TXT files. The document is queued
    for async processing via the ingestion pipeline.
    """
    # TODO: Save file, create DB record, enqueue for processing
    return DocumentResponse(
        id=UUID("00000000-0000-0000-0000-000000000000"),
        namespace_id=UUID("00000000-0000-0000-0000-000000000000"),
        title=title or (file.filename or "Untitled"),
        doc_type="pdf",
        status="pending",
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    db: DbSession,
    user: CurrentUser,
    namespace: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> DocumentListResponse:
    """List documents with optional namespace and status filters."""
    # TODO: Query from database
    return DocumentListResponse(documents=[], total=0, page=page, page_size=page_size)


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: UUID, db: DbSession, user: CurrentUser) -> DocumentResponse:
    """Get document details including chunk count and processing status."""
    # TODO: Fetch from database
    return DocumentResponse(
        id=doc_id,
        namespace_id=UUID("00000000-0000-0000-0000-000000000000"),
        title="Placeholder",
        doc_type="pdf",
    )


@router.delete("/{doc_id}", status_code=204)
async def delete_document(doc_id: UUID, db: DbSession, user: CurrentUser) -> None:
    """Delete a document and its associated chunks and vectors."""
    # TODO: Delete from DB + Milvus
    return None


@router.patch("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: UUID, request: DocumentUpdateRequest, db: DbSession, user: CurrentUser
) -> DocumentResponse:
    """Update document metadata."""
    # TODO: Update in database
    return DocumentResponse(
        id=doc_id,
        namespace_id=UUID("00000000-0000-0000-0000-000000000000"),
        title=request.title or "Updated",
        doc_type="pdf",
    )
