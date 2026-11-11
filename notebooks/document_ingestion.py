from config.config import (
    DOCUMENT_TABLE,
    PROCESSED_DOCUMENTS_PATH,
    RAW_EXTRACTION_FILENAME,
    STRUCTURED_CONTENT_FILENAME
)

from ingestion.pdf_extractor import extract_pdf
from ingestion.legal_structure_parser import parse_legal_structure
from ingestion.json_writer import save_json
from pyspark.sql import functions as F


def process_document(spark, document_id: str) -> dict:
    """
    Extracts PDF content, parses its legal structure,
    saves JSON files and updates the document record.
    """

    print(f"Starting document processing: {document_id}")

    # Step 1: Retrieve document information
    print("Step 1: Retrieving document information...")

    document = (
        spark.table(DOCUMENT_TABLE)
        .where(F.col("id") == document_id)
        .select("file_path")
        .first()
    )

    if document is None:
        raise ValueError(f"Document not found: {document_id}")

    document_path = document["file_path"]

    if not document_path:
        raise ValueError(f"Document has no file path: {document_id}")

    print(f"Document path: {document_path}")

    # Calculate output path
    output_directory = f"{PROCESSED_DOCUMENTS_PATH}/{document_id}"
    raw_path = f"{output_directory}/{RAW_EXTRACTION_FILENAME}"
    structured_path = f"{output_directory}/{STRUCTURED_CONTENT_FILENAME}"

    # Step 2: Extract PDF content
    print("Step 1: Extracting PDF content...")

    raw_content = extract_pdf(document_path)

    total_pages = len(raw_content["pages"])
    print(f"Extraction completed. Pages extracted: {total_pages}")

    # Step 3: Save raw extraction
    print("Step 2: Saving raw extraction...")

    save_json(raw_content, raw_path)

    print(f"Raw extraction saved: {raw_path}")

    # Step 4: Parse legal document structure
    print("Step 3: Parsing legal document structure...")

    structured_content = parse_legal_structure(raw_content)
    document_title = structured_content["title"]

    print(f"Legal structure parsed. Document title: {document_title}")

    # Step 5: Save structured content
    print("Step 4: Saving structured content...")

    save_json(structured_content, structured_path)

    print(f"Structured content saved: {structured_path}")

    # Step 6: Update document database record
    print("Step 5: Updating document database record...")

    update_query = f"""
        UPDATE {DOCUMENT_TABLE}
        SET
            title = :document_title,
            structured_content_path = :structured_path,
            status = :status,
            updated_at = current_timestamp()
        WHERE id = :document_id
    """

    spark.sql(
        update_query,
        args={
            "document_title": document_title,
            "structured_path": structured_path,
            "status": "DOCUMENT_PARSED",
            "document_id": document_id
        }
    )

    print("Document database record updated.")

    return {
        "document_id": document_id,
        "document_title": document_title,
        "total_pages": total_pages,
        "raw_extraction_path": raw_path,
        "structured_content_path": structured_path,
        "status": "DOCUMENT_PARSED"
    }

    