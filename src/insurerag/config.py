from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_INTERNAL_DIR = DATA_DIR / "raw" / "internal"
RAW_OFFICIAL_DIR = DATA_DIR / "raw" /"official"


RAW_VVG_DIR = RAW_OFFICIAL_DIR / "vvg"
RAW_VVG_INFOV_DIR = RAW_OFFICIAL_DIR / "vvg_infov"

VVG_HTML_PATH = RAW_VVG_DIR / "vvg_en.html"
VVG_INFOV_HTML_PATH = RAW_VVG_INFOV_DIR / "vvg_infov_en.html"

PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_CHUNKS_DIR = PROCESSED_DIR / "chunks"


PROCESSED_INTERNAL_CHUNKS_PATH = PROCESSED_CHUNKS_DIR / "internal_chunks.jsonl"
PROCESSED_OFFICIAL_CHUNKS_PATH = PROCESSED_CHUNKS_DIR / "official_chunks.jsonl"

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 100