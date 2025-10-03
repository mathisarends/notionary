from __future__ import annotations

from collections.abc import Callable
from typing import Self

from notionary.blocks.audio import AudioMarkdownNode
from notionary.blocks.bookmark import BookmarkMarkdownNode
from notionary.blocks.breadcrumbs import BreadcrumbMarkdownNode
from notionary.blocks.bulleted_list import BulletedListMarkdownNode
from notionary.blocks.callout import CalloutMarkdownNode
from notionary.blocks.code import CodeMarkdownNode
from notionary.blocks.column import ColumnListMarkdownNode, ColumnMarkdownNode
from notionary.blocks.divider import DividerMarkdownNode
from notionary.blocks.embed import EmbedMarkdownNode
from notionary.blocks.equation import EquationMarkdownNode
from notionary.blocks.file import FileMarkdownNode
from notionary.blocks.heading import HeadingMarkdownNode
from notionary.blocks.image_block import ImageMarkdownNode
from notionary.blocks.markdown.markdown_node import MarkdownNode
from notionary.blocks.numbered_list import NumberedListMarkdownNode
from notionary.blocks.paragraph import ParagraphMarkdownNode
from notionary.blocks.pdf import PdfMarkdownNode
from notionary.blocks.quote import QuoteMarkdownNode
from notionary.blocks.schemas import CodeLanguage
from notionary.blocks.space import SpaceMarkdownNode
from notionary.blocks.table import TableMarkdownNode
from notionary.blocks.table_of_contents import TableOfContentsMarkdownNode
from notionary.blocks.todo import TodoMarkdownNode
from notionary.blocks.toggle import ToggleMarkdownNode
from notionary.blocks.toggleable_heading import ToggleableHeadingMarkdownNode
from notionary.blocks.video import VideoMarkdownNode


class MarkdownBuilder:
    def __init__(self) -> None:
        self.children: list[MarkdownNode] = []

    def h1(self, text: str) -> Self:
        self.children.append(HeadingMarkdownNode(text=text, level=1))
        return self

    def h2(self, text: str) -> Self:
        self.children.append(HeadingMarkdownNode(text=text, level=2))
        return self

    def h3(self, text: str) -> Self:
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

    def space(self) -> Self:
        """
        Add a space block.

        """
        self.children.append(SpaceMarkdownNode())
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
        """
        self.children.append(QuoteMarkdownNode(text=text))
        return self

    def divider(self) -> Self:
        self.children.append(DividerMarkdownNode())
        return self

    def numbered_list(self, items: list[str]) -> Self:
        self.children.append(NumberedListMarkdownNode(texts=items))
        return self

    def bulleted_list(self, items: list[str]) -> Self:
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

    def todo_list(self, items: list[str], completed: list[bool] | None = None) -> Self:
        if completed is None:
            completed = [False] * len(items)

        for i, item in enumerate(items):
            is_done = completed[i] if i < len(completed) else False
            self.children.append(TodoMarkdownNode(text=item, checked=is_done))
        return self

    def callout(self, text: str, emoji: str | None = None) -> Self:
        """
        Add a callout block.

        Args:
            text: The callout text content
            emoji: Optional emoji for the callout icon
        """
        self.children.append(CalloutMarkdownNode(text=text, emoji=emoji))
        return self

    def toggle(self, title: str, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder]) -> Self:
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
        self.children.append(ToggleMarkdownNode(title=title, children=toggle_builder.children))
        return self

    def toggleable_heading(
        self,
        text: str,
        level: int,
        builder_func: Callable[[MarkdownBuilder], MarkdownBuilder],
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
        self.children.append(ToggleableHeadingMarkdownNode(text=text, level=level, children=toggle_builder.children))
        return self

    def image(self, url: str, caption: str | None = None, alt: str | None = None) -> Self:
        """
        Add an image.

        Args:
            url: Image URL or file path
            caption: Optional image caption text
            alt: Optional alternative text for accessibility
        """
        self.children.append(ImageMarkdownNode(url=url, caption=caption, alt=alt))
        return self

    def video(self, url: str, caption: str | None = None) -> Self:
        """
        Add a video.

        Args:
            url: Video URL or file path
            caption: Optional video caption text
        """
        self.children.append(VideoMarkdownNode(url=url, caption=caption))
        return self

    def audio(self, url: str, caption: str | None = None) -> Self:
        """
        Add audio content.

        Args:
            url: Audio file URL or path
            caption: Optional audio caption text
        """
        self.children.append(AudioMarkdownNode(url=url, caption=caption))
        return self

    def file(self, url: str, caption: str | None = None) -> Self:
        """
        Add a file.

        Args:
            url: File URL or path
            caption: Optional file caption text
        """
        self.children.append(FileMarkdownNode(url=url, caption=caption))
        return self

    def pdf(self, url: str, caption: str | None = None) -> Self:
        """
        Add a PDF document.

        Args:
            url: PDF URL or file path
            caption: Optional PDF caption text
        """
        self.children.append(PdfMarkdownNode(url=url, caption=caption))
        return self

    def bookmark(self, url: str, title: str | None = None, caption: str | None = None) -> Self:
        """
        Add a bookmark.

        Args:
            url: Bookmark URL
            title: Optional bookmark title
            description: Optional bookmark description text
        """
        self.children.append(BookmarkMarkdownNode(url=url, title=title, caption=caption))
        return self

    def embed(self, url: str, caption: str | None = None) -> Self:
        """
        Add an embed.

        Args:
            url: URL to embed (e.g., YouTube, Twitter, etc.)
            caption: Optional embed caption text
        """
        self.children.append(EmbedMarkdownNode(url=url, caption=caption))
        return self

    def code(self, code: str, language: str | None = None, caption: str | None = None) -> Self:
        """
        Add a code block.

        Args:
            code: The source code content
            language: Optional programming language for syntax highlighting
            caption: Optional code block caption text
        """
        self.children.append(CodeMarkdownNode(code=code, language=language, caption=caption))
        return self

    def mermaid(self, diagram: str, caption: str | None = None) -> Self:
        """
        Add a Mermaid diagram block.

        Args:
            diagram: The Mermaid diagram source code
            caption: Optional diagram caption text
        """
        self.children.append(CodeMarkdownNode(code=diagram, language=CodeLanguage.MERMAID.value, caption=caption))
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

    def table_of_contents(self, color: str | None = None) -> Self:
        """
        Add a table of contents.

        Args:
            color: Optional color for the table of contents (e.g., "blue", "blue_background")
        """
        self.children.append(TableOfContentsMarkdownNode(color=color))
        return self

    def columns(
        self,
        *builder_funcs: Callable[[MarkdownBuilder], MarkdownBuilder],
        width_ratios: list[float] | None = None,
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

            column_node = ColumnMarkdownNode(children=col_builder.children, width_ratio=width_ratio)
            columns.append(column_node)

        self.children.append(ColumnListMarkdownNode(columns=columns))
        return self

    def column_with_nodes(self, *nodes: MarkdownNode, width_ratio: float | None = None) -> Self:
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

    def _column(self, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder]) -> ColumnMarkdownNode:
        """
        Internal helper to create a single column.
        Use columns() instead for public API.
        """
        col_builder = MarkdownBuilder()
        builder_func(col_builder)
        return ColumnMarkdownNode(children=col_builder.children)

    def build(self) -> str:
        """Build and return the final markdown string."""
        return "\n\n".join(child.to_markdown() for child in self.children if child is not None)
