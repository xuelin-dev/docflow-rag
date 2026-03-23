"""Conversation history endpoints."""

from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import CurrentUser, DbSession

router = APIRouter()


class MessageResponse(BaseModel):
    """A single query-answer pair."""
    id: UUID
    query: str
    answer: str | None = None
    sources: list[dict] = []
    cached: bool = False
    latency_ms: int = 0
    created_at: str | None = None


class ConversationResponse(BaseModel):
    """Conversation with messages."""
    id: UUID
    title: str | None = None
    namespace: str = "default"
    messages: list[MessageResponse] = []
    created_at: str | None = None
    updated_at: str | None = None


class ConversationListResponse(BaseModel):
    """List of conversations."""
    conversations: list[ConversationResponse]
    total: int


@router.get("", response_model=ConversationListResponse)
async def list_conversations(db: DbSession, user: CurrentUser) -> ConversationListResponse:
    """List user's conversations."""
    # TODO: Query from database
    return ConversationListResponse(conversations=[], total=0)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID, db: DbSession, user: CurrentUser
) -> ConversationResponse:
    """Get conversation with full message history."""
    # TODO: Fetch from database
    return ConversationResponse(id=conversation_id)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: UUID, db: DbSession, user: CurrentUser) -> None:
    """Delete a conversation and its query history."""
    # TODO: Delete from database
    return None
