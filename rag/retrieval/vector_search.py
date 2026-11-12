
import os

from config.config import (
    VECTOR_SEARCH_INDEX,
    RETRIEVAL_NUM_RESULTS,
    RETRIEVAL_QUERY_TYPE
)

from databricks.ai_search.client import AISearchClient


SEARCH_COLUMNS = [
    "id",
    "document_id",
    "chunk_type",
    "article_number",
    "chunk_index",
    "content",
    "embedding_text",
    "metadata"
]



def get_vector_search_index():
    workspace_url = os.getenv("DATABRICKS_HOST")
    client_id = os.getenv("DATABRICKS_CLIENT_ID")
    client_secret = os.getenv("DATABRICKS_CLIENT_SECRET")

    credentials = [workspace_url, client_id, client_secret]

    if all(credentials):
        # Databricks Apps may provide the host without URL scheme.
        workspace_url = workspace_url.strip().rstrip("/")

        if not workspace_url.startswith(("https://", "http://")):
            workspace_url = f"https://{workspace_url}"

        client = AISearchClient(
            workspace_url=workspace_url,
            service_principal_client_id=client_id,
            service_principal_client_secret=client_secret
        )

    elif any(credentials):
        raise RuntimeError(
            "Incomplete Databricks service principal configuration."
        )

    else:
        # Notebook-native authentication
        client = AISearchClient()

    index_name = os.getenv(
        "VECTOR_SEARCH_INDEX",
        VECTOR_SEARCH_INDEX
    )

    return client.get_index(index_name=index_name)


def search_chunks(
    index,
    question: str,
    query_embedding: list[float],
    num_results: int = RETRIEVAL_NUM_RESULTS
) -> list[dict]:

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not query_embedding:
        raise ValueError("Query embedding cannot be empty.")

    response = index.similarity_search(
        query_text=question,
        query_vector=query_embedding,
        columns=SEARCH_COLUMNS,
        num_results=num_results,
        query_type=RETRIEVAL_QUERY_TYPE,
        query_columns=["content", "embedding_text"]
    )

    manifest_columns = [
        column["name"]
        for column in response["manifest"]["columns"]
    ]

    data_array = response["result"]["data_array"]

    results = [
        dict(zip(manifest_columns, row))
        for row in data_array
    ]

    return results
