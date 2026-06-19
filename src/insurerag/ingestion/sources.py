from dataclasses import dataclass
from pathlib import Path

from insurerag.config import VVG_HTML_PATH, VVG_INFOV_HTML_PATH


@dataclass(frozen=True)
class SourceSpec:
    """
    Defines one downloadable source document for the InsureRAG ingestion pipeline.

    This class is only configuration.

    It does not:
    - download files
    - parse HTML
    - clean text
    - create chunks
    - create embeddings
    - store data in Qdrant
    """

    name: str
    url: str
    output_path: Path
    source_type: str
    jurisdiction: str
    language: str
    parser_type: str


OFFICIAL_SOURCES: list[SourceSpec] = [
    SourceSpec(
        name="vvg",
        url="https://www.gesetze-im-internet.de/englisch_vvg/englisch_vvg.html",
        output_path=VVG_HTML_PATH,
        source_type="official_english_translation",
        jurisdiction="Germany",
        language="en",
        parser_type="vvg_english",
    ),
    SourceSpec(
        name="vvg_infov",
        url="https://www.bafin.de/SharedDocs/Veroeffentlichungen/EN/Aufsichtsrecht/Verordnung/VVG-InfoV_va_en.html",
        output_path=VVG_INFOV_HTML_PATH,
        source_type="official_english_regulatory_reference",
        jurisdiction="Germany",
        language="en",
        parser_type="bafin_article",
    ),
]