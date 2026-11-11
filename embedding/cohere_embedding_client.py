
import cohere
from databricks.sdk.runtime import dbutils
from config.config import (
    COHERE_EMBEDDING_MODEL,
    COHERE_SECRET_SCOPE,
    COHERE_SECRET_KEY
)


class CohereEmbeddingClient:
    INPUT_TYPE = "search_document"

    def __init__(self):
        api_key = dbutils.secrets.get(
            scope=COHERE_SECRET_SCOPE,
            key=COHERE_SECRET_KEY
        )

        self.client = cohere.ClientV2(api_key=api_key)

    def generate_embeddings(
        self,
        texts: list[str],
        input_type: str = "search_document") -> list[list[float]]:

        if not texts:
            return []

        if any(not text or not text.strip() for text in texts):
            raise ValueError("Cannot generate embeddings for empty texts.")

        response = self.client.embed(
            model=COHERE_EMBEDDING_MODEL,
            texts=texts,
            input_type=input_type,
            embedding_types=["float"],
            truncate="NONE"
        )

        return response.embeddings.float


    def generate_embedding(
        self,
        text: str,
        input_type: str = "search_document") -> list[float]:

        return self.generate_embeddings(
            [text],
            input_type=input_type
        )[0]
        
