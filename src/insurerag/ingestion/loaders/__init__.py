"""
Public loader API.
"""

from .markdown_loader import (
    load_markdown_document,
    load_markdown_documents,
    load_markdown_file,
    load_markdown_files,
)


__all__ = [
    "load_markdown_file",
    "load_markdown_files",
    "load_markdown_document",
    "load_markdown_documents",
]