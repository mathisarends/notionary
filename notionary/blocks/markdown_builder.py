"""
Clean Fluent Markdown Builder
============================

A direct, chainable builder for all MarkdownNode types without overengineering.
Maps 1:1 to the available blocks with clear, expressive method names.
"""

from __future__ import annotations
from typing import Optional, Self, Union

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
    MarkdownNode,
)


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

    def quote(self, text: str, author: Optional[str] = None) -> Self:
        """
        Add a blockquote.

        Args:
            text: Quote text content
            author: Optional quote author/attribution
        """
        self.children.append(QuoteMarkdownNode(text=text, author=author))
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

    def toggle(self, title: str, content: Optional[list[str]] = None) -> Self:
        """
        Add a toggle block.

        Args:
            title: The toggle title/header text
            content: Optional list of content items inside the toggle
        """
        self.children.append(ToggleMarkdownNode(title=title, content=content))
        return self

    def toggleable_heading(
        self, text: str, level: int = 2, content: Optional[list[str]] = None
    ) -> Self:
        """
        Add a toggleable heading.

        Args:
            text: The heading text content
            level: Heading level (1-3), defaults to 2
            content: Optional list of content items inside the toggleable heading
        """
        self.children.append(
            ToggleableHeadingMarkdownNode(text=text, level=level, content=content)
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

    def document(self, url: str, caption: Optional[str] = None) -> Self:
        """
        Add a document file.

        Args:
            url: Document file URL or path
            caption: Optional document caption text
        """
        self.children.append(DocumentMarkdownNode(url=url, caption=caption))
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

    def table(self, headers: list[str], rows: list[list[str]]) -> Self:
        """
        Add a table.

        Args:
            headers: List of column header texts
            rows: List of rows, where each row is a list of cell texts
        """
        self.children.append(TableMarkdownNode(headers=headers, rows=rows))
        return self

    def mention_page(self, page_id: str) -> Self:
        """
        Add a page mention.

        Args:
            page_id: The ID of the page to mention
        """
        self.children.append(MentionMarkdownNode("page", page_id))
        return self

    def mention_database(self, database_id: str) -> Self:
        """
        Add a database mention.

        Args:
            database_id: The ID of the database to mention
        """
        self.children.append(MentionMarkdownNode("database", database_id))
        return self

    def mention_date(self, date: str) -> Self:
        """
        Add a date mention.

        Args:
            date: Date in YYYY-MM-DD format
        """
        self.children.append(MentionMarkdownNode("date", date))
        return self

    def add_custom(self, node: MarkdownNode) -> Self:
        """
        Add a custom MarkdownNode.

        Args:
            node: A custom MarkdownNode instance
        """
        self.children.append(node)
        return self

    def space(self) -> Self:
        """Add vertical spacing."""
        return self.paragraph("")

    def build(self) -> str:
        """Build and return the final markdown string."""
        return "\n\n".join(
            child.to_markdown() for child in self.children if child is not None
        )
