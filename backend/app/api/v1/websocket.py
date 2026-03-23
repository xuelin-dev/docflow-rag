"""WebSocket handlers for streaming RAG queries."""

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

router = APIRouter()


@router.websocket("/ws/query")
async def websocket_query(websocket: WebSocket) -> None:
    """Stream RAG query results via WebSocket.

    Protocol:
    1. Client sends: {"query": "...", "namespace": "...", "conversation_id": "..."}
    2. Server streams:
       - {"type": "status", "node": "analyze_query", "message": "Analyzing..."}
       - {"type": "status", "node": "hybrid_retrieve", "message": "Searching..."}
       - {"type": "chunk", "text": "partial answer text..."}
       - {"type": "sources", "data": [{...}]}
       - {"type": "done", "metadata": {"latency_ms": 1234, "cached": false}}
    """
    await websocket.accept()

    try:
        data = await websocket.receive_json()
        query = data.get("query", "")
        namespace = data.get("namespace", "default")

        # Send status updates
        stages = [
            ("analyze_query", "Analyzing query..."),
            ("hybrid_retrieve", "Searching documents..."),
            ("grade_documents", "Evaluating relevance..."),
            ("generate", "Generating answer..."),
        ]
        for node, message in stages:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json({"type": "status", "node": node, "message": message})

        # TODO: Integrate with RAG engine streaming
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json({"type": "chunk", "text": f"Placeholder response for: {query}"})
            await websocket.send_json({"type": "sources", "data": []})
            await websocket.send_json({
                "type": "done",
                "metadata": {"latency_ms": 0, "cached": False, "namespace": namespace},
            })

    except WebSocketDisconnect:
        pass
    except json.JSONDecodeError:
        await websocket.send_json({"type": "error", "message": "Invalid JSON"})
    except Exception as e:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
