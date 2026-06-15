from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class Jurisdiction(str, Enum):
    GERMANY = "Germany"
    EU = "EU"
    INTERNAL = "Internal"


class SourceType(str, Enum):
    LAW = "law"
    REGULATION = "regulation"
    GUIDANCE = "guidance"
    INTERNAL_POLICY = "internal_policy"


class SourceDocument(BaseModel):
    source_name: str = Field(..., description="Full name of the source document")
    abbreviation: str = Field(..., description="Short document name, e.g. VVG")
    jurisdiction: Jurisdiction
    source_type: SourceType
    language: str = Field(..., description="Document language, e.g. de or en")

    source_path: Optional[Path] = None
    source_url: Optional[str] = None
    document_version: Optional[str] = None
    download_date: Optional[str] = None