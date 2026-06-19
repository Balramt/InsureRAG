from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from insurerag.ingestion.sources import OFFICIAL_SOURCES, SourceSpec


def download_source(source: SourceSpec, overwrite: bool = False) -> None:
    """
    Downloads one source document and saves it locally.

    This function only downloads raw files.
    It does not parse, clean, chunk, embed, or store vectors.
    """

    source.output_path.parent.mkdir(parents=True, exist_ok=True)

    if source.output_path.exists() and not overwrite:
        print(f"Skipping existing file: {source.output_path}")
        return

    request = Request(
        source.url,
        headers={
            "User-Agent": "InsureRAG/0.1 educational compliance RAG project"
        },
    )

    try:
        with urlopen(request, timeout=30) as response:
            content = response.read()

    except HTTPError as error:
        raise RuntimeError(
            f"Failed to download {source.name}. "
            f"HTTP status: {error.code}. URL: {source.url}"
        ) from error

    except URLError as error:
        raise RuntimeError(
            f"Failed to download {source.name}. "
            f"Network error: {error.reason}. URL: {source.url}"
        ) from error

    source.output_path.write_bytes(content)

    print(f"Downloaded source: {source.name}")
    print(f"Language: {source.language}")
    print(f"Source type: {source.source_type}")
    print(f"Parser type: {source.parser_type}")
    print(f"URL: {source.url}")
    print(f"Saved to: {source.output_path}")


def download_official_sources(overwrite: bool = False) -> None:
    """
    Downloads all configured official/regulatory source documents.
    """

    for source in OFFICIAL_SOURCES:
        download_source(source=source, overwrite=overwrite)


if __name__ == "__main__":
    download_official_sources(overwrite=False)