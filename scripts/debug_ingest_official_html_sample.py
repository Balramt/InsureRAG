"""
Debug official HTML ingestion on a tiny sample.

This script:
1. selects the downloaded VVG-InfoV HTML source,
2. loads only the first few sentences into ParsedDocument,
3. passes the ParsedDocument through the generic chunker,
4. writes the chunks to official_chunks.jsonl.

This is a learning/debug script.
"""

from insurerag.config import PROCESSED_INTERNAL_CHUNKS_PATH
from insurerag.ingestion.chunkers import chunk_parsed_documents
from insurerag.ingestion.loaders.html_loader import load_html_documents_sample
from insurerag.ingestion.sources import OFFICIAL_SOURCES
from insurerag.ingestion.writers import write_chunks_to_jsonl


def main() -> None:
    """
    Run tiny official HTML ingestion sample.
    """

    source = next(
        source for source in OFFICIAL_SOURCES if source.name == "vvg_infov"
    )

    parsed_documents = load_html_documents_sample(
        source=source,
        max_sentences=2,
    )

    chunks = chunk_parsed_documents(parsed_documents)

    write_chunks_to_jsonl(
        chunks=chunks,
        output_path=PROCESSED_INTERNAL_CHUNKS_PATH,
    )

    print("Official HTML sample ingestion completed.")
    print(f"Source: {source.name}")
    print(f"Parsed documents: {len(parsed_documents)}")
    print(f"Generated chunks: {len(chunks)}")
    print(f"Output file: {PROCESSED_INTERNAL_CHUNKS_PATH}")

    print("\nParsed document preview:")
    print(parsed_documents[0].text[:500])

    print("\nFirst chunk preview:")
    print(chunks[0].text[:500])


if __name__ == "__main__":
    main()