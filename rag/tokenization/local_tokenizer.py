from transformers import AutoTokenizer


class LocalCohereTokenizer:

    MODEL_NAME = "CohereLabs/Cohere-embed-multilingual-v3.0"

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.MODEL_NAME
        )

    def count_tokens(self, text: str) -> int:
        if not text or not text.strip():
            return 0

        tokens = self.tokenizer.encode(
            text,
            add_special_tokens=True
        )

        return len(tokens)