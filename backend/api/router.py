"""Aggregate API router.

Mounts the health endpoint at the root (``/health``) and the versioned
application endpoints under ``/api/v1`` (``/api/v1/chat``).
"""

from fastapi import APIRouter

from api.routes import chat, health

api_router = APIRouter()

# Liveness lives at the root, unversioned.
api_router.include_router(health.router)

# Versioned application API.
api_router.include_router(chat.router, prefix="/api/v1")
