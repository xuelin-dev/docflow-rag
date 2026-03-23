"""Rate limiting using Redis sliding window."""

from fastapi import HTTPException, Request

from app.services.redis import redis_service


async def check_rate_limit(request: Request, user_id: str, limit: int = 30, window: int = 60) -> None:
    """Check rate limit for a user on the current endpoint.

    Uses Redis sliding window counter: rate_limit:{user_id}:{path}

    Args:
        request: The incoming request.
        user_id: Authenticated user ID.
        limit: Maximum requests per window.
        window: Window size in seconds.

    Raises:
        HTTPException: If rate limit exceeded.
    """
    key = f"rate_limit:{user_id}:{request.url.path}"
    client = redis_service.client

    if client is None:
        return  # Skip rate limiting if Redis unavailable

    current = await client.incr(key)
    if current == 1:
        await client.expire(key, window)

    if current > limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {limit} requests per {window}s.",
            headers={"Retry-After": str(window)},
        )
