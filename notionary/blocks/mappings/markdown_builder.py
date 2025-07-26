"""
# Complete Fluent Markdown Builder
==================================

Enhanced builder with support for all available MarkdownNode classes.
"""

from __future__ import annotations
from typing import Optional, Self, Union
from notionary.blocks.mappings.elements import (
    HeadingMarkdownBlock,
    ImageMarkdownBlock,
    ParagraphMarkdownBlock,
    AudioMarkdownBlock,
    BookmarkMarkdownBlock,
    CalloutMarkdownBlock,
    CodeMarkdownBlock,
    ColumnsMarkdownBlock,
    DividerMarkdownBlock,
    DocumentMarkdownBlock,
    EmbedMarkdownBlock,
    MentionMarkdownBlock,
    NumberedListMarkdownBlock,
    QuoteMarkdownBlock,
    TableMarkdownBlock,
    TodoMarkdownBlock,
    ToggleMarkdownBlock,
    ToggleableHeadingMarkdownBlock,
    VideoMarkdownBlock,
)
from notionary.blocks.mappings.markdown_node import MarkdownNode


class MarkdownBuilder:
    """
    Fluent interface builder for creating Notion content programmatically.
    Supports all available MarkdownNode types.
    """

    def __init__(self) -> None:
        self.children: list[MarkdownNode] = []

    # ========== BASIC CONTENT ==========

    def heading(self, text: str, level: int = 2) -> Self:
        """Add a heading block (H1-H3)."""
        self.children.append(HeadingMarkdownBlock(text=text, level=level))
        return self

    def paragraph(self, text: str) -> Self:
        """Add a paragraph block."""
        self.children.append(ParagraphMarkdownBlock(text=text))
        return self

    def quote(self, text: Union[str, list[str]]) -> Self:
        """Add a quote block."""
        self.children.append(QuoteMarkdownBlock(text=text))
        return self

    def divider(self) -> Self:
        """Add a divider block."""
        self.children.append(DividerMarkdownBlock())
        return self

    # ========== LISTS ==========

    def numbered_list_item(self, text: str, number: int = 1) -> Self:
        """Add a numbered list item."""
        self.children.append(NumberedListMarkdownBlock(text=text, number=number))
        return self

    def todo(self, text: str, checked: bool = False, marker: str = "-") -> Self:
        """Add a todo block."""
        self.children.append(
            TodoMarkdownBlock(text=text, checked=checked, marker=marker)
        )
        return self

    # ========== MEDIA ==========

    def audio(self, url: str, caption: Optional[str] = None) -> Self:
        """Add an audio block."""
        self.children.append(AudioMarkdownBlock(url=url, caption=caption))
        return self

    def image(
        self, url: str, caption: Optional[str] = None, alt: Optional[str] = None
    ) -> Self:
        """Add an image block."""
        self.children.append(ImageMarkdownBlock(url=url, caption=caption, alt=alt))
        return self

    def video(self, url: str, caption: Optional[str] = None) -> Self:
        """Add a video block."""
        self.children.append(VideoMarkdownBlock(url=url, caption=caption))
        return self

    def document(self, url: str, caption: Optional[str] = None) -> Self:
        """Add a document block."""
        self.children.append(DocumentMarkdownBlock(url=url, caption=caption))
        return self

    # ========== INTERACTIVE ==========

    def bookmark(
        self, url: str, title: Optional[str] = None, description: Optional[str] = None
    ) -> Self:
        """Add a bookmark block."""
        self.children.append(
            BookmarkMarkdownBlock(url=url, title=title, description=description)
        )
        return self

    def embed(self, url: str, caption: Optional[str] = None) -> Self:
        """Add an embed block."""
        self.children.append(EmbedMarkdownBlock(url=url, caption=caption))
        return self

    def callout(self, text: str, emoji: Optional[str] = None) -> Self:
        """Add a callout block."""
        self.children.append(CalloutMarkdownBlock(text=text, emoji=emoji))
        return self

    # ========== CODE ==========

    def code(
        self, code: str, language: Optional[str] = None, caption: Optional[str] = None
    ) -> Self:
        """Add a code block."""
        self.children.append(
            CodeMarkdownBlock(code=code, language=language, caption=caption)
        )
        return self

    # ========== ADVANCED ==========

    def toggle(self, title: str, content: Optional[list[str]] = None) -> Self:
        """Add a toggle block."""
        self.children.append(ToggleMarkdownBlock(title=title, content=content))
        return self

    def toggleable_heading(
        self, text: str, level: int = 1, content: Optional[list[str]] = None
    ) -> Self:
        """Add a toggleable heading block."""
        self.children.append(
            ToggleableHeadingMarkdownBlock(text=text, level=level, content=content)
        )
        return self

    def columns(self, columns: list[list[str]]) -> Self:
        """Add a columns layout."""
        self.children.append(ColumnsMarkdownBlock(columns=columns))
        return self

    def table(self, headers: list[str], rows: list[list[str]]) -> Self:
        """Add a table block."""
        self.children.append(TableMarkdownBlock(headers=headers, rows=rows))
        return self

    # ========== MENTIONS ==========

    def mention_page(self, page_id: str) -> Self:
        """Add a page mention."""
        self.children.append(MentionMarkdownBlock("page", page_id))
        return self

    def mention_database(self, database_id: str) -> Self:
        """Add a database mention."""
        self.children.append(MentionMarkdownBlock("database", database_id))
        return self

    def mention_date(self, date: str) -> Self:
        """Add a date mention (YYYY-MM-DD format)."""
        self.children.append(MentionMarkdownBlock("date", date))
        return self

    # ========== UTILITY ==========

    def add_custom(self, node: MarkdownNode) -> Self:
        """Add a custom MarkdownNode."""
        self.children.append(node)
        return self

    def add_text(self, text: str) -> Self:
        """Convenience method - alias for paragraph."""
        return self.paragraph(text)

    def add_space(self) -> Self:
        """Add some vertical space (empty paragraph)."""
        return self.paragraph("")

    # ========== BUILDER METHODS ==========

    def build(self) -> str:
        """Build and return the final markdown string."""
        return "\n\n".join(
            child.to_markdown() for child in self.children if child is not None
        )

    def to_markdown(self) -> str:
        """Alias for build() method."""
        return self.build()

    def clear(self) -> Self:
        """Clear all content and start fresh."""
        self.children.clear()
        return self

    def count(self) -> int:
        """Get the number of blocks in the builder."""
        return len(self.children)

    def preview(self, max_length: int = 200) -> str:
        """Get a preview of the generated markdown."""
        content = self.build()
        return content[:max_length] + "..." if len(content) > max_length else content
