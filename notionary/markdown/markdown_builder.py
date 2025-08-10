"""
Clean Fluent Markdown Builder
============================

A direct, chainable builder for all MarkdownNode types without overengineering.
Maps 1:1 to the available blocks with clear, expressive method names.
"""

from __future__ import annotations
from typing import Callable, Optional, Self

from notionary.blocks.audio.audio_markdown_node import AudioMarkdownNode
from notionary.blocks.bookmark.bookmark_markdown_node import BookmarkMarkdownNode
from notionary.blocks.breadcrumbs.breadcrumb_markdown_node import BreadcrumbMarkdownNode
from notionary.blocks.bulleted_list.bulleted_list_markdown_node import (
    BulletedListMarkdownNode,
)
from notionary.blocks.callout.callout_markdown_node import CalloutMarkdownNode
from notionary.blocks.code.code_markdown_node import CodeMarkdownNode
from notionary.blocks.code.code_models import CodeLanguage
from notionary.blocks.column.column_list_markdown_node import ColumnListMarkdownNode
from notionary.blocks.column.column_markdown_node import ColumnMarkdownNode
from notionary.blocks.divider.divider_markdown_node import DividerMarkdownNode
from notionary.blocks.embed.embed_markdown_node import EmbedMarkdownNode
from notionary.blocks.equation.equation_element_markdown_node import (
    EquationMarkdownNode,
)
from notionary.blocks.file.file_element_markdown_node import FileMarkdownNode
from notionary.blocks.heading.heading_markdown_node import HeadingMarkdownNode
from notionary.blocks.image_block.image_markdown_node import ImageMarkdownNode
from notionary.blocks.numbered_list.numbered_list_markdown_node import (
    NumberedListMarkdownNode,
)
from notionary.blocks.paragraph.paragraph_markdown_node import ParagraphMarkdownNode
from notionary.blocks.quote.quote_markdown_node import QuoteMarkdownNode
from notionary.blocks.table.table_markdown_node import TableMarkdownNode
from notionary.blocks.table_of_contents.table_of_contents_markdown_node import (
    TableOfContentsMarkdownNode,
)
from notionary.blocks.todo.todo_markdown_node import TodoMarkdownNode
from notionary.blocks.toggle.toggle_markdown_node import ToggleMarkdownNode
from notionary.blocks.toggleable_heading.toggleable_heading_markdown_node import (
    ToggleableHeadingMarkdownNode,
)
from notionary.blocks.video.video_markdown_node import VideoMarkdownNode
from notionary.markdown.markdown_node import MarkdownNode


class MarkdownBuilder:
    """
    Fluent interface builder for creating Notion content with clean, direct methods.
    """

    def __init__(self) -> None:
        self.children: list[MarkdownNode] = []

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
                code=diagram, language=CodeLanguage.MERMAID, caption=caption
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

    def build(self) -> str:
        """Build and return the final markdown string."""
        return "\n\n".join(
            child.to_markdown() for child in self.children if child is not None
        )

    def space(self) -> Self:
        """Add vertical spacing."""
        return self.paragraph("")
