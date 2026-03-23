"""Mount all v1 route modules."""

from fastapi import APIRouter

from app.api.v1 import conversations, documents, evals, namespaces, query, websocket

v1_router = APIRouter(tags=["v1"])

v1_router.include_router(query.router, prefix="/query", tags=["query"])
v1_router.include_router(documents.router, prefix="/documents", tags=["documents"])
v1_router.include_router(namespaces.router, prefix="/namespaces", tags=["namespaces"])
v1_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
v1_router.include_router(evals.router, prefix="/evals", tags=["evaluation"])
v1_router.include_router(websocket.router, tags=["websocket"])
