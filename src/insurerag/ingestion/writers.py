"""
Writers for processed ingestion outputs.

This module persists validated ingestion objects, such as DocumentChunk
instances, to local files.

For the MVP, we save chunks as JSONL so they can be inspected manually
and later used for embedding and vector database ingestion.
"""

import json
from pathlib import Path

from insurerag.schemas.chunk import DocumentChunk


def write_chunks_to_jsonl(chunks: list[DocumentChunk], output_path: Path) -> None:
    """
    Write document chunks to a JSONL file.

    Each line in the output file represents one DocumentChunk.

    Args:
        chunks: List of validated DocumentChunk objects.
        output_path: Target JSONL file path.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(
                json.dumps(
                    chunk.model_dump(),
                    ensure_ascii=False,
                    default=str,
                )
            )
            file.write("\n")