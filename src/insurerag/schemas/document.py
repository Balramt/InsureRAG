"""
Document-level schemas for InsureRAG.

This module defines the metadata contract for original source documents,
such as German insurance laws, EU regulations, BaFin/EIOPA guidance,
and simulated internal insurance company policies.

These schemas describe full source documents, not retrievable chunks.
Chunk-level schemas are defined separately in `schemas.chunk`.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


class Jurisdiction(str, Enum):
    """Supported jurisdiction categories for source documents."""

    GERMANY = "Germany"
    EU = "EU"
    INTERNAL = "Internal"


class SourceType(str, Enum):
    """Supported source types used for source classification and filtering."""

    LAW = "law"
    REGULATION = "regulation"
    GUIDANCE = "guidance"
    INTERNAL_POLICY = "internal_policy"


class SourceDocument(BaseModel):
    """
    Metadata describing one original source document.

    A source document represents the full document before chunking.
    Examples include VVG, VVG-InfoV, EU AI Act, or an internal policy file.

    This metadata later supports:
    - source classification,
    - citation generation,
    - metadata-aware retrieval,
    - auditability of compliance answers.
    """

    source_name: str = Field(..., description="Full name of the source document.")
    abbreviation: str = Field(..., description="Short document name, e.g. VVG.")
    jurisdiction: Jurisdiction = Field(..., description="Jurisdiction of the source.")
    source_type: SourceType = Field(..., description="Type of source document.")
    language: str = Field(..., description="Document language, e.g. de or en.")

    source_path: Optional[Path] = Field(
        default=None,
        description="Local path to the raw source document.",
    )
    source_url: Optional[str] = Field(
        default=None,
        description="Official URL where the source document was obtained.",
    )
    document_version: Optional[str] = Field(
        default=None,
        description="Version or publication identifier if available.",
    )
    download_date: Optional[str] = Field(
        default=None,
        description="Date when the source document was downloaded.",
    )



class ParsedDocument(BaseModel):
    """
    Clean document section extracted from a raw source file.

    This object is created after loading/parsing and before chunking.

    Examples:
    - VVG Section 6
    - VVG-InfoV Section 1
    - Internal policy section
    - Future PDF page or section
    """

    document_id: str = Field(
        ...,
        description="Stable ID for the parsed document section.",
    )
    text: str = Field(
        ...,
        description="Clean text content of the parsed document section.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata needed for citation, filtering, and chunking.",
    )