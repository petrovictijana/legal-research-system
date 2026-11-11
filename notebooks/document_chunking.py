
import json
import uuid

from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    FloatType,
    ArrayType
)
from pyspark.sql.functions import current_timestamp

from config.config import DOCUMENT_TABLE, CHUNK_TABLE
from chunking.legal_chunker import LegalChunker
from tokenization.local_tokenizer import LocalCohereTokenizer


def process_document(spark, document_id: str):
    print(f"[Chunking] Starting document processing: {document_id}")

    # Step 1: Retrieve document information
    print("Step 1: Retrieving document information...")

    document_record = (
        spark.table(DOCUMENT_TABLE)
        .where(F.col("id") == document_id)
        .select("structured_content_path")
        .first()
    )

    if document_record is None:
        raise ValueError(f"Document not found: {document_id}")

    structured_content_path = document_record["structured_content_path"]

    if not structured_content_path:
        raise ValueError(
            f"Document has no structured content path: {document_id}"
        )

    print(f"Structured content path: {structured_content_path}")

    # Step 2: Retrieve structured file content
    print("Step 2: Loading structured document...")

    with open(structured_content_path, "r", encoding="utf-8") as file:
        document = json.load(file)

    # Step 3: Initialize tokenizer and chunker
    print("Step 3: Initializing tokenizer and chunker...")

    tokenizer = LocalCohereTokenizer()
    chunker = LegalChunker(tokenizer)

    # Step 4: Create chunks
    print("Step 4: Creating chunks...")

    chunks = chunker.chunk_document(
        document_id=document_id,
        document=document
    )

    if not chunks:
        print(f"No chunks generated for document {document_id}.")
        return 0

    print(f"Generated {len(chunks)} chunks.")

    # Step 5: Prepare chunks for database insertion
    print("Step 5: Preparing chunks for database insertion...")

    rows = [
        {
            "id": str(uuid.uuid4()),
            "document_id": chunk["document_id"],
            "chunk_type": chunk["chunk_type"],
            "article_number": chunk["article_number"],
            "chunk_index": chunk["chunk_index"],
            "content": chunk["content"],
            "embedding_text": chunk["embedding_text"],
            "metadata": json.dumps(
                chunk["metadata"],
                ensure_ascii=False
            ),
            "embedding": None
        }
        for chunk in chunks
    ]

    schema = StructType([
        StructField("id", StringType(), False),
        StructField("document_id", StringType(), False),
        StructField("chunk_type", StringType(), True),
        StructField("article_number", StringType(), True),
        StructField("chunk_index", IntegerType(), False),
        StructField("content", StringType(), False),
        StructField("embedding_text", StringType(), False),
        StructField("metadata", StringType(), True),
        StructField("embedding", ArrayType(FloatType()), True)
    ])

    chunks_df = spark.createDataFrame(rows, schema=schema)

    chunks_df = chunks_df.withColumn(
        "created_at",
        current_timestamp()
    )

    # Step 6: Save chunks in Delta table
    print("Step 6: Saving chunks in database...")

    (
        chunks_df.write
        .format("delta")
        .mode("overwrite")
        .option(
            "replaceWhere",
            f"document_id = '{document_id}'"
        )
        .saveAsTable(CHUNK_TABLE)
    )

    print(
        f"[Chunking] Successfully saved {len(chunks)} "
        f"chunks for document {document_id}."
    )

    return len(chunks)
