"""
Metadata extraction utilities for InsureRAG ingestion.

This module extracts source-level metadata from raw Markdown documents
and converts it into validated chunk metadata.

For the first MVP, we support simple Markdown front matter metadata.

Example front matter:

---
source_name: Internal Customer Information Policy
abbreviation: ICIP
jurisdiction: Internal
source_type: internal_policy
language: en
document_version: 0.1
---

This module does not load files, split chunks, embed text, or call an LLM.
"""

from pathlib import Path

from insurerag.schemas.chunk import ChunkMetadata
from insurerag.schemas.document import Jurisdiction, SourceType


def parse_markdown_front_matter(markdown_text: str) -> tuple[dict[str, str], str]:
    """
    Extract front matter metadata from a Markdown document.

    Args:
        markdown_text: Raw Markdown document text.

    Returns:
        A tuple containing:
        - metadata dictionary extracted from front matter,
        - Markdown body without the front matter.

    If no valid front matter is found, an empty metadata dictionary
    and the original Markdown text are returned.
    """

    stripped_text = markdown_text.lstrip()

    if not stripped_text.startswith("---"):
        return {}, markdown_text

    parts = stripped_text.split("---", maxsplit=2)

    if len(parts) < 3:
        return {}, markdown_text

    raw_metadata = parts[1].strip()
    body = parts[2].strip()

    metadata: dict[str, str] = {}

    for line in raw_metadata.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", maxsplit=1)
        metadata[key.strip()] = value.strip()

    return metadata, body


def build_chunk_metadata(
    front_matter: dict[str, str],
    source_path: Path,
    section: str | None = None,
) -> ChunkMetadata:
    """
    Build validated chunk metadata from Markdown front matter.

    Args:
        front_matter: Metadata extracted from the Markdown document.
        source_path: Local path to the raw Markdown source file.
        section: Optional section heading for the chunk.

    Returns:
        Validated ChunkMetadata object.

    Raises:
        KeyError: If a required metadata field is missing.
        ValueError: If jurisdiction or source_type is invalid.
    """

    return ChunkMetadata(
        source_name=front_matter["source_name"],
        abbreviation=front_matter["abbreviation"],
        jurisdiction=Jurisdiction(front_matter["jurisdiction"]),
        source_type=SourceType(front_matter["source_type"]),
        language=front_matter["language"],
        section=section,
        source_path=str(source_path),
        document_version=front_matter.get("document_version"),
    )