from __future__ import annotations

from collections.abc import Callable
from typing import Self

from notionary.blocks.enums import CodingLanguage
from notionary.page.content.markdown.nodes import (
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
    ToggleMarkdownNode,
    VideoMarkdownNode,
)


class MarkdownBuilder:
    def __init__(self) -> None:
        self.children: list[MarkdownNode] = []

    def h1(self, text: str, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder] | None = None) -> Self:
        return self._add_heading(text, 1, builder_func)

    def h2(self, text: str, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder] | None = None) -> Self:
        return self._add_heading(text, 2, builder_func)

    def h3(self, text: str, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder] | None = None) -> Self:
        return self._add_heading(text, 3, builder_func)

    def paragraph(self, text: str) -> Self:
        self.children.append(ParagraphMarkdownNode(text=text))
        return self

    def space(self) -> Self:
        self.children.append(SpaceMarkdownNode())
        return self

    def quote(self, text: str, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder] | None = None) -> Self:
        children = self._build_children(builder_func)
        self.children.append(QuoteMarkdownNode(text=text, children=children))
        return self

    def divider(self) -> Self:
        self.children.append(DividerMarkdownNode())
        return self

    def numbered_list(self, items: list[str]) -> Self:
        self.children.append(NumberedListMarkdownNode(texts=items))
        return self

    def numbered_list_item(
        self, text: str, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder] | None = None
    ) -> Self:
        children = self._build_children(builder_func)
        child_nodes = [children] if children else None
        self.children.append(NumberedListMarkdownNode(texts=[text], children=child_nodes))
        return self

    def bulleted_list(self, items: list[str]) -> Self:
        self.children.append(BulletedListMarkdownNode(texts=items))
        return self

    def bulleted_list_item(
        self, text: str, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder] | None = None
    ) -> Self:
        children = self._build_children(builder_func)
        child_nodes = [children] if children else None
        self.children.append(BulletedListMarkdownNode(texts=[text], children=child_nodes))
        return self

    def todo(
        self,
        text: str,
        checked: bool = False,
        builder_func: Callable[[MarkdownBuilder], MarkdownBuilder] | None = None,
    ) -> Self:
        children = self._build_children(builder_func)
        self.children.append(TodoMarkdownNode(text=text, checked=checked, children=children))
        return self

    def checked_todo(self, text: str, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder] | None = None) -> Self:
        return self.todo(text, checked=True, builder_func=builder_func)

    def unchecked_todo(
        self, text: str, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder] | None = None
    ) -> Self:
        return self.todo(text, checked=False, builder_func=builder_func)

    def todo_list(self, items: list[str], completed: list[bool] | None = None) -> Self:
        completed = completed or [False] * len(items)
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
        children = self._build_children(builder_func)
        self.children.append(CalloutMarkdownNode(text=text, emoji=emoji, children=children))
        return self

    def toggle(self, title: str, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder]) -> Self:
        children = self._build_children(builder_func)
        self.children.append(ToggleMarkdownNode(title=title, children=children))
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

    def code(self, code: str, language: CodingLanguage | None = None, caption: str | None = None) -> Self:
        self.children.append(CodeMarkdownNode(code=code, language=language, caption=caption))
        return self

    def mermaid(self, diagram: str, caption: str | None = None) -> Self:
        self.children.append(CodeMarkdownNode(code=diagram, language=CodingLanguage.MERMAID.value, caption=caption))
        return self

    def table(self, headers: list[str], rows: list[list[str]]) -> Self:
        self.children.append(TableMarkdownNode(headers=headers, rows=rows))
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
        columns = self._build_columns(builder_funcs, width_ratios)
        self.children.append(ColumnListMarkdownNode(columns=columns))
        return self

    def build(self) -> str:
        return "\n\n".join(child.to_markdown() for child in self.children if child is not None)

    def _add_heading(
        self, text: str, level: int, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder] | None
    ) -> Self:
        children = self._build_children(builder_func)
        self.children.append(HeadingMarkdownNode(text=text, level=level, children=children))
        return self

    def _build_children(self, builder_func: Callable[[MarkdownBuilder], MarkdownBuilder] | None) -> list[MarkdownNode]:
        if builder_func is None:
            return []

        builder = MarkdownBuilder()
        builder_func(builder)
        return builder.children

    def _build_columns(
        self,
        builder_funcs: tuple[Callable[[MarkdownBuilder], MarkdownBuilder], ...],
        width_ratios: list[float] | None,
    ) -> list[ColumnMarkdownNode]:
        columns = []
        for i, builder_func in enumerate(builder_funcs):
            width_ratio = width_ratios[i] if width_ratios else None
            children = self._build_children(builder_func)
            columns.append(ColumnMarkdownNode(children=children, width_ratio=width_ratio))
        return columns
