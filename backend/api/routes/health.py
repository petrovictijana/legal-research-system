"""Liveness endpoint.

Reports that the API process is up. Intentionally does NOT touch Databricks or
the RAG pipeline, so it stays a cheap, always-available liveness signal.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str = "ok"


@router.get("/health", response_model=HealthResponse, summary="Провера доступности API-ја")
def health() -> HealthResponse:
    return HealthResponse(status="ok")
