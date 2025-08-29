"""
Markdown module for Notionary.

This module provides classes and utilities for working with Markdown content,
including builders, model processors, and parameter types.
"""

from __future__ import annotations

from .markdown_document_model import (
    MarkdownDocumentModel,
    MarkdownBlock,
    # ProcessorModel classes (renamed from previous Block classes)
    HeadingProcessorModel,
    ParagraphProcessorModel,
    QuoteProcessorModel,
    BulletedListProcessorModel,
    NumberedListProcessorModel,
    TodoProcessorModel,
    CalloutProcessorModel,
    CodeProcessorModel,
    ImageProcessorModel,
    VideoProcessorModel,
    AudioProcessorModel,
    FileProcessorModel,
    PdfProcessorModel,
    BookmarkProcessorModel,
    EmbedProcessorModel,
    TableProcessorModel,
    DividerProcessorModel,
    EquationProcessorModel,
    TableOfContentsProcessorModel,
    ToggleProcessorModel,
    ToggleableHeadingProcessorModel,
    ColumnProcessorModel,
    BreadcrumbProcessorModel,
)
from .markdown_node import MarkdownNode

__all__ = [
    # Core classes
    "MarkdownDocumentModel",
    "MarkdownNode",
    # Document model blocks
    "MarkdownBlock",
    # ProcessorModel classes (type-safe parameter models)
    "AudioProcessorModel",
    "BookmarkProcessorModel",
    "BreadcrumbProcessorModel",
    "BulletedListProcessorModel",
    "CalloutProcessorModel",
    "CodeProcessorModel",
    "ColumnProcessorModel",
    "DividerProcessorModel",
    "EmbedProcessorModel",
    "EquationProcessorModel",
    "FileProcessorModel",
    "HeadingProcessorModel",
    "ImageProcessorModel",
    "NumberedListProcessorModel",
    "ParagraphProcessorModel",
    "PdfProcessorModel",
    "QuoteProcessorModel",
    "TableProcessorModel",
    "TableOfContentsProcessorModel",
    "TodoProcessorModel",
    "ToggleProcessorModel",
    "ToggleableHeadingProcessorModel",
    "VideoProcessorModel",
]
