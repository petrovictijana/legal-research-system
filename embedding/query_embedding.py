
from config.config import EMBEDDING_DIMENSIONS


def generate_query_embedding(question: str, embedding_client) -> list[float]:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    embedding = embedding_client.generate_embedding(
        question.strip(),
        input_type="search_query"
    )

    if len(embedding) != EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
            f"got {len(embedding)}."
        )

    return embedding
