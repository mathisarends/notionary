from notionary.blocks.mappings import MarkdownBuilder


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