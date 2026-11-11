from databricks_openai import DatabricksOpenAI

from config.config import (
    LLM_MODEL,
    LLM_MAX_TOKENS
)


def generate_answer(messages: list[dict]) -> str:
    """
    Generates an answer using the configured Databricks LLM.
    """

    if not messages:
        raise ValueError("Messages cannot be empty.")

    client = DatabricksOpenAI(use_ai_gateway=True)

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        max_tokens=LLM_MAX_TOKENS
    )

    answer = response.choices[0].message.content

    # Reasoning models return content as a list of
    # typed blocks; extract the actual text blocks.
    if isinstance(answer, list):
        answer = "".join(
            part.get("text", "")
            for part in answer
            if part.get("type") == "text"
        )

    if not answer or not answer.strip():
        raise RuntimeError("The language model returned an empty answer.")

    return answer.strip()