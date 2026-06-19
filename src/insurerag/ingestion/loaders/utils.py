"""
Shared utilities for InsureRAG loaders.

These helpers are used by multiple loader modules.

This file should not contain source-specific parsing logic.
"""

import re
from enum import Enum
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


def clean_text(text: str) -> str:
    """
    Normalize whitespace without rewriting the source text.
    """

    return " ".join(text.split())


def slugify(value: str) -> str:
    """
    Convert text into a simple lowercase identifier.
    """

    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def metadata_value(value: Any) -> str:
    """
    Convert enum values or plain values into metadata-safe strings.
    """

    if isinstance(value, Enum):
        return str(value.value)

    return str(value)


def validate_required_metadata(metadata: dict[str, Any], source_path: Path) -> None:
    """
    Validate metadata required later by ChunkMetadata.
    """

    required_fields = {
        "source_name",
        "jurisdiction",
        "source_type",
        "language",
    }

    missing_fields = sorted(
        field for field in required_fields if not metadata.get(field)
    )

    if missing_fields:
        raise ValueError(
            f"Missing required metadata fields in {source_path}: {missing_fields}"
        )


def read_html_file(file_path: Path) -> BeautifulSoup:
    """
    Read an HTML file from disk and return a BeautifulSoup object.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"HTML file not found: {file_path}")

    if file_path.suffix.lower() not in {".html", ".htm"}:
        raise ValueError(f"Expected an HTML file, got: {file_path}")

    html_bytes = file_path.read_bytes()  # why byte not text, Because HTML files may have encoding information inside

    return BeautifulSoup(html_bytes, "html.parser")


def build_official_source_metadata(
    source: Any,
    section_number: str,
    section_title: str,
) -> dict[str, Any]:
    """
    Build ParsedDocument metadata for official/regulatory source sections.
    """

    return {
        "source_name": source.name,
        "jurisdiction": metadata_value(source.jurisdiction),
        "source_type": metadata_value(source.source_type),
        "language": source.language,
        "section": f"{section_number}: {section_title}".strip(": "),
        "section_number": section_number,
        "section_title": section_title,
        "source_path": str(source.output_path),
        "source_url": getattr(source, "url", None),
        "parser_type": source.parser_type,
    }