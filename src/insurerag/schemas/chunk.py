"""
Chunk-level schemas for InsureRAG.

This module defines the metadata and text structure for retrievable
document chunks. A chunk is the smallest unit that will later be embedded,
stored in Qdrant, retrieved for a user question, and cited in an answer.

These schemas do not perform chunking. The actual splitting logic belongs
to `ingestion.chunkers`.
"""

from typing import Optional

from pydantic import BaseModel, Field

from insurerag.schemas.document import Jurisdiction, SourceType


class ChunkMetadata(BaseModel):
    """
    Metadata attached to a retrievable document chunk.

    This metadata is critical for:
    - source citations,
    - source classification,
    - metadata-aware filtering,
    - confidence/fallback decisions,
    - auditability of compliance answers.
    """

    source_name: str = Field(..., description="Full name of the source document.")
    abbreviation: str = Field(..., description="Short source abbreviation, e.g. VVG.")
    jurisdiction: Jurisdiction = Field(..., description="Jurisdiction of the source.")
    source_type: SourceType = Field(..., description="Type of source document.")
    language: str = Field(..., description="Chunk language, e.g. de or en.")

    section: Optional[str] = Field(
        default=None,
        description="Section identifier, e.g. § 7 or Section 2.",
    )
    article: Optional[str] = Field(
        default=None,
        description="Article identifier for EU regulations, e.g. Article 9.",
    )
    topic: Optional[str] = Field(
        default=None,
        description="Optional normalized topic label for filtering or evaluation.",
    )

    source_path: Optional[str] = Field(
        default=None,
        description="Local path to the original source document.",
    )
    source_url: Optional[str] = Field(
        default=None,
        description="Official URL of the source document, if available.",
    )
    document_version: Optional[str] = Field(
        default=None,
        description="Version or publication identifier if available.",
    )
    download_date: Optional[str] = Field(
        default=None,
        description="Date when the source document was downloaded.",
    )


class DocumentChunk(BaseModel):
    """
    A retrieval-ready chunk of text with citation metadata.

    Each DocumentChunk represents one piece of a source document that can be:
    - embedded,
    - stored in a vector database,
    - retrieved for a user query,
    - shown as evidence,
    - cited in the final answer.
    """

    chunk_id: str = Field(
        ...,
        description="Stable unique identifier for the chunk.",
    )
    text: str = Field(
        ...,
        description="Text content of the chunk.",
    )
    metadata: ChunkMetadata = Field(
        ...,
        description="Citation and filtering metadata for the chunk.",
    )