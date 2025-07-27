"""
# Complete Fluent Markdown Builder
==================================

Enhanced builder with support for all available MarkdownNode classes.
"""

from __future__ import annotations
from typing import Optional, Self
from notionary.blocks import (
    HeadingMarkdownNode,
    ImageMarkdownNode,
    ParagraphMarkdownNode,
    AudioMarkdownNode,
    BookmarkMarkdownNode,
    CalloutMarkdownNode,
    CodeMarkdownNode,
    DividerMarkdownNode,
    DocumentMarkdownNode,
    EmbedMarkdownNode,
    MentionMarkdownNode,
    NumberedListMarkdownNode,
    BulletedListMarkdownNode,
    QuoteMarkdownNode,
    TableMarkdownNode,
    TodoMarkdownNode,
    ToggleMarkdownNode,
    ToggleableHeadingMarkdownNode,
    VideoMarkdownNode,
)
from notionary.blocks.markdown_node import MarkdownNode


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
        self.children.append(HeadingMarkdownNode(text=text, level=level))
        return self

    def paragraph(self, text: str) -> Self:
        """Add a paragraph block."""
        self.children.append(ParagraphMarkdownNode(text=text))
        return self

    def quote(self, text: str, author: Optional[str] = None) -> Self:
        """Add a quote block."""
        self.children.append(QuoteMarkdownNode(text=text, author=author))
        return self

    def divider(self) -> Self:
        """Add a divider block."""
        self.children.append(DividerMarkdownNode())
        return self

    # ========== LISTS ==========

    def numbered_list(self, items: list[str]) -> Self:
        """Add a numbered list with multiple items."""
        self.children.append(NumberedListMarkdownNode(texts=items))
        return self

    def numbered_list_item(self, text: str) -> Self:
        """Add a single numbered list item (creates a list with one item)."""
        self.children.append(NumberedListMarkdownNode(texts=[text]))
        return self

    def bulleted_list(self, items: list[str]) -> Self:
        """Add a bulleted list with multiple items."""
        self.children.append(BulletedListMarkdownNode(texts=items))
        return self

    def bulleted_list_item(self, text: str) -> Self:
        """Add a single bulleted list item (creates a list with one item)."""
        self.children.append(BulletedListMarkdownNode(texts=[text]))
        return self

    def todo(self, text: str, checked: bool = False, marker: str = "-") -> Self:
        """Add a todo block."""
        self.children.append(
            TodoMarkdownNode(text=text, checked=checked, marker=marker)
        )
        return self

    # ========== MEDIA ==========

    def audio(self, url: str, caption: Optional[str] = None) -> Self:
        """Add an audio block."""
        self.children.append(AudioMarkdownNode(url=url, caption=caption))
        return self

    def image(self, url: str, caption: Optional[str] = None) -> Self:
        """Add an image block."""
        self.children.append(ImageMarkdownNode(url=url, caption=caption))
        return self

    def video(self, url: str, caption: Optional[str] = None) -> Self:
        """Add a video block."""
        self.children.append(VideoMarkdownNode(url=url, caption=caption))
        return self

    def document(self, url: str, caption: Optional[str] = None) -> Self:
        """Add a document block."""
        self.children.append(DocumentMarkdownNode(url=url, caption=caption))
        return self

    # ========== INTERACTIVE ==========

    def bookmark(
        self, url: str, title: Optional[str] = None, description: Optional[str] = None
    ) -> Self:
        """Add a bookmark block."""
        self.children.append(
            BookmarkMarkdownNode(url=url, title=title, description=description)
        )
        return self

    def embed(self, url: str, caption: Optional[str] = None) -> Self:
        """Add an embed block."""
        self.children.append(EmbedMarkdownNode(url=url, caption=caption))
        return self

    def callout(self, text: str, emoji: Optional[str] = None) -> Self:
        """Add a callout block."""
        self.children.append(CalloutMarkdownNode(text=text, emoji=emoji))
        return self

    # ========== CODE ==========

    def code(
        self, code: str, language: Optional[str] = None, caption: Optional[str] = None
    ) -> Self:
        """Add a code block."""
        self.children.append(
            CodeMarkdownNode(code=code, language=language, caption=caption)
        )
        return self

    # ========== ADVANCED ==========

    def toggle(self, title: str, content: Optional[list[str]] = None) -> Self:
        """Add a toggle block."""
        self.children.append(ToggleMarkdownNode(title=title, content=content))
        return self

    def toggleable_heading(
        self, text: str, level: int = 1, content: Optional[list[str]] = None
    ) -> Self:
        """Add a toggleable heading block."""
        self.children.append(
            ToggleableHeadingMarkdownNode(text=text, level=level, content=content)
        )
        return self

    def table(self, headers: list[str], rows: list[list[str]]) -> Self:
        """Add a table block."""
        self.children.append(TableMarkdownNode(headers=headers, rows=rows))
        return self

    # ========== MENTIONS ==========

    def mention_page(self, page_id: str) -> Self:
        """Add a page mention."""
        self.children.append(MentionMarkdownNode("page", page_id))
        return self

    def mention_database(self, database_id: str) -> Self:
        """Add a database mention."""
        self.children.append(MentionMarkdownNode("database", database_id))
        return self

    def mention_date(self, date: str) -> Self:
        """Add a date mention (YYYY-MM-DD format)."""
        self.children.append(MentionMarkdownNode("date", date))
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

    def add_numbered_items(self, *items: str) -> Self:
        """Add multiple numbered list items as separate single-item lists."""
        for item in items:
            self.numbered_list_item(item)
        return self

    def add_bulleted_items(self, *items: str) -> Self:
        """Add multiple bulleted list items as separate single-item lists."""
        for item in items:
            self.bulleted_list_item(item)
        return self
