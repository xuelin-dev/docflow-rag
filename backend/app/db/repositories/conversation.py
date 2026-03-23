"""Conversation repository — async CRUD for conversations and query history."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Conversation, QueryHistory


class ConversationRepository:
    """Async CRUD operations for conversations and query history."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        user_id: uuid.UUID | None = None,
        namespace_id: uuid.UUID | None = None,
        title: str | None = None,
    ) -> Conversation:
        """Create a new conversation."""
        conv = Conversation(user_id=user_id, namespace_id=namespace_id, title=title)
        self.session.add(conv)
        await self.session.flush()
        return conv

    async def get_by_id(self, conversation_id: uuid.UUID) -> Conversation | None:
        """Get a conversation by ID."""
        return await self.session.get(Conversation, conversation_id)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Conversation], int]:
        """List conversations for a user."""
        query = select(Conversation).where(Conversation.user_id == user_id)
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar() or 0

        query = query.order_by(Conversation.updated_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def add_query(
        self,
        conversation_id: uuid.UUID,
        query: str,
        answer: str | None = None,
        sources: dict | None = None,
        query_type: str | None = None,
        rewrite_count: int = 0,
        cached: bool = False,
        latency_ms: int | None = None,
    ) -> QueryHistory:
        """Add a query-answer pair to a conversation."""
        entry = QueryHistory(
            conversation_id=conversation_id,
            query=query,
            answer=answer,
            sources=sources,
            query_type=query_type,
            rewrite_count=rewrite_count,
            cached=cached,
            latency_ms=latency_ms,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def delete(self, conversation_id: uuid.UUID) -> bool:
        """Delete a conversation and its query history (cascading)."""
        conv = await self.get_by_id(conversation_id)
        if conv:
            await self.session.delete(conv)
            await self.session.flush()
            return True
        return False
