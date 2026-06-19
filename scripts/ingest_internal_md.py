"""
Ingest internal Markdown policy documents.

This script:
1. loads internal Markdown files,
2. converts them into ParsedDocument objects,
3. chunks them into DocumentChunk objects,
4. writes the chunks to JSONL.

Input:
    data/raw/internal/*.md

Output:
    data/processed/chunks/internal_chunks.jsonl
"""

from insurerag.config import RAW_INTERNAL_DIR, PROCESSED_INTERNAL_CHUNKS_PATH
from insurerag.ingestion.chunkers import chunk_parsed_documents
from insurerag.ingestion.loaders import load_markdown_documents
from insurerag.ingestion.writers import write_chunks_to_jsonl


def main() -> None:
    """
    Run internal Markdown ingestion.
    """

    parsed_documents = load_markdown_documents(RAW_INTERNAL_DIR)

    chunks = chunk_parsed_documents(parsed_documents)

    write_chunks_to_jsonl(
        chunks=chunks,
        output_path=PROCESSED_INTERNAL_CHUNKS_PATH,
    )

    print("Internal Markdown ingestion completed.")
    print(f"Parsed documents: {len(parsed_documents)}")
    print(f"Generated chunks: {len(chunks)}")
    print(f"Output file: {PROCESSED_INTERNAL_CHUNKS_PATH}")


if __name__ == "__main__":
    main()