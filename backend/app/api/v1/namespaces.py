"""Namespace management endpoints."""

from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, DbSession

router = APIRouter()


class NamespaceCreateRequest(BaseModel):
    """Create namespace request."""
    name: str = Field(..., min_length=1, max_length=128, pattern=r"^[a-zA-Z0-9_-]+$")
    description: str | None = None


class NamespaceResponse(BaseModel):
    """Namespace details."""
    id: UUID
    name: str
    description: str | None = None
    doc_count: int = 0
    chunk_count: int = 0
    created_at: str | None = None


class NamespaceListResponse(BaseModel):
    """List of namespaces."""
    namespaces: list[NamespaceResponse]


@router.post("", response_model=NamespaceResponse, status_code=201)
async def create_namespace(
    request: NamespaceCreateRequest, db: DbSession, user: CurrentUser
) -> NamespaceResponse:
    """Create a new document namespace."""
    # TODO: Insert into database
    return NamespaceResponse(
        id=UUID("00000000-0000-0000-0000-000000000000"),
        name=request.name,
        description=request.description,
    )


@router.get("", response_model=NamespaceListResponse)
async def list_namespaces(db: DbSession, user: CurrentUser) -> NamespaceListResponse:
    """List all namespaces with document counts."""
    # TODO: Query from database with aggregation
    return NamespaceListResponse(namespaces=[])


@router.delete("/{name}", status_code=204)
async def delete_namespace(name: str, db: DbSession, user: CurrentUser) -> None:
    """Delete a namespace and all associated documents, chunks, and vectors."""
    # TODO: Cascade delete
    return None
