"""
# Complete Fluent Markdown Builder
==================================

Enhanced builder with support for all available MarkdownNode classes.
"""

from __future__ import annotations
from typing import Optional, Self, List, Union
from notionary.blocks.mappings import (
    MarkdownNode,
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


class MarkdownBuilder:
    """
    Fluent interface builder for creating Notion content programmatically.
    Supports all available MarkdownNode types.
    """

    def __init__(self) -> None:
        self.children: List[MarkdownNode] = []

    # ========== BASIC CONTENT ==========
    
    def heading(self, text: str, level: int = 2) -> Self:
        """Add a heading block (H1-H3)."""
        self.children.append(HeadingMarkdownBlock(text=text, level=level))
        return self

    def paragraph(self, text: str) -> Self:
        """Add a paragraph block."""
        self.children.append(ParagraphMarkdownBlock(text=text))
        return self

    def quote(self, text: Union[str, List[str]]) -> Self:
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
        self.children.append(TodoMarkdownBlock(text=text, checked=checked, marker=marker))
        return self

    # ========== MEDIA ==========

    def audio(self, url: str, caption: Optional[str] = None) -> Self:
        """Add an audio block."""
        self.children.append(AudioMarkdownBlock(url=url, caption=caption))
        return self

    def image(self, url: str, caption: Optional[str] = None, alt: Optional[str] = None) -> Self:
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

    def bookmark(self, url: str, title: Optional[str] = None, description: Optional[str] = None) -> Self:
        """Add a bookmark block."""
        self.children.append(BookmarkMarkdownBlock(url=url, title=title, description=description))
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

    def code(self, code: str, language: Optional[str] = None, caption: Optional[str] = None) -> Self:
        """Add a code block."""
        self.children.append(CodeMarkdownBlock(code=code, language=language, caption=caption))
        return self

    # ========== ADVANCED ==========

    def toggle(self, title: str, content: Optional[List[str]] = None) -> Self:
        """Add a toggle block."""
        self.children.append(ToggleMarkdownBlock(title=title, content=content))
        return self

    def toggleable_heading(self, text: str, level: int = 1, content: Optional[List[str]] = None) -> Self:
        """Add a toggleable heading block."""
        self.children.append(ToggleableHeadingMarkdownBlock(text=text, level=level, content=content))
        return self

    def columns(self, columns: List[List[str]]) -> Self:
        """Add a columns layout."""
        self.children.append(ColumnsMarkdownBlock(columns=columns))
        return self

    def table(self, headers: List[str], rows: List[List[str]]) -> Self:
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


def demo_comprehensive_builder():
    """Demonstrate all builder capabilities."""
    
    content = (
        MarkdownBuilder()
        
        # Basic content
        .heading("🚀 Complete Builder Demo", level=1)
        .paragraph("This demonstrates **all** available MarkdownNode types in one fluent interface.")
        .callout("This builder supports every type of Notion block!", "✨")
        
        # Lists and tasks
        .heading("📋 Lists & Tasks", level=2)
        .numbered_list_item("First numbered item", 1)
        .numbered_list_item("Second numbered item", 2)
        .todo("Complete documentation", checked=True)
        .todo("Add more examples", checked=False)
        
        # Media content
        .heading("🎬 Media Content", level=2)
        .audio("https://example.com/audio.mp3", "Sample Audio File")
        .image("https://example.com/image.jpg", "Sample Image", "Alt text")
        .video("https://youtube.com/watch?v=xyz", "Demo Video")
        .document("https://example.com/doc.pdf", "Important Document")
        
        # Interactive elements
        .heading("🔗 Interactive Elements", level=2)
        .bookmark("https://notion.so", "Notion", "The connected workspace")
        .embed("https://codepen.io/example", "CodePen Example")
        
        # Code and technical
        .heading("💻 Code Examples", level=2)
        .code("print('Hello, World!')", "python", "Basic Python example")
        .code("SELECT * FROM users;", "sql")
        
        # Advanced layouts
        .heading("🏗️ Advanced Layouts", level=2)
        .columns([
            ["## Left Column", "Content for left side"],
            ["## Right Column", "Content for right side"]
        ])
        .table(
            headers=["Name", "Type", "Description"],
            rows=[
                ["Audio", "Media", "Audio content block"],
                ["Video", "Media", "Video content block"],
                ["Table", "Layout", "Structured data display"]
            ]
        )
        
        # Collapsible content
        .heading("📁 Collapsible Content", level=2)
        .toggle("Click to expand", ["Hidden content here", "More details..."])
        .toggleable_heading("Collapsible Section", 3, ["Nested content", "Additional info"])
        
        # Mentions and references
        .divider()
        .quote("The fluent interface pattern makes complex content creation simple and readable.")
        .paragraph("References: @date[2024-01-15] and @[page-id] mentions are supported.")
        
        .build()
    )
    
    print("Generated comprehensive content:")
    print("=" * 50)
    print(content[:500] + "..." if len(content) > 500 else content)
    print("=" * 50)
    print(f"Total content length: {len(content)} characters")


def demo_quick_content():
    """Quick content creation example."""
    
    quick_content = (
        MarkdownBuilder()
        .heading("Quick Demo")
        .paragraph("Just a quick example with **bold** text.")
        .audio("https://example.com/quick.mp3", "Quick Audio")
        .todo("Review this content")
        .callout("Done in just a few lines!", "🎉")
        .build()
    )
    
    print("\nQuick content example:")
    print(quick_content)


if __name__ == "__main__":
    demo_comprehensive_builder()
    demo_quick_content()