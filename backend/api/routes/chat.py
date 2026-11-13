"""Chat endpoint: submit a legal question, receive an answer with sources.

The route stays thin: it validates input (via ``ChatRequest``), delegates to
``ChatService``, and maps a pipeline failure to a safe HTTP error. All business
logic lives in the service; all RAG access lives behind the ``rag`` dependency.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from dependencies.rag import RagPipelineError, RagRunner, get_rag_runner
from schemas.chat import ChatRequest, ChatResponse
from services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

# User-facing (Serbian Cyrillic) message for any pipeline failure. Technical
# details are logged server-side and never returned to the client.
_RAG_UNAVAILABLE_MESSAGE = (
    "Тренутно није могуће обрадити ваше питање. Покушајте поново касније."
)


def get_chat_service(
    rag_runner: RagRunner = Depends(get_rag_runner),
) -> ChatService:
    """Provide a ``ChatService`` wired to the current RAG runner."""
    return ChatService(rag_runner)


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Постави правно питање",
    response_description="Одговор са правним изворима.",
)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    try:
        # Offload the synchronous, I/O-bound RAG call to a worker thread so the
        # event loop stays free to serve other requests.
        return await run_in_threadpool(service.answer_question, request.question)
    except RagPipelineError:
        # Already logged with full detail at the source. Return a safe message.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_RAG_UNAVAILABLE_MESSAGE,
        )
