"""
Debug BaFin HTML section parsing.

This script parses the downloaded BaFin VVG-InfoV HTML file into
section-level ParsedDocument objects and prints previews.

It does not chunk or write JSONL.
"""

from insurerag.ingestion.loaders.html_loader import load_bafin_article_html
from insurerag.ingestion.sources import OFFICIAL_SOURCES


def main() -> None:
    """
    Parse BaFin VVG-InfoV sections and inspect ParsedDocuments.
    """

    source = next(
        source for source in OFFICIAL_SOURCES if source.name == "vvg_infov"
    )

    parsed_documents = load_bafin_article_html(source=source)

    print("BaFin section parsing completed.")
    print(f"Source: {source.name}")
    print(f"Parsed documents: {len(parsed_documents)}")

    print("\nParsed document previews:")

    for parsed_document in parsed_documents[:5]:
        print("-" * 80)
        print(f"Document ID: {parsed_document.document_id}")
        print(f"Section: {parsed_document.metadata.get('section_number')}")
        print(f"Title: {parsed_document.metadata.get('section_title')}")
        print(f"Source type: {parsed_document.metadata.get('source_type')}")
        print(f"Abbreviation: {parsed_document.metadata.get('abbreviation')}")
        print(f"Text length: {len(parsed_document.text)}")
        print(parsed_document.text[:500])


if __name__ == "__main__":
    main()