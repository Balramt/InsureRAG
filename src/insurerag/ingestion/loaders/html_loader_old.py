"""
HTML loaders for official/regulatory source documents.

This module converts supported HTML files into ParsedDocument objects.

Current support:
- English VVG HTML from Gesetze im Internet
- English BaFin VVG-InfoV article page
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
)


VVG_SECTION_HEADING_PATTERN = re.compile(
    pattern=r"^(Section\s+\d+[a-zA-Z]?)\s*(?P<title>.*)$"
)

BAFIN_SECTION_HEADING_PATTERN = re.compile(
    pattern=r"^(Section\s+\d+[a-zA-Z]?)\s*[-–]?\s*(?P<title>.*)$"
)

STRUCTURAL_HEADING_PATTERN = re.compile(
    pattern=r"^(Part|Chapter|Division|Subdivision)\b",
    flags=re.IGNORECASE,
)


def _is_center_bold_paragraph(paragraph: Tag) -> bool:
    """
    Check whether a paragraph is styled like a VVG section heading.
    """

    style = str(paragraph.get("style", "")).lower().replace(" ", "")

    return (
        "text-align:center" in style
        and "font-weight:bold" in style
    )


def load_vvg_english_html(source: SourceSpec) -> list[ParsedDocument]:
    """
    Parse the English VVG HTML file into section-level ParsedDocument objects.

    The VVG English HTML file uses centered bold paragraph tags for section
    headings. Each legal section becomes one ParsedDocument.
    """

    soup = read_html_file(source.output_path)

    parsed_documents: list[ParsedDocument] = []

    current_section_number: str | None = None
    current_section_title: str | None = None
    current_paragraphs: list[str] = []

    def flush_current_section() -> None:
        nonlocal current_section_number
        nonlocal current_section_title
        nonlocal current_paragraphs

        if not current_section_number:
            return

        if not current_paragraphs:
            return

        section_title = current_section_title or ""
        document_id = f"{source.name}_{slugify(current_section_number)}"

        parsed_documents.append(
            ParsedDocument(
                document_id=document_id,
                text="\n".join(current_paragraphs),
                metadata=build_official_source_metadata(
                    source=source,
                    section_number=current_section_number,
                    section_title=section_title,
                ),
            )
        )

        current_section_number = None
        current_section_title = None
        current_paragraphs = []

    for paragraph in soup.find_all("p"):
        text = clean_text(paragraph.get_text(" ", strip=True))

        if not text:
            continue

        if text.lower() == "table of contents":
            continue

        if _is_center_bold_paragraph(paragraph):
            if STRUCTURAL_HEADING_PATTERN.match(text):
                continue

            match = VVG_SECTION_HEADING_PATTERN.match(text)

            if match:
                flush_current_section()

                current_section_number = match.group(1).strip()
                current_section_title = match.group("title").strip()
                current_paragraphs = []
                continue

        if current_section_number:
            current_paragraphs.append(text)

    flush_current_section()

    return parsed_documents


def _extract_bafin_content_from_node(node: Tag) -> list[str]:
    """
    Extract useful legal text from one BaFin article node.
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
                extracted_text.extend(_extract_bafin_content_from_node(child))

    return extracted_text


def load_bafin_article_html(source: SourceSpec) -> list[ParsedDocument]:
    """
    Parse a BaFin article page into section-level ParsedDocument objects.

    The useful content is expected inside:

    <div class="l-article__content">

    Each section starts with an <h2> heading.
    """

    soup = read_html_file(source.output_path)

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
                section_parts.extend(_extract_bafin_content_from_node(sibling))

        section_text = "\n".join(section_parts).strip()

        if not section_text:
            continue

        document_id = f"{source.name}_{slugify(section_number)}"

        parsed_documents.append(
            ParsedDocument(
                document_id=document_id,
                text=section_text,
                metadata=build_official_source_metadata(
                    source=source,
                    section_number=section_number,
                    section_title=section_title,
                ),
            )
        )

    return parsed_documents