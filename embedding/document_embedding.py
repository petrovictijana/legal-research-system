
from delta.tables import DeltaTable

from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    ArrayType,
    FloatType
)

from config.config import (
    CHUNK_TABLE,
    EMBEDDING_DIMENSIONS)

def process_document(
    spark,
    document_id: str,
    embedding_client,
    batch_size: int = 50
):
    print(f"[Embedding] Starting: {document_id}")

    schema = StructType([
        StructField("id", StringType(), False),
        StructField(
            "embedding",
            ArrayType(FloatType(), containsNull=False),
            False
        )
    ])

    processed_count = 0
    delta_table = DeltaTable.forName(spark, CHUNK_TABLE)

    while True:
        pending_chunks = (
            spark.table(CHUNK_TABLE)
            .where(
                (F.col("document_id") == document_id) &
                F.col("embedding").isNull() &
                F.col("embedding_text").isNotNull() &
                (F.length(F.trim(F.col("embedding_text"))) > 0)
            )
            .orderBy("chunk_index")
            .limit(batch_size)
            .select("id", "embedding_text")
            .collect()
        )

        if not pending_chunks:
            break

        texts = [row["embedding_text"] for row in pending_chunks]

        embeddings = embedding_client.generate_embeddings(texts)

        if len(embeddings) != len(pending_chunks):
            raise ValueError(
                "Number of generated embeddings does not match "
                "number of input chunks."
            )

        if any(
            len(embedding) != EMBEDDING_DIMENSIONS
            for embedding in embeddings
        ):
            raise ValueError(
                f"Expected embeddings with {EMBEDDING_DIMENSIONS} dimensions."
            )

        updates = [
            (row["id"], embedding)
            for row, embedding in zip(pending_chunks, embeddings)
        ]

        updates_df = spark.createDataFrame(updates, schema)

        (
            delta_table.alias("target")
            .merge(
                updates_df.alias("source"),
                "target.id = source.id"
            )
            .whenMatchedUpdate(
                set={"embedding": "source.embedding"}
            )
            .execute()
        )

        processed_count += len(pending_chunks)

        print(
            f"[Embedding] Processed: {processed_count}"
        )

    print(
        f"[Embedding] Completed. Total: {processed_count}"
    )

    return processed_count
