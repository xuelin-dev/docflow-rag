"""Document repository — async CRUD for documents and chunks."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk, Document, Namespace


class DocumentRepository:
    """Async CRUD operations for documents."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        namespace_id: uuid.UUID,
        title: str,
        doc_type: str,
        source_url: str | None = None,
        file_path: str | None = None,
        file_size_bytes: int | None = None,
        metadata: dict | None = None,
    ) -> Document:
        """Create a new document record."""
        doc = Document(
            namespace_id=namespace_id,
            title=title,
            doc_type=doc_type,
            source_url=source_url,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            metadata_=metadata or {},
        )
        self.session.add(doc)
        await self.session.flush()
        return doc

    async def get_by_id(self, doc_id: uuid.UUID) -> Document | None:
        """Get a document by ID."""
        return await self.session.get(Document, doc_id)

    async def list_by_namespace(
        self,
        namespace_id: uuid.UUID,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Document], int]:
        """List documents in a namespace with optional status filter."""
        query = select(Document).where(Document.namespace_id == namespace_id)
        if status:
            query = query.where(Document.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar() or 0

        query = query.order_by(Document.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def update_status(self, doc_id: uuid.UUID, status: str, error_message: str | None = None) -> None:
        """Update document processing status."""
        doc = await self.get_by_id(doc_id)
        if doc:
            doc.status = status
            if error_message:
                doc.error_message = error_message
            await self.session.flush()

    async def delete(self, doc_id: uuid.UUID) -> bool:
        """Delete a document and its chunks (cascading)."""
        doc = await self.get_by_id(doc_id)
        if doc:
            await self.session.delete(doc)
            await self.session.flush()
            return True
        return False
