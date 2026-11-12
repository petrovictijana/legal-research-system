CATALOG = "workspace"
SCHEMA = "legal_research_system"

DATABASE = f"{CATALOG}.{SCHEMA}"

DOCUMENT_TABLE = f"{DATABASE}.documents"
CHUNK_TABLE = f"{DATABASE}.document_chunks"

# Volume paths
RAW_DOCUMENTS_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/raw_documents"
PROCESSED_DOCUMENTS_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/processed_documents"

# Processing output files
RAW_EXTRACTION_FILENAME = "raw_extraction.json"
STRUCTURED_CONTENT_FILENAME = "structured_content.json"

CHUNK_MAX_TOKENS = 450
OVERLAP_TOKENS = 50

COHERE_EMBEDDING_MODEL = "embed-multilingual-v3.0"
EMBEDDING_DIMENSIONS = 1024
COHERE_SECRET_SCOPE = "legal-research-system"
COHERE_SECRET_KEY = "cohere-api-key"

VECTOR_SEARCH_INDEX = f"{DATABASE}.document_chunks_index"

RETRIEVAL_NUM_RESULTS = 5
RETRIEVAL_QUERY_TYPE = "HYBRID"

LLM_MODEL = "system.ai.qwen35-122b-a10b"
LLM_MAX_TOKENS = 8000