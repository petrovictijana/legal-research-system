import fitz


def extract_pdf(document_path: str) -> dict:
    """
    Extracts text blocks from a PDF document.
    """

    extracted_pages = []

    with fitz.open(document_path) as pdf:

        for page_index, page in enumerate(pdf):
            page_data = {
                "page_number": page_index + 1,
                "elements": []
            }

            page_dict = page.get_text("dict", sort=True)

            for block_index, block in enumerate(page_dict["blocks"]):
                lines = []

                for line in block.get("lines", []):
                    line_text = "".join(
                        span.get("text", "")
                        for span in line.get("spans", [])
                    )

                    if line_text.strip():
                        lines.append(line_text)

                text = "\n".join(lines).strip()

                if not text:
                    continue

                page_data["elements"].append({
                    "element_id": f"p{page_index + 1}_b{block_index}",
                    "type": "TEXT_BLOCK",
                    "text": text,
                    "bbox": list(block.get("bbox", []))
                })

            extracted_pages.append(page_data)

    return {
        "extraction_metadata": {
            "source_file": document_path,
            "total_pages": len(extracted_pages),
            "extractor": "PyMuPDF"
        },
        "pages": extracted_pages
    }
