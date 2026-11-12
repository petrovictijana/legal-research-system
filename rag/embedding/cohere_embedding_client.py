
import os
import cohere

from config.config import COHERE_EMBEDDING_MODEL


class CohereEmbeddingClient:
    INPUT_TYPE = "search_document"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("COHERE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Cohere API key is not configured. "
                "Provide api_key or set COHERE_API_KEY."
            )

        self.client = cohere.ClientV2(api_key=self.api_key)

    def generate_embeddings(
        self,
        texts: list[str],
        input_type: str = "search_document"
    ) -> list[list[float]]:

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
        input_type: str = "search_document"
    ) -> list[float]:

        return self.generate_embeddings(
            [text],
            input_type=input_type
        )[0]
