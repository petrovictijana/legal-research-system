
from embedding.cohere_embedding_client import CohereEmbeddingClient
from embedding.query_embedding import generate_query_embedding

from retrieval.vector_search import (
    get_vector_search_index,
    search_chunks
)

from retrieval.context_builder import build_context


def retrieve_context(connection, query: str) -> dict:
    """
    Retrieves relevant document chunks and builds context
    for the given user query.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    print("Starting document retrieval...")

    # Step 1: Initialize dependencies
    embedding_client = CohereEmbeddingClient()
    index = get_vector_search_index()

    # Step 2: Generate query embedding
    query_embedding = generate_query_embedding(
        question=query,
        embedding_client=embedding_client
    )

    # Step 3: Retrieve relevant chunks
    retrieved_chunks = search_chunks(
        index=index,
        question=query,
        query_embedding=query_embedding
    )

    if not retrieved_chunks:
        return {
            "query": query,
            "context": "",
            "sources": []
        }

    # Step 4: Build context using SQL connection
    context_result = build_context(
        connection=connection,
        retrieved_chunks=retrieved_chunks
    )

    print("Context successfully built.")

    return {
        "query": query,
        "context": context_result["context"],
        "sources": context_result["sources"]
    }
