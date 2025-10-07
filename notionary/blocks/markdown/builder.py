from __future__ import annotations

from collections.abc import Callable
from typing import Self

from notionary.blocks.enums import CodeLanguage
from notionary.blocks.markdown.nodes import (
    AudioMarkdownNode,
    BookmarkMarkdownNode,
    BreadcrumbMarkdownNode,
    BulletedListMarkdownNode,
    CalloutMarkdownNode,
    CodeMarkdownNode,
    ColumnListMarkdownNode,
    ColumnMarkdownNode,
    DividerMarkdownNode,
    EmbedMarkdownNode,
    EquationMarkdownNode,
    FileMarkdownNode,
    HeadingMarkdownNode,
    ImageMarkdownNode,
    MarkdownNode,
    NumberedListMarkdownNode,
    ParagraphMarkdownNode,
    PdfMarkdownNode,
    QuoteMarkdownNode,
    SpaceMarkdownNode,
    TableMarkdownNode,
    TableOfContentsMarkdownNode,
    TodoMarkdownNode,
    ToggleableHeadingMarkdownNode,
    ToggleMarkdownNode,
    VideoMarkdownNode,
)


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

    def paragraph(self, text: str) -> Self:
        self.children.append(ParagraphMarkdownNode(text=text))
        return self

    def space(self) -> Self:
        self.children.append(SpaceMarkdownNode())
        return self

    def quote(self, text: str) -> Self:
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
        self.children.append(TodoMarkdownNode(text=text, checked=checked))
        return self

    def checked_todo(self, text: str) -> Self:
        return self.todo(text, checked=True)

    def unchecked_todo(self, text: str) -> Self:
        return self.todo(text, checked=False)

    def todo_list(self, items: list[str], completed: list[bool] | None = None) -> Self:
        if completed is None:
            completed = [False] * len(items)

        for i, item in enumerate(items):
            is_done = completed[i] if i < len(completed) else False
            self.children.append(TodoMarkdownNode(text=item, checked=is_done))
        return self

    def callout(self, text: str, emoji: str | None = None) -> Self:
        self.children.append(CalloutMarkdownNode(text=text, emoji=emoji))
        return self

    def callout_with_children(
        self,
        text: str,
        emoji: str | None = None,
        builder_func: Callable[[MarkdownBuilder], MarkdownBuilder] | None = None,
    ) -> Self:
        """
        Add a callout block with children built using the builder API.

        Args:
            text: The callout text content
            emoji: Optional emoji for the callout icon
            builder_func: Optional function that receives a MarkdownBuilder and returns it configured

        Example:
            builder.callout_with_children("Important note", "⚠️", lambda c:
                c.paragraph("Additional details here")
                .bulleted_list(["Point 1", "Point 2"])
            )
        """
        if builder_func is None:
            self.children.append(CalloutMarkdownNode(text=text, emoji=emoji))
            return self

        callout_builder = MarkdownBuilder()
        builder_func(callout_builder)
        self.children.append(CalloutMarkdownNode(text=text, emoji=emoji, children=callout_builder.children))
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

    def image(self, url: str, caption: str | None = None) -> Self:
        self.children.append(ImageMarkdownNode(url=url, caption=caption))
        return self

    def video(self, url: str, caption: str | None = None) -> Self:
        self.children.append(VideoMarkdownNode(url=url, caption=caption))
        return self

    def audio(self, url: str, caption: str | None = None) -> Self:
        self.children.append(AudioMarkdownNode(url=url, caption=caption))
        return self

    def file(self, url: str, caption: str | None = None) -> Self:
        self.children.append(FileMarkdownNode(url=url, caption=caption))
        return self

    def pdf(self, url: str, caption: str | None = None) -> Self:
        self.children.append(PdfMarkdownNode(url=url, caption=caption))
        return self

    def bookmark(self, url: str, title: str | None = None, caption: str | None = None) -> Self:
        self.children.append(BookmarkMarkdownNode(url=url, title=title, caption=caption))
        return self

    def embed(self, url: str, caption: str | None = None) -> Self:
        self.children.append(EmbedMarkdownNode(url=url, caption=caption))
        return self

    def code(self, code: str, language: CodeLanguage | None = None, caption: str | None = None) -> Self:
        self.children.append(CodeMarkdownNode(code=code, language=language, caption=caption))
        return self

    def mermaid(self, diagram: str, caption: str | None = None) -> Self:
        self.children.append(CodeMarkdownNode(code=diagram, language=CodeLanguage.MERMAID.value, caption=caption))
        return self

    def table(self, headers: list[str], rows: list[list[str]]) -> Self:
        self.children.append(TableMarkdownNode(headers=headers, rows=rows))
        return self

    def add_custom(self, node: MarkdownNode) -> Self:
        self.children.append(node)
        return self

    def breadcrumb(self) -> Self:
        self.children.append(BreadcrumbMarkdownNode())
        return self

    def equation(self, expression: str) -> Self:
        self.children.append(EquationMarkdownNode(expression=expression))
        return self

    def table_of_contents(self) -> Self:
        self.children.append(TableOfContentsMarkdownNode())
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
        self._validate_columns_args(builder_funcs, width_ratios)

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

    def _validate_columns_args(
        self,
        builder_funcs: tuple[Callable[[MarkdownBuilder], MarkdownBuilder], ...],
        width_ratios: list[float] | None,
    ) -> None:
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

    def build(self) -> str:
        return "\n\n".join(child.to_markdown() for child in self.children if child is not None)
