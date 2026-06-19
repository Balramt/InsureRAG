"""
Run the internal document ingestion pipeline.

This script loads internal Markdown policy documents, extracts front matter
metadata, chunks the document body by section headings, prints a summary,
and saves the generated chunks as JSONL.

For now, this script does not embed chunks, store vectors, or call an LLM.
"""

from insurerag.config import PROCESSED_CHUNKS_DIR, RAW_INTERNAL_DIR
from insurerag.ingestion.chunkers import chunk_markdown_document
from insurerag.ingestion.loaders import load_markdown_files
from insurerag.ingestion.metadata import parse_markdown_front_matter
from insurerag.ingestion.writers import write_chunks_to_jsonl


def main() -> None:
    """
    Load, chunk, print, and persist all internal Markdown policy documents.
    """

    markdown_documents = load_markdown_files(RAW_INTERNAL_DIR)

    all_chunks = []

    for source_path, markdown_text in markdown_documents.items():
        front_matter, markdown_body = parse_markdown_front_matter(markdown_text)

        chunks = chunk_markdown_document(
            markdown_body=markdown_body,
            front_matter=front_matter,
            source_path=source_path,
        )

        all_chunks.extend(chunks)

        print("=" * 100)
        print(f"Source file: {source_path}")
        print(f"Source name: {front_matter.get('source_name')}")
        print(f"Generated chunks: {len(chunks)}")

        for chunk in chunks:
            print("-" * 100)
            print(f"Chunk ID: {chunk.chunk_id}")
            print(f"Section: {chunk.metadata.section}")
            print(f"Source type: {chunk.metadata.source_type.value}")
            print(f"Jurisdiction: {chunk.metadata.jurisdiction.value}")
            print("Preview:")
            print(chunk.text[:300])

    output_path = PROCESSED_CHUNKS_DIR / "internal_policy_chunks.jsonl"
    write_chunks_to_jsonl(all_chunks, output_path)

    print("=" * 100)
    print(f"Total documents processed: {len(markdown_documents)}")
    print(f"Total chunks generated: {len(all_chunks)}")
    print(f"Chunks written to: {output_path}")


if __name__ == "__main__":
    main()