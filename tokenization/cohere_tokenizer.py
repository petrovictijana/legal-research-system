import cohere
from tokenization.tokenizer import Tokenizer


class CohereTokenizer:

    def __init__(self, api_key: str, model: str):
        self.client = cohere.Client(api_key=api_key)
        self.model = model

    def count_tokens(self, text: str) -> int:
        if not text or not text.strip():
            return 0

        response = self.client.tokenize(
            text=text,
            model=self.model,
            offline=False
        )

        return len(response.tokens)