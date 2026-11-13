"""Pydantic request/response models for the chat endpoint.

These define the public API contract. They are intentionally minimal and mirror
the structure the existing RAG pipeline already returns
(``{"answer": str, "sources": [{"document_title", "article_number"}]}``), so the
service layer maps results with no invented fields.

Validation error messages are user-facing and therefore in Serbian Cyrillic;
identifiers and docstrings stay in English.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator

# A generous upper bound: long enough for a detailed legal question, short
# enough to reject obvious abuse / accidental payloads.
QUESTION_MAX_LENGTH = 2000


class ChatRequest(BaseModel):
    """Incoming legal question."""

    question: str = Field(
        ...,
        description="Правно питање на српском језику.",
    )

    @field_validator("question")
    @classmethod
    def _validate_question(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Питање не сме бити празно.")
        if len(stripped) > QUESTION_MAX_LENGTH:
            raise ValueError(
                f"Питање је предугачко (највише {QUESTION_MAX_LENGTH} карактера)."
            )
        return stripped

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "Који су услови за закључење уговора о раду?"
            }
        }
    )


class Source(BaseModel):
    """A single legal citation backing an answer."""

    document_title: str = Field(..., description="Назив правног документа.")
    article_number: str = Field(..., description="Број члана.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"document_title": "Закон о раду", "article_number": "30"}
        }
    )


class ChatResponse(BaseModel):
    """Answer plus the legal sources it is grounded in."""

    answer: str = Field(..., description="Одговор заснован на правним изворима.")
    sources: list[Source] = Field(
        default_factory=list, description="Листа цитираних правних извора."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "answer": "Уговор о раду закључује се...",
                "sources": [
                    {"document_title": "Закон о раду", "article_number": "30"}
                ],
            }
        }
    )
