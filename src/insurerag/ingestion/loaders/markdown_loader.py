"""
Markdown loader for internal policy documents.

This module converts Markdown files into ParsedDocument objects.

Markdown-specific parsing belongs here, not in chunkers.py.
"""

import re
from pathlib import Path
from typing import Any

from insurerag.ingestion.metadata import parse_markdown_front_matter
from insurerag.schemas.document import ParsedDocument

from .utils import slugify, validate_required_metadata


MARKDOWN_SECTION_HEADING_PATTERN = re.compile(
    pattern=r"^##\s+(?P<section>.+?)\s*$",
    flags=re.MULTILINE,
)


def load_markdown_file(file_path: Path) -> str:
    """
    Load a single Markdown file from disk.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    if file_path.suffix.lower() != ".md":
        raise ValueError(f"Expected a Markdown file, got: {file_path}")

    return file_path.read_text(encoding="utf-8")


def load_markdown_files(directory_path: Path) -> dict[Path, str]:
    """
    Load all Markdown files from a directory as raw text.

    This is useful for debugging. The main ingestion flow should use
    load_markdown_documents(), because it returns ParsedDocument objects.
    """

    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    markdown_files = sorted(directory_path.glob("*.md"))

    return {
        file_path: load_markdown_file(file_path)
        for file_path in markdown_files
    }


def _extract_markdown_title(markdown_body: str) -> str | None:
    """
    Extract the first H1 title from a Markdown document body.
    """

    for line in markdown_body.splitlines():
        stripped_line = line.strip()

        if stripped_line.startswith("# ") and not stripped_line.startswith("## "):
            return stripped_line.replace("#", "", 1).strip()

    return None


def _split_markdown_body_by_sections(markdown_body: str) -> list[tuple[str, str]]:
    """
    Split Markdown body into section-level text blocks.

    Each '## ...' heading becomes one ParsedDocument later.
    """

    markdown_body = markdown_body.strip()
    document_title = _extract_markdown_title(markdown_body)

    section_matches = list(MARKDOWN_SECTION_HEADING_PATTERN.finditer(markdown_body))

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
            section_text = f"{document_title}\n\n{section_text}"

        sections.append((section_heading, section_text))

    return sections


def _build_markdown_metadata(
    front_matter: dict[str, str],
    source_path: Path,
    section: str,
) -> dict[str, Any]:
    """
    Build ParsedDocument metadata for one Markdown section.
    """

    validate_required_metadata(
        metadata=front_matter,
        source_path=source_path,
    )

    return {
        "source_name": front_matter["source_name"],
        "abbreviation": front_matter.get("abbreviation"),
        "jurisdiction": front_matter["jurisdiction"],
        "source_type": front_matter["source_type"],
        "language": front_matter["language"],
        "section": section,
        "section_title": section,
        "source_path": str(source_path),
        "document_version": front_matter.get("document_version"),
        "parser_type": "markdown_front_matter",
    }


def load_markdown_document(file_path: Path) -> list[ParsedDocument]:
    """
    Load one Markdown file and convert it into ParsedDocument objects.

    Each Markdown '## ...' section becomes one ParsedDocument.
    """

    markdown_text = load_markdown_file(file_path)
    front_matter, markdown_body = parse_markdown_front_matter(markdown_text)

    validate_required_metadata(
        metadata=front_matter,
        source_path=file_path,
    )

    document_abbreviation = front_matter.get("abbreviation") or front_matter["source_name"]
    document_slug = slugify(document_abbreviation)

    sections = _split_markdown_body_by_sections(markdown_body)

    parsed_documents: list[ParsedDocument] = []

    for index, (section_heading, section_text) in enumerate(sections, start=1):
        section_slug = slugify(section_heading)
        document_id = f"{document_slug}_{section_slug}_{index}"

        parsed_documents.append(
            ParsedDocument(
                document_id=document_id,
                text=section_text,
                metadata=_build_markdown_metadata(
                    front_matter=front_matter,
                    source_path=file_path,
                    section=section_heading,
                ),
            )
        )

    return parsed_documents


def load_markdown_documents(directory_path: Path) -> list[ParsedDocument]:
    """
    Load all Markdown files in a directory as ParsedDocument objects.
    """

    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    markdown_files = sorted(directory_path.glob("*.md"))

    parsed_documents: list[ParsedDocument] = []

    for file_path in markdown_files:
        parsed_documents.extend(load_markdown_document(file_path))

    return parsed_documents