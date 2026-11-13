"""FastAPI application entry point for the Pravnislav backend.

Exposes the existing Databricks RAG pipeline over a small REST API:
``GET /health`` and ``POST /api/v1/chat``. This layer is an API facade only —
retrieval, embedding, context construction and generation all live in the
existing ``orchestration`` pipeline (see ``dependencies/rag.py``).

Run locally:   ``uvicorn main:app --reload``
Databricks:    see ``app.yaml``.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.router import api_router
from core.settings import get_settings

# Log to stdout; Databricks Apps captures process output. Configured once here
# rather than in library modules.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

settings = get_settings()

# Swagger/OpenAPI docs are served only in development.
_docs_enabled = settings.is_development

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs" if _docs_enabled else None,
    redoc_url="/redoc" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# ---------------------------------------------------------------------------
# Static frontend (Databricks Apps, single-app deployment).
#
# The Vite build output (frontend/dist) is served by this same process, so the
# browser talks to one origin and the frontend calls the API with a relative
# URL — no CORS, no second app. The mount is registered AFTER the routers, so
# /health and /api/v1/* keep precedence. In local development dist/ may not
# exist yet — then only the API is served.
# ---------------------------------------------------------------------------
_frontend_dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"

if _frontend_dist.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=str(_frontend_dist), html=True),
        name="frontend",
    )
