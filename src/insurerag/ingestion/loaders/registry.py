"""
Loader registry for official/regulatory sources.

This module selects the correct loader based on SourceSpec.parser_type.
"""

from insurerag.ingestion.sources import OFFICIAL_SOURCES, SourceSpec
from insurerag.schemas.document import ParsedDocument

from .html_loader_old import load_bafin_article_html, load_vvg_english_html


def load_source(source: SourceSpec) -> list[ParsedDocument]:
    """
    Load and parse one configured source based on its parser_type.
    """

    if source.parser_type == "vvg_english":
        return load_vvg_english_html(source)

    if source.parser_type == "bafin_article":
        return load_bafin_article_html(source)

    raise ValueError(
        f"Unsupported parser type '{source.parser_type}' for source '{source.name}'"
    )


def load_official_sources() -> list[ParsedDocument]:
    """
    Load and parse all configured official/regulatory sources.
    """

    parsed_documents: list[ParsedDocument] = []

    for source in OFFICIAL_SOURCES:
        parsed_documents.extend(load_source(source))

    return parsed_documents