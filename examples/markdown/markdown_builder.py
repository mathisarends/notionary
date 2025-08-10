from notionary import MarkdownBuilder


def demo_comprehensive_builder():
    """Demonstrate all builder capabilities."""

    content = (
        MarkdownBuilder()
        # Basic content
        .heading(text="🚀 Complete Builder Demo", level=1)
        .paragraph(
            text="This demonstrates **all** available MarkdownNode types in one fluent interface."
        )
        .callout(text="This builder supports every type of Notion block!", emoji="✨")
        # Lists and tasks
        .heading(text="📋 Lists & Tasks", level=2)
        .numbered_list(
            items=["First numbered item", "Second numbered item", "Third numbered item"]
        )
        .bulleted_list(
            items=["First bullet point", "Second bullet point", "Third bullet point"]
        )
        .todo(text="Complete documentation", checked=True)
        .todo(text="Add more examples", checked=False)
        # Media content
        .heading(text="🎬 Media Content", level=2)
        .audio(url="https://example.com/audio.mp3", caption="Sample Audio File")
        .image(
            url="https://example.com/image.jpg", caption="Sample Image", alt="Alt text"
        )
        .video(url="https://youtube.com/watch?v=xyz", caption="Demo Video")
        .file(url="https://example.com/doc.pdf", caption="Important Document")
        # Interactive elements
        .heading(text="🔗 Interactive Elements", level=2)
        .bookmark(
            url="https://notion.so",
            title="Notion",
            description="The connected workspace",
        )
        .embed(url="https://codepen.io/example", caption="CodePen Example")
        # Code and technical
        .heading(text="💻 Code Examples", level=2)
        .code(
            code="print('Hello, World!')",
            language="python",
            caption="Basic Python example",
        )
        .code(code="SELECT * FROM users;", language="sql")
        # Structured content
        .heading(text="🏗️ Structured Content", level=2)
        .table(
            headers=["Name", "Type", "Description"],
            rows=[
                ["Audio", "Media", "Audio content block"],
                ["Video", "Media", "Video content block"],
                ["Table", "Layout", "Structured data display"],
            ],
        )
        # Collapsible content
        .heading(text="📁 Collapsible Content", level=2)
        .toggle(
            title="Click to expand", content=["Hidden content here", "More details..."]
        )
        .toggleable_heading(
            text="Collapsible Section",
            level=3,
            content=["Nested content", "Additional info"],
        )
        # Mentions and references
        .tid()
        .quote(
            text="The fluent interface pattern makes complex content creation simple and readable."
        )
        .paragraph(
            text="References: @date[2024-01-15] and @[page-id] mentions are supported."
        )
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
        .heading(text="Quick Demo")
        .paragraph(text="Just a quick example with **bold** text.")
        .audio(url="https://example.com/quick.mp3", caption="Quick Audio")
        .todo(text="Review this content")
        .callout(text="Done in just a few lines!", emoji="🎉")
        .build()
    )

    print("\nQuick content example:")
    print(quick_content)


def demo_list_variations():
    """Demonstrate different ways to create lists."""

    list_content = (
        MarkdownBuilder()
        .heading(text="🔢 List Variations Demo", level=2)
        # Multiple items at once
        .paragraph(text="**Method 1: Multiple items at once**")
        .numbered_list(items=["Setup environment", "Install dependencies", "Run tests"])
        .bulleted_list(items=["Feature A", "Feature B", "Feature C"])
        # Individual items
        .paragraph(text="**Method 2: Individual items**")
        .numbered_list(text="Single numbered item")
        .bulleted_list(text="Single bulleted item")
        .build()
    )

    print("\nList variations example:")
    print(list_content)


if __name__ == "__main__":
    demo_comprehensive_builder()
    demo_quick_content()
    demo_list_variations()
