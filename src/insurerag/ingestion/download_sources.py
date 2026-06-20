import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from insurerag.ingestion.sources import OFFICIAL_SOURCES, SourceSpec


def download_source(
    source: SourceSpec,
    overwrite: bool = False,
    max_retries: int = 3,
    retry_delay_seconds: int = 5,
) -> bool:
    """
    Downloads one source document and saves it locally.

    This function only downloads raw files.
    It does not parse, clean, chunk, embed, or store vectors.

    Returns:
        True if the source was downloaded or already existed.
        False if the source could not be downloaded.
    """

    source.output_path.parent.mkdir(parents=True, exist_ok=True)

    if source.output_path.exists() and not overwrite:
        print(f"Skipping existing file: {source.output_path}")
        return True

    request = Request(
        source.url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
        },
    )

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Downloading {source.name} attempt {attempt}/{max_retries}...")

            with urlopen(request, timeout=30) as response:
                content = response.read()

            if not content:
                print(f"Downloaded empty content for {source.name}")
                return False

            source.output_path.write_bytes(content)

            print(f"Downloaded source: {source.name}")
            print(f"Language: {source.language}")
            print(f"Source type: {source.source_type}")
            print(f"Parser type: {source.parser_type}")
            print(f"URL: {source.url}")
            print(f"Saved to: {source.output_path}")
            print(f"Size: {len(content)} bytes")
            print("-" * 80)

            return True

        except HTTPError as error:
            print(
                f"HTTP error while downloading {source.name}: "
                f"{error.code}. URL: {source.url}"
            )

            if attempt < max_retries:
                time.sleep(retry_delay_seconds)

        except URLError as error:
            print(
                f"Network error while downloading {source.name}: "
                f"{error.reason}. URL: {source.url}"
            )

            if attempt < max_retries:
                time.sleep(retry_delay_seconds)

    print(f"Failed to download source after retries: {source.name}")
    print("-" * 80)
    return False


def download_official_sources(overwrite: bool = False) -> None:
    """
    Downloads all configured official/regulatory source documents.
    """

    successful_downloads = 0
    failed_downloads = 0

    for source in OFFICIAL_SOURCES:
        success = download_source(source=source, overwrite=overwrite)

        if success:
            successful_downloads += 1
        else:
            failed_downloads += 1

    print("Download summary")
    print(f"Successful: {successful_downloads}")
    print(f"Failed: {failed_downloads}")


if __name__ == "__main__":
    download_official_sources(overwrite=False)