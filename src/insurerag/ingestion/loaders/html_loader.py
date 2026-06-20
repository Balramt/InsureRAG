"""
HTML loaders for official/regulatory source documents.

This module converts downloaded raw HTML files into ParsedDocument objects.

It does not:
- download files
- chunk documents
- create embeddings
- write JSONL
- store vectors
"""

import re

from bs4 import Tag

from insurerag.ingestion.sources import SourceSpec
from insurerag.schemas.document import ParsedDocument

from .utils import (
    build_official_source_metadata,
    clean_text,
    read_html_file,
    slugify,
    validate_required_metadata,
)


BAFIN_SECTION_HEADING_PATTERN = re.compile(
    pattern=r"^(Section\s+\d+[a-zA-Z]?)\s*[-–]?\s*(?P<title>.*)$"
)


def _extract_text_from_bafin_node(node: Tag) -> list[str]:
    """
    Extract useful legal text from one BaFin HTML node.

    Handles:
    - paragraphs
    - ordered lists
    - unordered lists
    - nested HTML nodes
    """

    extracted_text: list[str] = []

    if node.name == "p":
        text = clean_text(node.get_text(" ", strip=True))

        if text:
            extracted_text.append(text)

    elif node.name == "ol":
        for index, list_item in enumerate(
            node.find_all("li", recursive=False),
            start=1,
        ):
            text = clean_text(list_item.get_text(" ", strip=True))

            if text:
                extracted_text.append(f"{index}. {text}")

    elif node.name == "ul":
        for list_item in node.find_all("li", recursive=False):
            text = clean_text(list_item.get_text(" ", strip=True))

            if text:
                extracted_text.append(f"- {text}")

    else:
        for child in node.children:
            if isinstance(child, Tag):
                extracted_text.extend(_extract_text_from_bafin_node(child))

    return extracted_text


def load_bafin_article_html(source: SourceSpec) -> list[ParsedDocument]:
    """
    Parse the downloaded BaFin VVG-InfoV HTML file into section-level
    ParsedDocument objects.

    Each legal section becomes one ParsedDocument.
    """

    soup = read_html_file(source.output_path)

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    article_content = soup.find("div", class_="l-article__content")

    if article_content is None:
        raise ValueError(
            f"Could not find BaFin article content in: {source.output_path}"
        )

    parsed_documents: list[ParsedDocument] = []

    section_headings = article_content.find_all("h2")

    for heading in section_headings:
        heading_text = clean_text(heading.get_text(" ", strip=True))

        match = BAFIN_SECTION_HEADING_PATTERN.match(heading_text)

        if match is None:
            continue

        section_number = match.group(1).strip()
        section_title = match.group("title").strip()

        section_parts: list[str] = []

        for sibling in heading.find_next_siblings():
            if isinstance(sibling, Tag) and sibling.name == "h2":
                break

            if isinstance(sibling, Tag):
                section_parts.extend(_extract_text_from_bafin_node(sibling))

        section_text = "\n".join(section_parts).strip()

        if not section_text:
            continue

        document_id = f"{source.name}_{slugify(section_number)}"

        metadata = build_official_source_metadata(
            source=source,
            section_number=section_number,
            section_title=section_title,
        )

        # Hardcoded for now. Later we move this into SourceSpec.
        metadata["abbreviation"] = "VVG-InfoV"

        validate_required_metadata(
            metadata=metadata,
            source_path=source.output_path,
        )

        parsed_documents.append(
            ParsedDocument(
                document_id=document_id,
                text=section_text,
                metadata=metadata,
            )
        )

    return parsed_documents