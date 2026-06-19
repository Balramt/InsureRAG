"""
Generic chunking utilities for InsureRAG ingestion.

This module converts ParsedDocument objects into retrieval-ready
DocumentChunk objects.

Important:
- This module does not know whether the original file was Markdown, HTML, PDF, or TXT.
- File-format-specific parsing belongs in loaders.py.
- This module only chunks clean ParsedDocument text.

Pipeline:

Raw file
    ↓ loaders.py
ParsedDocument
    ↓ chunkers.py
DocumentChunk
"""

from pydantic import ValidationError

from insurerag.schemas.chunk import ChunkMetadata, DocumentChunk
from insurerag.schemas.document import ParsedDocument


DEFAULT_CHUNK_SIZE_WORDS = 220
DEFAULT_CHUNK_OVERLAP_WORDS = 40


def split_text_into_word_chunks(
    text: str,
    chunk_size_words: int = DEFAULT_CHUNK_SIZE_WORDS,
    chunk_overlap_words: int = DEFAULT_CHUNK_OVERLAP_WORDS,
) -> list[str]:
    """
    Split clean text into word-based retrieval chunks.

    This function is file-format independent. It does not know whether
    the text came from Markdown, HTML, PDF, or TXT.

    Args:
        text: Clean text from a ParsedDocument.
        chunk_size_words: Maximum number of words per chunk.
        chunk_overlap_words: Number of overlapping words between chunks.

    Returns:
        List of text chunks.

    Raises:
        ValueError: If chunk size or overlap configuration is invalid.
    """

    if chunk_size_words <= 0:
        raise ValueError("chunk_size_words must be greater than 0")

    if chunk_overlap_words < 0:
        raise ValueError("chunk_overlap_words cannot be negative")

    if chunk_overlap_words >= chunk_size_words:
        raise ValueError("chunk_overlap_words must be smaller than chunk_size_words")

    words = text.split()

    if not words:
        return []

    if len(words) <= chunk_size_words:
        return [" ".join(words)]

    chunks: list[str] = []
    start_index = 0

    while start_index < len(words):
        end_index = min(start_index + chunk_size_words, len(words))
        chunk_words = words[start_index:end_index]

        chunks.append(" ".join(chunk_words))

        if end_index == len(words):
            break

        start_index = end_index - chunk_overlap_words

    return chunks


def _build_chunk_metadata(
    document: ParsedDocument,
    chunk_index: int,
    chunk_count: int,
) -> ChunkMetadata:
    """
    Build validated ChunkMetadata from ParsedDocument metadata.

    Args:
        document: ParsedDocument created by a loader.
        chunk_index: 1-based index of the current chunk.
        chunk_count: Total chunks created from the parent document.

    Returns:
        Validated ChunkMetadata object.

    Raises:
        ValueError: If ParsedDocument metadata is missing required fields.
    """

    raw_metadata = {
        **document.metadata,
        "parent_document_id": document.document_id,
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
    }

    try:
        return ChunkMetadata(**raw_metadata)

    except ValidationError as error:
        raise ValueError(
            f"Invalid metadata for ParsedDocument '{document.document_id}'. "
            f"Make sure loaders.py provides required metadata fields: "
            f"source_name, jurisdiction, source_type, and language."
        ) from error


def chunk_parsed_document(
    document: ParsedDocument,
    chunk_size_words: int = DEFAULT_CHUNK_SIZE_WORDS,
    chunk_overlap_words: int = DEFAULT_CHUNK_OVERLAP_WORDS,
) -> list[DocumentChunk]:
    """
    Convert one ParsedDocument into retrieval-ready DocumentChunk objects.

    This function is generic. It works for parsed content from:
    - Markdown
    - HTML
    - PDF
    - TXT

    Args:
        document: ParsedDocument created by a loader.
        chunk_size_words: Maximum number of words per chunk.
        chunk_overlap_words: Number of overlapping words between chunks.

    Returns:
        List of DocumentChunk objects.
    """

    text_chunks = split_text_into_word_chunks(
        text=document.text,
        chunk_size_words=chunk_size_words,
        chunk_overlap_words=chunk_overlap_words,
    )

    chunks: list[DocumentChunk] = []

    for index, text_chunk in enumerate(text_chunks, start=1):
        chunk_id = f"{document.document_id}_chunk_{index}"

        metadata = _build_chunk_metadata(
            document=document,
            chunk_index=index,
            chunk_count=len(text_chunks),
        )

        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                text=text_chunk,
                metadata=metadata,
            )
        )

    return chunks


def chunk_parsed_documents(
    documents: list[ParsedDocument],
    chunk_size_words: int = DEFAULT_CHUNK_SIZE_WORDS,
    chunk_overlap_words: int = DEFAULT_CHUNK_OVERLAP_WORDS,
) -> list[DocumentChunk]:
    """
    Convert multiple ParsedDocument objects into retrieval-ready chunks.

    Args:
        documents: Parsed documents from loaders.py.
        chunk_size_words: Maximum number of words per chunk.
        chunk_overlap_words: Number of overlapping words between chunks.

    Returns:
        Flat list of DocumentChunk objects.
    """

    chunks: list[DocumentChunk] = []

    for document in documents:
        chunks.extend(
            chunk_parsed_document(
                document=document,
                chunk_size_words=chunk_size_words,
                chunk_overlap_words=chunk_overlap_words,
            )
        )

    return chunks