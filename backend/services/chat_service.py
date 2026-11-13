"""Application-level business logic for the chat endpoint.

Connects the API layer to the existing RAG pipeline: it receives a validated
question, invokes the pipeline (via an injected runner), and maps the pipeline's
raw result to the ``ChatResponse`` contract.

The service is intentionally independent of FastAPI request/response objects, so
it can be unit-tested in isolation. It is synchronous; the route offloads it to
a thread pool so the (blocking, I/O-bound) RAG call never blocks the event loop.
"""

import logging

from dependencies.rag import RagRunner
from schemas.chat import ChatResponse, Source

logger = logging.getLogger(__name__)


class ChatService:
    """Orchestrates a single question → answer+sources turn."""

    def __init__(self, rag_runner: RagRunner) -> None:
        self._rag_runner = rag_runner

    def answer_question(self, question: str) -> ChatResponse:
        """Run the RAG pipeline and map its result to ``ChatResponse``.

        Propagates ``RagPipelineError`` (raised by the runner) unchanged; the
        HTTP layer turns it into a safe response. The pipeline's own fallback
        answers (e.g. "insufficient information") come back as a normal answer
        and are passed through untouched — we never second-guess them.
        """
        raw = self._rag_runner(question)
        answer = raw.get("answer") or ""
        sources = self._map_sources(raw.get("sources") or [])
        return ChatResponse(answer=answer, sources=sources)

    @staticmethod
    def _map_sources(raw_sources: object) -> list[Source]:
        """Map the pipeline's source dicts to ``Source`` models, defensively.

        The pipeline returns ``{"document_title", "article_number"}`` entries.
        ``article_number`` may arrive as an int/float, so it is coerced to str.
        Malformed entries (not a dict, or missing a title) are skipped rather
        than fabricated, so the API never invents a citation.
        """
        if not isinstance(raw_sources, (list, tuple)):
            logger.warning("Unexpected 'sources' type from RAG pipeline: %r", type(raw_sources))
            return []

        mapped: list[Source] = []
        for item in raw_sources:
            if not isinstance(item, dict):
                continue
            title = item.get("document_title")
            if not title:
                continue
            article = item.get("article_number")
            mapped.append(
                Source(
                    document_title=str(title),
                    article_number="" if article is None else str(article),
                )
            )
        return mapped
