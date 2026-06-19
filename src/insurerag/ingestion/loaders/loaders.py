"""
Document loading utilities for InsureRAG.

This module is responsible for reading raw source documents from disk.
It does not clean, chunk, embed, retrieve, or generate answers.

For the first MVP step, we only support internal Markdown policy files.
Official HTML/legal document loading will be added later.
"""

from pathlib import Path


def load_markdown_file(file_path: Path) -> str:
    """
    Load a single Markdown file from disk.

    Args:
        file_path: Path to the Markdown file.

    Returns:
        Raw Markdown content as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a Markdown file.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    if file_path.suffix.lower() != ".md":
        raise ValueError(f"Expected a Markdown file, got: {file_path}")

    return file_path.read_text(encoding="utf-8")


def load_markdown_files(directory_path: Path) -> dict[Path, str]:
    """
    Load all Markdown files from a directory.

    Args:
        directory_path: Directory containing Markdown files.

    Returns:
        Dictionary where keys are file paths and values are file contents.
    """

    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    markdown_files = sorted(directory_path.glob("*.md"))

    return {
        file_path: load_markdown_file(file_path)
        for file_path in markdown_files
    }