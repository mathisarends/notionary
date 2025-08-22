"""
Clean Fluent Markdown Builder
============================

A direct, chainable builder for all MarkdownNode types without overengineering.
Maps 1:1 to the available blocks with clear, expressive method names.
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Self

from notionary.blocks.audio import AudioMarkdownBlockParams, AudioMarkdownNode
from notionary.blocks.bookmark import BookmarkMarkdownBlockParams, BookmarkMarkdownNode
from notionary.blocks.breadcrumbs import BreadcrumbMarkdownNode
from notionary.blocks.bulleted_list import (
    BulletedListMarkdownBlockParams,
    BulletedListMarkdownNode,
)
from notionary.blocks.callout import CalloutMarkdownBlockParams, CalloutMarkdownNode
from notionary.blocks.code import CodeBlock, CodeLanguage, CodeMarkdownNode
from notionary.blocks.column import (
    ColumnListMarkdownBlockParams,
    ColumnListMarkdownNode,
    ColumnMarkdownNode,
)
from notionary.blocks.divider import DividerMarkdownBlockParams, DividerMarkdownNode
from notionary.blocks.embed import EmbedMarkdownBlockParams, EmbedMarkdownNode
from notionary.blocks.equation import EquationMarkdownBlockParams, EquationMarkdownNode
from notionary.blocks.file import FileMarkdownNode, FileMarkdownNodeParams
from notionary.blocks.heading import HeadingMarkdownBlockParams, HeadingMarkdownNode
from notionary.blocks.image_block import ImageMarkdownBlockParams, ImageMarkdownNode
from notionary.blocks.numbered_list import (
    NumberedListMarkdownBlockParams,
    NumberedListMarkdownNode,
)
from notionary.blocks.paragraph import (
    ParagraphMarkdownBlockParams,
    ParagraphMarkdownNode,
)
from notionary.blocks.pdf import PdfMarkdownNode, PdfMarkdownNodeParams
from notionary.blocks.quote import QuoteMarkdownBlockParams, QuoteMarkdownNode
from notionary.blocks.table import TableMarkdownBlockParams, TableMarkdownNode
from notionary.blocks.table_of_contents import (
    TableOfContentsMarkdownBlockParams,
    TableOfContentsMarkdownNode,
)
from notionary.blocks.todo import TodoMarkdownBlockParams, TodoMarkdownNode
from notionary.blocks.toggle import ToggleMarkdownBlockParams, ToggleMarkdownNode
from notionary.blocks.toggleable_heading import (
    ToggleableHeadingMarkdownBlockParams,
    ToggleableHeadingMarkdownNode,
)
from notionary.blocks.types import BlockType, MarkdownBlockType
from notionary.blocks.video import VideoMarkdownBlockParams, VideoMarkdownNode
from notionary.markdown.markdown_document_model import (
    MarkdownBlock,
    MarkdownDocumentModel,
)
from notionary.markdown.markdown_node import MarkdownNode


class MarkdownBuilder:
    """
    Fluent interface builder for creating Notion content with clean, direct methods.
    """

    def __init__(self) -> None:
        self.children: list[MarkdownNode] = []

        self._block_processors: dict[str, Callable[[Any], None]] = {
            MarkdownBlockType.HEADING_1: self._add_heading,
            MarkdownBlockType.HEADING_2: self._add_heading,
            MarkdownBlockType.HEADING_3: self._add_heading,
            MarkdownBlockType.PARAGRAPH: self._add_paragraph,
            MarkdownBlockType.QUOTE: self._add_quote,
            MarkdownBlockType.BULLETED_LIST_ITEM: self._add_bulleted_list,
            MarkdownBlockType.NUMBERED_LIST_ITEM: self._add_numbered_list,
            MarkdownBlockType.TO_DO: self._add_todo,
            MarkdownBlockType.CALLOUT: self._add_callout,
            MarkdownBlockType.CODE: self._add_code,
            MarkdownBlockType.IMAGE: self._add_image,
            MarkdownBlockType.VIDEO: self._add_video,
            MarkdownBlockType.AUDIO: self._add_audio,
            MarkdownBlockType.FILE: self._add_file,
            MarkdownBlockType.PDF: self._add_pdf,
            MarkdownBlockType.BOOKMARK: self._add_bookmark,
            MarkdownBlockType.EMBED: self._add_embed,
            MarkdownBlockType.TABLE: self._add_table,
            MarkdownBlockType.DIVIDER: self._add_divider,
            MarkdownBlockType.EQUATION: self._add_equation,
            MarkdownBlockType.TABLE_OF_CONTENTS: self._add_table_of_contents,
            MarkdownBlockType.TOGGLE: self._add_toggle,
            MarkdownBlockType.COLUMN_LIST: self._add_columns,
            MarkdownBlockType.BREADCRUMB: self._add_breadcrumb,
            MarkdownBlockType.HEADING: self._add_heading,
            MarkdownBlockType.BULLETED_LIST: self._add_bulleted_list,
            MarkdownBlockType.NUMBERED_LIST: self._add_numbered_list,
            MarkdownBlockType.TODO: self._add_todo,
            MarkdownBlockType.TOGGLEABLE_HEADING: self._add_toggleable_heading,
            MarkdownBlockType.COLUMNS: self._add_columns,
            MarkdownBlockType.SPACE: self._add_space,
        }

    @classmethod
    def from_model(cls, model: MarkdownDocumentModel) -> Self:
        """Create MarkdownBuilder from a Pydantic model."""
        builder = cls()
        builder._process_blocks(model.blocks)
        return builder

    def h1(self, text: str) -> Self:
        """
        Add an H1 heading.

        Args:
            text: The heading text content
        """
        self.children.append(HeadingMarkdownNode(text=text, level=1))
        return self

    def h2(self, text: str) -> Self:
        """
        Add an H2 heading.

        Args:
            text: The heading text content
        """
        self.children.append(HeadingMarkdownNode(text=text, level=2))
        return self

    def h3(self, text: str) -> Self:
        """
        Add an H3 heading.

        Args:
            text: The heading text content
        """
        self.children.append(HeadingMarkdownNode(text=text, level=3))
        return self

    def heading(self, text: str, level: int = 2) -> Self:
        """
        Add a heading with specified level.

        Args:
            text: The heading text content
            level: Heading level (1-3), defaults to 2
        """
        self.children.append(HeadingMarkdownNode(text=text, level=level))
        return self

    def paragraph(self, text: str) -> Self:
        """
        Add a paragraph block.

        Args:
            text: The paragraph text content
        """
        self.children.append(ParagraphMarkdownNode(text=text))
        return self

    def text(self, content: str) -> Self:
        """
        Add a text paragraph (alias for paragraph).

        Args:
            content: The text content
        """
        return self.paragraph(content)

    def quote(self, text: str) -> Self:
        """
        Add a blockquote.

        Args:
            text: Quote text content
            author: Optional quote author/attribution
        """
        self.children.append(QuoteMarkdownNode(text=text))
        return self

    def divider(self) -> Self:
        """Add a horizontal divider."""
        self.children.append(DividerMarkdownNode())
        return self

    def numbered_list(self, items: list[str]) -> Self:
        """
        Add a numbered list.

        Args:
            items: List of text items for the numbered list
        """
        self.children.append(NumberedListMarkdownNode(texts=items))
        return self

    def bulleted_list(self, items: list[str]) -> Self:
        """
        Add a bulleted list.

        Args:
            items: List of text items for the bulleted list
        """
        self.children.append(BulletedListMarkdownNode(texts=items))
        return self

    def todo(self, text: str, checked: bool = False) -> Self:
        """
        Add a single todo item.

        Args:
            text: The todo item text
            checked: Whether the todo item is completed, defaults to False
        """
        self.children.append(TodoMarkdownNode(text=text, checked=checked))
        return self

    def todo_list(
        self, items: list[str], completed: Optional[list[bool]] = None
    ) -> Self:
        """
        Add multiple todo items.

        Args:
            items: List of todo item texts
            completed: List of completion states for each item, defaults to all False
        """
        if completed is None:
            completed = [False] * len(items)

        for i, item in enumerate(items):
            is_done = completed[i] if i < len(completed) else False
            self.children.append(TodoMarkdownNode(text=item, checked=is_done))
        return self

    def callout(self, text: str, emoji: Optional[str] = None) -> Self:
        """
        Add a callout block.

        Args:
            text: The callout text content
            emoji: Optional emoji for the callout icon
        """
        self.children.append(CalloutMarkdownNode(text=text, emoji=emoji))
        return self

    def toggle(
        self, title: str, builder_func: Callable[["MarkdownBuilder"], "MarkdownBuilder"]
    ) -> Self:
        """
        Add a toggle block with content built using the builder API.

        Args:
            title: The toggle title/header text
            builder_func: Function that receives a MarkdownBuilder and returns it configured

        Example:
            builder.toggle("Advanced Settings", lambda t:
                t.h3("Configuration")
                .paragraph("Settings description")
                .table(["Setting", "Value"], [["Debug", "True"]])
                .callout("Important note", "⚠️")
            )
        """
        toggle_builder = MarkdownBuilder()
        builder_func(toggle_builder)
        self.children.append(
            ToggleMarkdownNode(title=title, children=toggle_builder.children)
        )
        return self

    def toggleable_heading(
        self,
        text: str,
        level: int,
        builder_func: Callable[["MarkdownBuilder"], "MarkdownBuilder"],
    ) -> Self:
        """
        Add a toggleable heading with content built using the builder API.

        Args:
            text: The heading text content
            level: Heading level (1-3)
            builder_func: Function that receives a MarkdownBuilder and returns it configured

        Example:
            builder.toggleable_heading("Advanced Section", 2, lambda t:
                t.paragraph("Introduction to this section")
                .numbered_list(["Step 1", "Step 2", "Step 3"])
                .code("example_code()", "python")
                .table(["Feature", "Status"], [["API", "Ready"]])
            )
        """
        toggle_builder = MarkdownBuilder()
        builder_func(toggle_builder)
        self.children.append(
            ToggleableHeadingMarkdownNode(
                text=text, level=level, children=toggle_builder.children
            )
        )
        return self

    def image(
        self, url: str, caption: Optional[str] = None, alt: Optional[str] = None
    ) -> Self:
        """
        Add an image.

        Args:
            url: Image URL or file path
            caption: Optional image caption text
            alt: Optional alternative text for accessibility
        """
        self.children.append(ImageMarkdownNode(url=url, caption=caption, alt=alt))
        return self

    def video(self, url: str, caption: Optional[str] = None) -> Self:
        """
        Add a video.

        Args:
            url: Video URL or file path
            caption: Optional video caption text
        """
        self.children.append(VideoMarkdownNode(url=url, caption=caption))
        return self

    def audio(self, url: str, caption: Optional[str] = None) -> Self:
        """
        Add audio content.

        Args:
            url: Audio file URL or path
            caption: Optional audio caption text
        """
        self.children.append(AudioMarkdownNode(url=url, caption=caption))
        return self

    def file(self, url: str, caption: Optional[str] = None) -> Self:
        """
        Add a file.

        Args:
            url: File URL or path
            caption: Optional file caption text
        """
        self.children.append(FileMarkdownNode(url=url, caption=caption))
        return self

    def pdf(self, url: str, caption: Optional[str] = None) -> Self:
        """
        Add a PDF document.

        Args:
            url: PDF URL or file path
            caption: Optional PDF caption text
        """
        self.children.append(PdfMarkdownNode(url=url, caption=caption))
        return self

    def bookmark(
        self, url: str, title: Optional[str] = None, description: Optional[str] = None
    ) -> Self:
        """
        Add a bookmark.

        Args:
            url: Bookmark URL
            title: Optional bookmark title
            description: Optional bookmark description text
        """
        self.children.append(
            BookmarkMarkdownNode(url=url, title=title, description=description)
        )
        return self

    def embed(self, url: str, caption: Optional[str] = None) -> Self:
        """
        Add an embed.

        Args:
            url: URL to embed (e.g., YouTube, Twitter, etc.)
            caption: Optional embed caption text
        """
        self.children.append(EmbedMarkdownNode(url=url, caption=caption))
        return self

    def code(
        self, code: str, language: Optional[str] = None, caption: Optional[str] = None
    ) -> Self:
        """
        Add a code block.

        Args:
            code: The source code content
            language: Optional programming language for syntax highlighting
            caption: Optional code block caption text
        """
        self.children.append(
            CodeMarkdownNode(code=code, language=language, caption=caption)
        )
        return self

    def mermaid(self, diagram: str, caption: Optional[str] = None) -> Self:
        """
        Add a Mermaid diagram block.

        Args:
            diagram: The Mermaid diagram source code
            caption: Optional diagram caption text
        """
        self.children.append(
            CodeMarkdownNode(
                code=diagram, language=CodeLanguage.MERMAID.value, caption=caption
            )
        )
        return self

    def table(self, headers: list[str], rows: list[list[str]]) -> Self:
        """
        Add a table.

        Args:
            headers: List of column header texts
            rows: List of rows, where each row is a list of cell texts
        """
        self.children.append(TableMarkdownNode(headers=headers, rows=rows))
        return self

    def add_custom(self, node: MarkdownNode) -> Self:
        """
        Add a custom MarkdownNode.

        Args:
            node: A custom MarkdownNode instance
        """
        self.children.append(node)
        return self

    def breadcrumb(self) -> Self:
        """Add a breadcrumb navigation block."""
        self.children.append(BreadcrumbMarkdownNode())
        return self

    def equation(self, expression: str) -> Self:
        """
        Add a LaTeX equation block.

        Args:
            expression: LaTeX mathematical expression

        Example:
            builder.equation("E = mc^2")
            builder.equation("f(x) = \\sin(x) + \\cos(x)")
            builder.equation("x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}")
        """
        self.children.append(EquationMarkdownNode(expression=expression))
        return self

    def table_of_contents(self, color: Optional[str] = None) -> Self:
        """
        Add a table of contents.

        Args:
            color: Optional color for the table of contents (e.g., "blue", "blue_background")
        """
        self.children.append(TableOfContentsMarkdownNode(color=color))
        return self

    def columns(
        self,
        *builder_funcs: Callable[["MarkdownBuilder"], "MarkdownBuilder"],
        width_ratios: Optional[list[float]] = None,
    ) -> Self:
        """
        Add multiple columns in a layout.

        Args:
            *builder_funcs: Multiple functions, each building one column
            width_ratios: Optional list of width ratios (0.0 to 1.0).
                        If None, columns have equal width.
                        Length must match number of builder_funcs.

        Examples:
            # Equal width (original API unchanged):
            builder.columns(
                lambda col: col.h2("Left").paragraph("Left content"),
                lambda col: col.h2("Right").paragraph("Right content")
            )

            # Custom ratios:
            builder.columns(
                lambda col: col.h2("Main").paragraph("70% width"),
                lambda col: col.h2("Sidebar").paragraph("30% width"),
                width_ratios=[0.7, 0.3]
            )

            # Three columns with custom ratios:
            builder.columns(
                lambda col: col.h3("Nav").paragraph("Navigation"),
                lambda col: col.h2("Main").paragraph("Main content"),
                lambda col: col.h3("Ads").paragraph("Advertisement"),
                width_ratios=[0.2, 0.6, 0.2]
            )
        """
        if len(builder_funcs) < 2:
            raise ValueError("Column layout requires at least 2 columns")

        if width_ratios is not None:
            if len(width_ratios) != len(builder_funcs):
                raise ValueError(
                    f"width_ratios length ({len(width_ratios)}) must match number of columns ({len(builder_funcs)})"
                )

            ratio_sum = sum(width_ratios)
            if not (0.9 <= ratio_sum <= 1.1):  # Allow small floating point errors
                raise ValueError(f"width_ratios should sum to 1.0, got {ratio_sum}")

        # Create all columns
        columns = []
        for i, builder_func in enumerate(builder_funcs):
            width_ratio = width_ratios[i] if width_ratios else None

            col_builder = MarkdownBuilder()
            builder_func(col_builder)

            column_node = ColumnMarkdownNode(
                children=col_builder.children, width_ratio=width_ratio
            )
            columns.append(column_node)

        self.children.append(ColumnListMarkdownNode(columns=columns))
        return self

    def column_with_nodes(
        self, *nodes: MarkdownNode, width_ratio: Optional[float] = None
    ) -> Self:
        """
        Add a column with pre-built MarkdownNode objects.

        Args:
            *nodes: MarkdownNode objects to include in the column
            width_ratio: Optional width ratio (0.0 to 1.0)

        Examples:
            # Original API (unchanged):
            builder.column_with_nodes(
                HeadingMarkdownNode(text="Title", level=2),
                ParagraphMarkdownNode(text="Content")
            )

            # New API with ratio:
            builder.column_with_nodes(
                HeadingMarkdownNode(text="Sidebar", level=2),
                ParagraphMarkdownNode(text="Narrow content"),
                width_ratio=0.25
            )
        """
        from notionary.blocks.column.column_markdown_node import ColumnMarkdownNode

        column_node = ColumnMarkdownNode(children=list(nodes), width_ratio=width_ratio)
        self.children.append(column_node)
        return self

    def _column(
        self, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder]
    ) -> ColumnMarkdownNode:
        """
        Internal helper to create a single column.
        Use columns() instead for public API.
        """
        col_builder = MarkdownBuilder()
        builder_func(col_builder)
        return ColumnMarkdownNode(children=col_builder.children)

    def space(self) -> Self:
        """Add vertical spacing."""
        return self.paragraph("")

    def build(self) -> str:
        """Build and return the final markdown string."""
        return "\n\n".join(
            child.to_markdown() for child in self.children if child is not None
        )

    def _add_heading(self, params: HeadingMarkdownBlockParams) -> None:
        """Add a heading block."""
        self.children.append(HeadingMarkdownNode.from_params(params))

    def _add_paragraph(self, params: ParagraphMarkdownBlockParams) -> None:
        """Add a paragraph block."""
        self.children.append(ParagraphMarkdownNode.from_params(params))

    def _add_quote(self, params: QuoteMarkdownBlockParams) -> None:
        """Add a quote block."""
        self.children.append(QuoteMarkdownNode.from_params(params))

    def _add_bulleted_list(self, params: BulletedListMarkdownBlockParams) -> None:
        """Add a bulleted list block."""
        self.children.append(BulletedListMarkdownNode.from_params(params))

    def _add_numbered_list(self, params: NumberedListMarkdownBlockParams) -> None:
        """Add a numbered list block."""
        self.children.append(NumberedListMarkdownNode.from_params(params))

    def _add_todo(self, params: TodoMarkdownBlockParams) -> None:
        """Add a todo block."""
        self.children.append(TodoMarkdownNode.from_params(params))

    def _add_callout(self, params: CalloutMarkdownBlockParams) -> None:
        """Add a callout block."""
        self.children.append(CalloutMarkdownNode.from_params(params))

    def _add_code(self, params: CodeBlock) -> None:
        """Add a code block."""
        self.children.append(CodeMarkdownNode.from_params(params))

    def _add_image(self, params: ImageMarkdownBlockParams) -> None:
        """Add an image block."""
        self.children.append(ImageMarkdownNode.from_params(params))

    def _add_video(self, params: VideoMarkdownBlockParams) -> None:
        """Add a video block."""
        self.children.append(VideoMarkdownNode.from_params(params))

    def _add_audio(self, params: AudioMarkdownBlockParams) -> None:
        """Add an audio block."""
        self.children.append(AudioMarkdownNode.from_params(params))

    def _add_file(self, params: FileMarkdownNodeParams) -> None:
        """Add a file block."""
        self.children.append(FileMarkdownNode.from_params(params))

    def _add_pdf(self, params: PdfMarkdownNodeParams) -> None:
        """Add a PDF block."""
        self.children.append(PdfMarkdownNode.from_params(params))

    def _add_bookmark(self, params: BookmarkMarkdownBlockParams) -> None:
        """Add a bookmark block."""
        self.children.append(BookmarkMarkdownNode.from_params(params))

    def _add_embed(self, params: EmbedMarkdownBlockParams) -> None:
        """Add an embed block."""
        self.children.append(EmbedMarkdownNode.from_params(params))

    def _add_table(self, params: TableMarkdownBlockParams) -> None:
        """Add a table block."""
        self.children.append(TableMarkdownNode.from_params(params))

    def _add_divider(self, params: DividerMarkdownBlockParams) -> None:
        """Add a divider block."""
        self.children.append(DividerMarkdownNode.from_params(params))

    def _add_equation(self, params: EquationMarkdownBlockParams) -> None:
        """Add an equation block."""
        self.children.append(EquationMarkdownNode.from_params(params))

    def _add_table_of_contents(
        self, params: TableOfContentsMarkdownBlockParams
    ) -> None:
        """Add a table of contents block."""
        self.children.append(TableOfContentsMarkdownNode.from_params(params))

    def _add_toggle(self, params: ToggleMarkdownBlockParams) -> None:
        """Add a toggle block."""
        child_builder = MarkdownBuilder()
        child_builder._process_blocks(params.children)
        self.children.append(
            ToggleMarkdownNode(title=params.title, children=child_builder.children)
        )

    def _add_toggleable_heading(
        self, params: ToggleableHeadingMarkdownBlockParams
    ) -> None:
        """Add a toggleable heading block."""
        # Create nested builder for children
        child_builder = MarkdownBuilder()
        child_builder._process_blocks(params.children)
        self.children.append(
            ToggleableHeadingMarkdownNode(
                text=params.text, level=params.level, children=child_builder.children
            )
        )

    def _add_columns(self, params: ColumnListMarkdownBlockParams) -> None:
        """Add a columns block."""
        column_nodes = []

        for i, column_blocks in enumerate(params.columns):
            width_ratio = (
                params.width_ratios[i]
                if params.width_ratios and i < len(params.width_ratios)
                else None
            )

            col_builder = MarkdownBuilder()
            col_builder._process_blocks(column_blocks)

            # Erstelle ColumnMarkdownNode
            column_nodes.append(
                ColumnMarkdownNode(
                    children=col_builder.children, width_ratio=width_ratio
                )
            )

        self.children.append(ColumnListMarkdownNode(columns=column_nodes))

    def _add_breadcrumb(self, params) -> None:
        """Add a breadcrumb block."""
        self.children.append(BreadcrumbMarkdownNode())

    def _add_space(self, params) -> None:
        """Add a space block."""
        self.children.append(ParagraphMarkdownNode(text=""))

    def _process_blocks(self, blocks: list[MarkdownBlock]) -> None:
        """Process blocks using explicit mapping - type-safe and clear."""
        for block in blocks:
            processor = self._block_processors.get(block.type)
            if processor:
                processor(block.params)
            else:
                # More explicit error handling
                available_types = ", ".join(sorted(self._block_processors.keys()))
                raise ValueError(
                    f"Unsupported block type '{block.type}'. "
                    f"Available types: {available_types}"
                )
