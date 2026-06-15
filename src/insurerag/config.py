from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_INTERNAL_DIR = DATA_DIR / "raw" / "internal"

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 100