import pytest

from notionary.page.content.markdown.builder import MarkdownBuilder


@pytest.fixture
def builder() -> MarkdownBuilder:
    return MarkdownBuilder()


def test_simple_document(builder: MarkdownBuilder):
    result = builder.h1("Welcome").paragraph("This is a test document.").space().divider().build()

    assert "# Welcome" in result
    assert "This is a test document." in result


def test_heading_with_nested_content(builder: MarkdownBuilder):
    result = builder.h2(
        "Features", lambda b: b.paragraph("Key features:").bulleted_list(["Fast", "Simple", "Reliable"])
    ).build()

    assert "## Features" in result
    assert "Key features:" in result
    assert "Fast" in result


def test_columns_with_content(builder: MarkdownBuilder):
    result = builder.columns(
        lambda col: col.h3("Left Column").paragraph("Left content"),
        lambda col: col.h3("Right Column").paragraph("Right content"),
    ).build()

    assert "::: columns" in result
    assert "::: column" in result
    assert "### Left Column" in result
    assert "### Right Column" in result
    assert "Left content" in result
    assert "Right content" in result


def test_columns_with_width_ratios(builder: MarkdownBuilder):
    result = builder.columns(
        lambda col: col.paragraph("Sidebar"), lambda col: col.paragraph("Main content"), width_ratios=[0.3, 0.7]
    ).build()

    assert "::: columns" in result
    assert "Sidebar" in result
    assert "Main content" in result
    assert "0.3" in result
    assert "0.7" in result


def test_three_column_layout(builder: MarkdownBuilder):
    result = builder.columns(
        lambda col: col.h3("Nav").paragraph("Navigation"),
        lambda col: col.h2("Content").paragraph("Main content area"),
        lambda col: col.h3("Ads").paragraph("Advertisements"),
        width_ratios=[0.2, 0.6, 0.2],
    ).build()

    assert "::: columns" in result
    assert "### Nav" in result
    assert "## Content" in result
    assert "### Ads" in result


def test_callout_with_nested_content(builder: MarkdownBuilder):
    result = builder.callout_with_children(
        "Important note",
        emoji="⚠️",
        builder_func=lambda b: b.paragraph("Please read carefully.").bulleted_list(["Point 1", "Point 2"]),
    ).build()

    assert "[callout]" in result
    assert "Important note" in result
    assert "⚠️" in result
    assert "Please read carefully." in result
    assert "Point 1" in result


def test_toggle_section(builder: MarkdownBuilder):
    result = builder.toggle(
        "Advanced Settings",
        lambda b: b.h3("Configuration").paragraph("Details here").code("config = true", language="javascript"),
    ).build()

    assert "+++ Advanced Settings" in result
    assert "### Configuration" in result
    assert "Details here" in result
    assert "```javascript" in result
    assert "config = true" in result


def test_toggleable_heading_with_content(builder: MarkdownBuilder):
    result = builder.toggleable_heading(
        "API Reference",
        2,
        lambda b: b.paragraph("API documentation").table(
            ["Method", "Description"], [["GET", "Fetch data"], ["POST", "Create data"]]
        ),
    ).build()

    assert "+++##" in result
    assert "API Reference" in result
    assert "API documentation" in result
    assert "| Method |" in result


def test_simple_numbered_list(builder: MarkdownBuilder):
    result = builder.numbered_list(["First", "Second", "Third"]).build()

    assert "1. First" in result
    assert "2. Second" in result
    assert "3. Third" in result


def test_simple_bulleted_list(builder: MarkdownBuilder):
    result = builder.bulleted_list(["Item 1", "Item 2", "Item 3"]).build()

    assert "- Item 1" in result
    assert "- Item 2" in result
    assert "- Item 3" in result


def test_quote_with_nested_content(builder: MarkdownBuilder):
    result = builder.quote(
        "Life is what happens", lambda b: b.paragraph("— John Lennon").space().paragraph("From 1980 interview")
    ).build()

    assert "> Life is what happens" in result
    assert "John Lennon" in result
    assert "From 1980 interview" in result


def test_simple_documentation_page(builder: MarkdownBuilder):
    result = (
        builder.breadcrumb()
        .h1("Project Documentation")
        .paragraph("Complete guide for developers")
        .space()
        .table_of_contents()
        .divider()
        .h2(
            "Getting Started",
            lambda b: b.paragraph("Follow these steps:").numbered_list(["Install dependencies", "Run application"]),
        )
        .callout_with_children(
            "Note", emoji="💡", builder_func=lambda b: b.paragraph("Make sure Python 3.9+ is installed")
        )
        .build()
    )

    assert "# Project Documentation" in result
    assert "Complete guide for developers" in result
    assert "[toc]" in result
    assert "## Getting Started" in result
    assert "Install dependencies" in result
    assert "[callout]" in result
    assert "💡" in result


def test_todo_with_nested_tasks(builder: MarkdownBuilder):
    result = (
        builder.checked_todo(
            "Complete Phase 1",
            lambda b: b.paragraph("Finished tasks:").bulleted_list(["Design", "Implementation", "Testing"]),
        )
        .unchecked_todo("Start Phase 2")
        .build()
    )

    assert "- Complete Phase 1" in result
    assert "Finished tasks:" in result
    assert "- [ ] Start Phase 2" in result


def test_media_rich_content(builder: MarkdownBuilder):
    result = (
        builder.h2("Gallery")
        .image("https://example.com/photo.jpg", caption="Project screenshot")
        .space()
        .video("https://example.com/demo.mp4", caption="Demo video")
        .divider()
        .pdf("https://example.com/manual.pdf", caption="User manual")
        .build()
    )

    assert "## Gallery" in result
    assert "[image]" in result
    assert "https://example.com/photo.jpg" in result
    assert "Project screenshot" in result
    assert "https://example.com/demo.mp4" in result


def test_deeply_nested_structure(builder: MarkdownBuilder):
    result = builder.h1(
        "Documentation",
        lambda b: b.callout_with_children(
            "Overview",
            emoji="📚",
            builder_func=lambda c: c.paragraph("Main sections:").toggle(
                "Chapter 1", lambda t: t.h3("Introduction").paragraph("Content here")
            ),
        ),
    ).build()

    assert "# Documentation" in result
    assert "[callout]" in result
    assert "📚" in result
    assert "+++ Chapter 1" in result
    assert "### Introduction" in result


def test_table_with_surrounding_content(builder: MarkdownBuilder):
    result = (
        builder.h2("API Endpoints")
        .paragraph("Available routes:")
        .table(
            ["Method", "Path", "Description"],
            [
                ["GET", "/users", "List all users"],
                ["POST", "/users", "Create user"],
                ["DELETE", "/users/:id", "Delete user"],
            ],
        )
        .paragraph("All endpoints require authentication.")
        .build()
    )

    assert "## API Endpoints" in result
    assert "| Method |" in result
    assert "| GET |" in result
    assert "/users" in result
    assert "All endpoints require authentication." in result


def test_code_blocks(builder: MarkdownBuilder):
    result = (
        builder.h3("Code Example")
        .code("print('hello world')", language="python", caption="Python example")
        .space()
        .mermaid("graph TD\n  A-->B", caption="Flow diagram")
        .build()
    )

    assert "### Code Example" in result
    assert "```python" in result
    assert "print('hello world')" in result
    assert "```mermaid" in result


def test_build_produces_string(builder: MarkdownBuilder):
    builder.h1("Title").paragraph("Content")

    result = builder.build()

    assert isinstance(result, str)
    assert len(result) > 0


def test_empty_builder_builds_empty_string(builder: MarkdownBuilder):
    result = builder.build()

    assert result == ""


def test_multiple_media_types(builder: MarkdownBuilder):
    result = (
        builder.image("img.png", caption="Image")
        .video("video.mp4")
        .audio("audio.mp3", caption="Audio")
        .pdf("doc.pdf")
        .file("file.zip")
        .build()
    )

    assert "[image]" in result
    assert "[video]" in result
    assert "[audio]" in result
    assert "[pdf]" in result
    assert "[file]" in result
