
import json

from config.config import CHUNK_TABLE


def _parse_metadata(metadata):
    if isinstance(metadata, dict):
        return metadata

    if isinstance(metadata, str):
        return json.loads(metadata)

    raise ValueError("Invalid chunk metadata format.")


def build_context(connection, retrieved_chunks):

    if not retrieved_chunks:
        return {"context": "", "sources": []}

    # Identify split articles that need reconstruction
    split_keys = set()

    for chunk in retrieved_chunks:
        if chunk["chunk_type"] != "ARTICLE":
            metadata = _parse_metadata(chunk["metadata"])

            split_keys.add((
                chunk["document_id"],
                metadata["parent_id"]
            ))

    # Fetch all parts of identified articles in one SQL query
    grouped_chunks = {}

    if split_keys:
        conditions = []
        parameters = []

        for document_id, parent_id in split_keys:
            conditions.append(
                "(document_id = ? "
                "AND get_json_object(metadata, '$.parent_id') = ?)"
            )

            parameters.extend([document_id, parent_id])

        query = f"""
            SELECT
                document_id,
                get_json_object(metadata, '$.parent_id') AS parent_id,
                content,
                CAST(
                    get_json_object(metadata, '$.chunk_index')
                    AS INT
                ) AS part_index
            FROM {CHUNK_TABLE}
            WHERE {" OR ".join(conditions)}
        """

        cursor = connection.cursor()

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()
        finally:
            cursor.close()

        for row in rows:
            document_id, parent_id, content, part_index = row

            key = (document_id, parent_id)

            grouped_chunks.setdefault(key, []).append({
                "content": content,
                "part_index": part_index
            })

    # Build context in Vector Search relevance order
    context_parts = []
    sources = []
    processed = set()

    for chunk in retrieved_chunks:

        if chunk["chunk_type"] == "ARTICLE":
            key = (
                chunk["document_id"],
                chunk["article_number"]
            )

            if key in processed:
                continue

            content = chunk["content"]

            source = {
                "document_id": chunk["document_id"],
                "article_number": chunk["article_number"]
            }

        else:
            metadata = _parse_metadata(chunk["metadata"])

            key = (
                chunk["document_id"],
                metadata["parent_id"]
            )

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
