
import json

from pyspark.sql import functions as F

from config.config import CHUNK_TABLE


def build_context(spark, retrieved_chunks):

    if not retrieved_chunks:
        return {"context": "", "sources": []}

    # Identify split articles that need reconstruction
    split_keys = set()

    for chunk in retrieved_chunks:
        if chunk["chunk_type"] != "ARTICLE":
            metadata = json.loads(chunk["metadata"])
            split_keys.add((
                chunk["document_id"],
                metadata["parent_id"]
            ))

    # Fetch all parts of the identified articles in one query
    grouped_chunks = {}

    if split_keys:
        keys_df = spark.createDataFrame(
            list(split_keys),
            ["document_id", "parent_id"]
        )

        rows = (
            spark.table(CHUNK_TABLE)
            .withColumn(
                "parent_id",
                F.get_json_object("metadata", "$.parent_id")
            )
            .withColumn(
                "part_index",
                F.get_json_object("metadata", "$.chunk_index").cast("int")
            )
            .join(
                F.broadcast(keys_df),
                ["document_id", "parent_id"]
            )
            .collect()
        )

        for row in rows:
            key = (row["document_id"], row["parent_id"])
            grouped_chunks.setdefault(key, []).append(row)

    # Build context in Vector Search relevance order
    context_parts = []
    sources = []
    processed = set()

    for chunk in retrieved_chunks:

        if chunk["chunk_type"] == "ARTICLE":
            key = (chunk["document_id"], chunk["article_number"])

            if key in processed:
                continue

            content = chunk["content"]
            source = {
                "document_id": chunk["document_id"],
                "article_number": chunk["article_number"]
            }

        else:
            metadata = json.loads(chunk["metadata"])
            key = (chunk["document_id"], metadata["parent_id"])

            if key in processed:
                continue

            parts = grouped_chunks.get(key, [])
            parts.sort(key=lambda part: part["part_index"])

            content = "\n\n".join(
                part["content"].strip()
                for part in parts
                if part["content"] and part["content"].strip()
            )

            source = {
                "document_id": chunk["document_id"],
                "article_number": chunk["article_number"],
                "parent_id": metadata["parent_id"]
            }

        if not content:
            continue

        processed.add(key)
        context_parts.append(content)
        sources.append({**source, "content": content})

    return {
        "context": "\n\n---\n\n".join(context_parts),
        "sources": sources
    }
