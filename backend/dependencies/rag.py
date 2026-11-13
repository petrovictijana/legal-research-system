"""Access to the existing RAG pipeline.

This module is the single integration point between the FastAPI layer and the
Databricks RAG implementation. It deliberately does NOT re-implement retrieval,
embedding, context construction or generation — it only calls the existing
entry point ``orchestration.query_pipeline.generate_answer``, exactly as the
Streamlit app (``databricks/app.py``) does.

Design notes
------------
* **Lazy import.** ``orchestration`` lives in the Databricks workspace and is
  not importable in local/dev/test environments. Importing it lazily (on first
  use, not at module import) lets the API process start — and ``/health`` to
  respond — without Databricks, and keeps the import cost paid exactly once.
* **No duplicated Databricks config.** ``generate_answer`` owns its own
  Databricks authentication and Vector Search / LLM clients. We add none here.
* **Overridable.** ``get_rag_runner`` is a FastAPI dependency so tests can
  override it with a fake and never touch Databricks.
"""

import logging
import sys
from functools import lru_cache
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

# The pipeline is called as ``runner(question) -> {"answer", "sources"}``.
RagRunner = Callable[[str], dict]


class RagPipelineError(RuntimeError):
    """Raised when the RAG pipeline cannot produce a usable answer.

    Carries an internal (English) message for logs only; the HTTP layer maps it
    to a safe Serbian Cyrillic message and never leaks these details.
    """


@lru_cache(maxsize=1)
def _load_generate_answer() -> Callable[..., dict]:
    """Import and cache the real RAG entry point.

    Separated out so the (potentially slow) import happens once, and so tests
    can bypass it entirely via dependency override.

    The pipeline packages live in ``<repo>/rag`` and import each other flat
    (e.g. ``from config.config import ...``), so that directory — not the
    repo root — must be on ``sys.path``. They are not installed as a package,
    so the path is added here, computed from this file's location so it works
    in any deployment layout (local venv, Databricks Apps).
    """
    rag_root = Path(__file__).resolve().parents[2] / "rag"

    if str(rag_root) not in sys.path:
        sys.path.insert(0, str(rag_root))

    from orchestration.query_pipeline import generate_answer  # type: ignore

    return generate_answer


def run_rag(question: str) -> dict:
    """Run the existing RAG pipeline for ``question`` and return its raw result.

    Any failure — the pipeline being unavailable, raising, or returning an
    unexpected shape — is logged with full detail and re-raised as
    ``RagPipelineError`` so no internal error reaches the client.
    """
    try:
        generate_answer = _load_generate_answer()
    except Exception as exc:  # pragma: no cover - import failure path
        logger.exception(
            "RAG pipeline unavailable: cannot import orchestration.query_pipeline"
        )
        raise RagPipelineError("RAG pipeline is not available") from exc

    try:
        result = generate_answer(query=question)
    except Exception as exc:
        logger.exception("RAG pipeline execution failed")
        raise RagPipelineError("RAG pipeline execution failed") from exc

    if not isinstance(result, dict) or "answer" not in result:
        logger.error("RAG pipeline returned an unexpected result: %r", type(result))
        raise RagPipelineError("RAG pipeline returned no usable answer")

    return result


def get_rag_runner() -> RagRunner:
    """FastAPI dependency returning the callable that runs the RAG pipeline.

    Overridden in tests via ``app.dependency_overrides`` to avoid Databricks.
    """
    return run_rag
