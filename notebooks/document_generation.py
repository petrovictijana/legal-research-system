from pyspark.sql import functions as F

from config.config import DOCUMENT_TABLE

from notebooks.document_retrieval import retrieve_context

from generation.prompt_builder import build_messages
from generation.answer_generator import generate_answer as generate_llm_answer


def _enrich_sources(spark, sources: list[dict]) -> list[dict]:
    """
    Adds document titles to retrieved sources.
    """

    document_ids = list({
        source["document_id"]
        for source in sources
    })

    if not document_ids:
        return sources

    documents = (
        spark.table(DOCUMENT_TABLE)
        .filter(F.col("id").isin(document_ids))
        .select("id", "title")
        .collect()
    )

    document_titles = {
        row["id"]: row["title"]
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


def generate_answer(spark, query: str, dbutils) -> dict:
    """
    Retrieves relevant legal context and generates an answer.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    print("Starting answer generation...")

    # Step 1: Retrieve relevant context
    retrieval_result = retrieve_context(
        spark=spark,
        query=query,
        dbutils=dbutils
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
        spark=spark,
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

    print("Answer successfully generated.")

    return {
        "query": query,
        "answer": answer,
        "sources": sources
    }