
from config.config import DOCUMENT_TABLE

from infrastructure.sql_connection import create_sql_connection

from retrieval.document_retrieval import retrieve_context

from generation.prompt_builder import build_messages
from generation.answer_generator import (
    generate_answer as generate_llm_answer
)


def _enrich_sources(
    connection,
    sources: list[dict]
) -> list[dict]:
    """
    Adds document titles to retrieved sources.
    """

    document_ids = list({
        source["document_id"]
        for source in sources
    })

    if not document_ids:
        return sources

    placeholders = ", ".join(["?"] * len(document_ids))

    query = f"""
        SELECT id, title
        FROM {DOCUMENT_TABLE}
        WHERE id IN ({placeholders})
    """

    cursor = connection.cursor()

    try:
        cursor.execute(query, document_ids)
        documents = cursor.fetchall()
    finally:
        cursor.close()

    document_titles = {
        row[0]: row[1]
        for row in documents
    }

    enriched_sources = []

    for source in sources:
        document_title = document_titles.get(
            source["document_id"]
        )

        if not document_title:
            raise ValueError(
                f"Document title not found for document "
                f"{source['document_id']}."
            )

        enriched_sources.append({
            **source,
            "document_title": document_title
        })

    return enriched_sources


def generate_answer(query: str) -> dict:
    """
    Orchestrates the complete query pipeline:
    retrieval, context preparation and answer generation.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    print("Starting query pipeline...")

    connection = create_sql_connection()

    try:
        # Step 1: Retrieve relevant context
        retrieval_result = retrieve_context(
            connection=connection,
            query=query
        )

        sources = retrieval_result["sources"]

        # Step 2: Handle empty retrieval result
        if not sources:
            return {
                "query": query,
                "answer": (
                    "Informacija nije dostupna u dostavljenim dokumentima."
                ),
                "sources": []
            }

        # Step 3: Enrich sources with document titles
        sources = _enrich_sources(
            connection=connection,
            sources=sources
        )

        # Step 4: Build LLM messages
        messages = build_messages(
            query=query,
            sources=sources
        )

        # Step 5: Generate answer
        answer = generate_llm_answer(
            messages=messages
        )

        print("Query pipeline successfully completed.")

        return {
            "query": query,
            "answer": answer,
            "sources": sources
        }

    finally:
        connection.close()
