"""API key and JWT authentication."""

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config import settings

api_key_scheme = APIKeyHeader(name=settings.api_key_header, auto_error=False)


async def get_current_user(api_key: str | None = Security(api_key_scheme)) -> str:
    """Validate API key and return user identifier.

    MVP: Simple API key validation.
    V1: JWT token authentication with refresh tokens.
    """
    if api_key is None:
        raise HTTPException(status_code=401, detail="Missing API key in header")

    if settings.debug:
        return "dev-user"

    # TODO: Look up api_key in users table
    raise HTTPException(status_code=401, detail="Invalid API key")
