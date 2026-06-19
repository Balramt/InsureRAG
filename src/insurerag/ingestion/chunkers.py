"""
Chunking utilities for InsureRAG ingestion.

This module converts cleaned Markdown document bodies into retrieval-ready
DocumentChunk objects.

For the first MVP, we support section-based chunking for internal Markdown
policy documents. Each "## Section ..." block becomes one chunk.

This module does not load files from disk, parse front matter, embed text,
store vectors, or call an LLM.
"""

import re
from pathlib import Path

from insurerag.ingestion.metadata import build_chunk_metadata
from insurerag.schemas.chunk import DocumentChunk


SECTION_HEADING_PATTERN = re.compile(
    pattern=r"^##\s+(?P<section>.+?)\s*$",
    flags=re.MULTILINE,
)


def _slugify(value: str) -> str:
    """
    Convert text into a simple lowercase identifier.

    Args:
        value: Raw text value.

    Returns:
        Slugified identifier suitable for chunk IDs.
    """

    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def _extract_markdown_title(markdown_body: str) -> str | None:
    """
    Extract the first H1 title from a Markdown document body.

    Args:
        markdown_body: Markdown text without front matter.

    Returns:
        First H1 title if available, otherwise None.
    """

    for line in markdown_body.splitlines():
        stripped_line = line.strip()

        if stripped_line.startswith("# ") and not stripped_line.startswith("## "):
            return stripped_line

    return None


def split_markdown_by_sections(markdown_body: str) -> list[tuple[str, str]]:
    """
    Split a Markdown document body into section-level chunks.

    Args:
        markdown_body: Markdown text without front matter.

    Returns:
        A list of tuples:
        - section heading,
        - section text including the document title for context.
    """

    markdown_body = markdown_body.strip()
    document_title = _extract_markdown_title(markdown_body)

    section_matches = list(SECTION_HEADING_PATTERN.finditer(markdown_body))

    if not section_matches:
        return [("Full Document", markdown_body)]

    sections: list[tuple[str, str]] = []

    for index, match in enumerate(section_matches):
        section_heading = match.group("section").strip()
        section_start = match.start()

        if index + 1 < len(section_matches):
            section_end = section_matches[index + 1].start()
        else:
            section_end = len(markdown_body)

        section_text = markdown_body[section_start:section_end].strip()

        if document_title:
            chunk_text = f"{document_title}\n\n{section_text}"
        else:
            chunk_text = section_text

        sections.append((section_heading, chunk_text))

    return sections


def chunk_markdown_document(
    markdown_body: str,
    front_matter: dict[str, str],
    source_path: Path,
) -> list[DocumentChunk]:
    """
    Convert a Markdown document body into validated DocumentChunk objects.

    Args:
        markdown_body: Markdown text without front matter.
        front_matter: Metadata extracted from the Markdown document.
        source_path: Local path to the raw Markdown source file.

    Returns:
        List of validated DocumentChunk objects.
    """

    section_chunks = split_markdown_by_sections(markdown_body)

    document_abbreviation = front_matter["abbreviation"]
    document_slug = _slugify(document_abbreviation)

    chunks: list[DocumentChunk] = []

    for index, (section_heading, section_text) in enumerate(section_chunks, start=1):
        section_slug = _slugify(section_heading)

        chunk_id = f"{document_slug}-{section_slug}-{index}"

        metadata = build_chunk_metadata(
            front_matter=front_matter,
            source_path=source_path,
            section=section_heading,
        )

        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                text=section_text,
                metadata=metadata,
            )
        )

    return chunks