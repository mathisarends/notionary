import pytest

from notionary.blocks.enums import CodingLanguage
from notionary.page.content.markdown.builder import MarkdownBuilder
from notionary.page.content.markdown.structured_output import (
    AudioSchema,
    BookmarkSchema,
    BreadcrumbSchema,
    BulletedListItemSchema,
    BulletedListSchema,
    CalloutSchema,
    CodeSchema,
    ColumnSchema,
    ColumnsSchema,
    DividerSchema,
    EmbedSchema,
    EquationSchema,
    FileSchema,
    Heading1Schema,
    Heading2Schema,
    Heading3Schema,
    ImageSchema,
    MarkdownDocumentSchema,
    MermaidSchema,
    NumberedListItemSchema,
    NumberedListSchema,
    ParagraphSchema,
    PdfSchema,
    QuoteSchema,
    SpaceSchema,
    StructuredOutputMarkdownConverter,
    TableOfContentsSchema,
    TableSchema,
    TodoListSchema,
    TodoSchema,
    ToggleSchema,
    VideoSchema,
)


@pytest.fixture
def converter():
    return StructuredOutputMarkdownConverter()


def test_initialization_with_default_builder():
    converter = StructuredOutputMarkdownConverter()
    assert converter.builder is not None
    assert isinstance(converter.builder, MarkdownBuilder)


def test_initialization_with_custom_builder():
    custom_builder = MarkdownBuilder()
    converter = StructuredOutputMarkdownConverter(builder=custom_builder)
    assert converter.builder is custom_builder


def test_convert_empty_document(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(nodes=[])
    result = converter.convert(schema)
    assert result == ""


def test_convert_paragraph(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(nodes=[ParagraphSchema(text="Test paragraph")])
    result = converter.convert(schema)
    assert "Test paragraph" in result


def test_convert_heading_level_1(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(nodes=[Heading1Schema(text="Heading 1")])
    result = converter.convert(schema)
    assert "# Heading 1" in result


def test_convert_heading_level_2(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(nodes=[Heading2Schema(text="Heading 2")])
    result = converter.convert(schema)
    assert "## Heading 2" in result


def test_convert_heading_level_3(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(nodes=[Heading3Schema(text="Heading 3")])
    result = converter.convert(schema)
    assert "### Heading 3" in result


def test_convert_heading_with_children(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            Heading1Schema(
                text="Parent", children=[ParagraphSchema(text="Child content")]
            )
        ]
    )
    result = converter.convert(schema)
    assert "# Parent" in result
    assert "Child content" in result


def test_convert_space(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            ParagraphSchema(text="Before"),
            SpaceSchema(),
            ParagraphSchema(text="After"),
        ]
    )
    result = converter.convert(schema)
    assert "Before" in result
    assert "After" in result


def test_convert_divider(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(nodes=[DividerSchema()])
    result = converter.convert(schema)
    assert "---" in result


def test_convert_quote(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(nodes=[QuoteSchema(text="Quote text")])
    result = converter.convert(schema)
    assert "> Quote text" in result


def test_convert_quote_with_children(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[QuoteSchema(text="Quote", children=[ParagraphSchema(text="Nested")])]
    )
    result = converter.convert(schema)
    assert "> Quote" in result
    assert "Nested" in result


def test_convert_bulleted_list(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            BulletedListSchema(
                items=[
                    BulletedListItemSchema(text="Item 1"),
                    BulletedListItemSchema(text="Item 2"),
                    BulletedListItemSchema(text="Item 3"),
                ]
            )
        ]
    )
    result = converter.convert(schema)
    assert "- Item 1" in result
    assert "- Item 2" in result
    assert "- Item 3" in result


def test_convert_bulleted_list_item(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(nodes=[BulletedListItemSchema(text="Single item")])
    result = converter.convert(schema)
    assert "- Single item" in result


def test_convert_bulleted_list_item_with_children(
    converter: StructuredOutputMarkdownConverter,
):
    schema = MarkdownDocumentSchema(
        nodes=[
            BulletedListItemSchema(
                text="Parent item", children=[ParagraphSchema(text="Nested content")]
            )
        ]
    )
    result = converter.convert(schema)
    assert "- Parent item" in result
    assert "Nested content" in result


def test_convert_numbered_list(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            NumberedListSchema(
                items=[
                    NumberedListItemSchema(text="First"),
                    NumberedListItemSchema(text="Second"),
                    NumberedListItemSchema(text="Third"),
                ]
            )
        ]
    )
    result = converter.convert(schema)
    assert "First" in result
    assert "Second" in result
    assert "Third" in result


def test_convert_numbered_list_item(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[NumberedListItemSchema(text="Single numbered item")]
    )
    result = converter.convert(schema)
    assert "Single numbered item" in result


def test_convert_numbered_list_item_with_children(
    converter: StructuredOutputMarkdownConverter,
):
    schema = MarkdownDocumentSchema(
        nodes=[
            NumberedListItemSchema(
                text="Numbered item", children=[ParagraphSchema(text="Details")]
            )
        ]
    )
    result = converter.convert(schema)
    assert "Numbered item" in result
    assert "Details" in result


def test_convert_todo_unchecked(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[TodoSchema(text="Task to do", checked=False)]
    )
    result = converter.convert(schema)
    assert "Task to do" in result


def test_convert_todo_checked(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[TodoSchema(text="Completed task", checked=True)]
    )
    result = converter.convert(schema)
    assert "Completed task" in result


def test_convert_todo_with_children(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            TodoSchema(
                text="Task",
                checked=False,
                children=[ParagraphSchema(text="Task details")],
            )
        ]
    )
    result = converter.convert(schema)
    assert "Task" in result
    assert "Task details" in result


def test_convert_todo_list(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            TodoListSchema(
                items=[
                    TodoSchema(text="Task 1", checked=True),
                    TodoSchema(text="Task 2", checked=False),
                    TodoSchema(text="Task 3", checked=False),
                ]
            )
        ]
    )
    result = converter.convert(schema)
    assert "Task 1" in result
    assert "Task 2" in result
    assert "Task 3" in result


def test_convert_todo_list_without_completion_status(
    converter: StructuredOutputMarkdownConverter,
):
    schema = MarkdownDocumentSchema(
        nodes=[
            TodoListSchema(
                items=[
                    TodoSchema(text="Task A"),
                    TodoSchema(text="Task B"),
                ]
            )
        ]
    )
    result = converter.convert(schema)
    assert "Task A" in result
    assert "Task B" in result


def test_convert_callout_without_children(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[CalloutSchema(text="Important message", emoji="💡")]
    )
    result = converter.convert(schema)
    assert "Important message" in result


def test_convert_callout_with_children(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            CalloutSchema(
                text="Note",
                emoji="📝",
                children=[ParagraphSchema(text="Additional info")],
            )
        ]
    )
    result = converter.convert(schema)
    assert "Note" in result
    assert "Additional info" in result


def test_convert_toggle(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            ToggleSchema(
                title="Click to expand",
                children=[ParagraphSchema(text="Hidden content")],
            )
        ]
    )
    result = converter.convert(schema)
    assert "Click to expand" in result
    assert "Hidden content" in result


def test_convert_image(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[ImageSchema(url="https://example.com/image.png", caption="An image")]
    )
    result = converter.convert(schema)
    assert "https://example.com/image.png" in result


def test_convert_video(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[VideoSchema(url="https://example.com/video.mp4", caption="A video")]
    )
    result = converter.convert(schema)
    assert "https://example.com/video.mp4" in result


def test_convert_audio(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[AudioSchema(url="https://example.com/audio.mp3", caption="An audio")]
    )
    result = converter.convert(schema)
    assert "https://example.com/audio.mp3" in result


def test_convert_file(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[FileSchema(url="https://example.com/file.zip", caption="A file")]
    )
    result = converter.convert(schema)
    assert "https://example.com/file.zip" in result


def test_convert_pdf(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[PdfSchema(url="https://example.com/document.pdf", caption="A PDF")]
    )
    result = converter.convert(schema)
    assert "https://example.com/document.pdf" in result


def test_convert_bookmark(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            BookmarkSchema(
                url="https://example.com",
                title="Example Site",
                caption="Bookmark caption",
            )
        ]
    )
    result = converter.convert(schema)
    assert "https://example.com" in result


def test_convert_embed(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            EmbedSchema(
                url="https://www.youtube.com/embed/xyz", caption="Embedded video"
            )
        ]
    )
    result = converter.convert(schema)
    assert "https://www.youtube.com/embed/xyz" in result


def test_convert_code(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            CodeSchema(
                code='print("Hello, World!")',
                language=CodingLanguage.PYTHON,
                caption="Python example",
            )
        ]
    )
    result = converter.convert(schema)
    assert 'print("Hello, World!")' in result


def test_convert_mermaid(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            MermaidSchema(
                diagram="graph TD;\n    A-->B;",
                caption="Flow diagram",
            )
        ]
    )
    result = converter.convert(schema)
    assert "graph TD;" in result
    assert "A-->B;" in result


def test_convert_table(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            TableSchema(
                headers=["Name", "Age", "City"],
                rows=[["Alice", "30", "NYC"], ["Bob", "25", "LA"]],
            )
        ]
    )
    result = converter.convert(schema)
    assert "Name" in result
    assert "Age" in result
    assert "City" in result
    assert "Alice" in result
    assert "Bob" in result


def test_convert_breadcrumb(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(nodes=[BreadcrumbSchema()])
    result = converter.convert(schema)
    assert result != ""


def test_convert_equation(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(nodes=[EquationSchema(expression="E = mc^2")])
    result = converter.convert(schema)
    assert "E = mc^2" in result


def test_convert_table_of_contents(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(nodes=[TableOfContentsSchema()])
    result = converter.convert(schema)
    assert result != ""


def test_convert_columns(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            ColumnsSchema(
                columns=[
                    ColumnSchema(
                        width_ratio=0.5, children=[ParagraphSchema(text="Column 1")]
                    ),
                    ColumnSchema(
                        width_ratio=0.5, children=[ParagraphSchema(text="Column 2")]
                    ),
                ]
            )
        ]
    )
    result = converter.convert(schema)
    assert "Column 1" in result
    assert "Column 2" in result


def test_convert_columns_without_width_ratios(
    converter: StructuredOutputMarkdownConverter,
):
    schema = MarkdownDocumentSchema(
        nodes=[
            ColumnsSchema(
                columns=[
                    ColumnSchema(children=[ParagraphSchema(text="Col A")]),
                    ColumnSchema(children=[ParagraphSchema(text="Col B")]),
                ]
            )
        ]
    )
    result = converter.convert(schema)
    assert "Col A" in result
    assert "Col B" in result


def test_convert_complex_nested_document(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            Heading1Schema(
                text="Main Title",
                children=[
                    ParagraphSchema(text="Introduction paragraph"),
                    BulletedListItemSchema(
                        text="List item",
                        children=[ParagraphSchema(text="Item details")],
                    ),
                ],
            ),
            SpaceSchema(),
            QuoteSchema(
                text="Important quote",
                children=[
                    TodoSchema(
                        text="Follow-up task",
                        checked=False,
                        children=[ParagraphSchema(text="Task notes")],
                    )
                ],
            ),
        ]
    )
    result = converter.convert(schema)

    assert "# Main Title" in result
    assert "Introduction paragraph" in result
    assert "List item" in result
    assert "Item details" in result
    assert "> Important quote" in result
    assert "Follow-up task" in result
    assert "Task notes" in result


def test_convert_multiple_nodes_in_sequence(
    converter: StructuredOutputMarkdownConverter,
):
    schema = MarkdownDocumentSchema(
        nodes=[
            Heading1Schema(text="Document Title"),
            ParagraphSchema(text="First paragraph"),
            DividerSchema(),
            BulletedListSchema(
                items=[
                    BulletedListItemSchema(text="Alpha"),
                    BulletedListItemSchema(text="Beta"),
                    BulletedListItemSchema(text="Gamma"),
                ]
            ),
            SpaceSchema(),
            CodeSchema(code="x = 42", language=CodingLanguage.PYTHON),
        ]
    )
    result = converter.convert(schema)

    assert "# Document Title" in result
    assert "First paragraph" in result
    assert "---" in result
    assert "Alpha" in result
    assert "Beta" in result
    assert "Gamma" in result
    assert "x = 42" in result


def test_convert_complete_realistic_document(
    converter: StructuredOutputMarkdownConverter,
):
    schema = MarkdownDocumentSchema(
        nodes=[
            Heading1Schema(text="Project Documentation"),
            ParagraphSchema(text="Welcome to the project documentation."),
            SpaceSchema(),
            Heading2Schema(text="Features"),
            BulletedListSchema(
                items=[
                    BulletedListItemSchema(text="Fast"),
                    BulletedListItemSchema(text="Reliable"),
                    BulletedListItemSchema(text="Easy to use"),
                ]
            ),
            SpaceSchema(),
            Heading2Schema(text="Installation"),
            NumberedListSchema(
                items=[
                    NumberedListItemSchema(text="Clone the repository"),
                    NumberedListItemSchema(text="Install dependencies"),
                    NumberedListItemSchema(text="Run the application"),
                ]
            ),
            SpaceSchema(),
            CalloutSchema(text="Important: Read the docs!", emoji="⚠️"),
            SpaceSchema(),
            CodeSchema(
                code="pip install mypackage",
                language=CodingLanguage.BASH,
            ),
            SpaceSchema(),
            Heading2Schema(text="Todo"),
            TodoListSchema(
                items=[
                    TodoSchema(text="Write tests", checked=True),
                    TodoSchema(text="Update README", checked=True),
                    TodoSchema(text="Release v1.0", checked=False),
                ]
            ),
        ]
    )
    result = converter.convert(schema)

    assert "# Project Documentation" in result
    assert "Welcome to the project documentation." in result
    assert "## Features" in result
    assert "- Fast" in result
    assert "- Reliable" in result
    assert "- Easy to use" in result
    assert "## Installation" in result
    assert "Clone the repository" in result
    assert "Install dependencies" in result
    assert "Run the application" in result
    assert "Important: Read the docs!" in result
    assert "pip install mypackage" in result
    assert "## Todo" in result
    assert "Write tests" in result
    assert "Update README" in result
    assert "Release v1.0" in result


def test_deeply_nested_structure(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            Heading1Schema(
                text="Level 1",
                children=[
                    QuoteSchema(
                        text="Level 2",
                        children=[
                            CalloutSchema(
                                text="Level 3",
                                emoji="📌",
                                children=[
                                    TodoSchema(
                                        text="Level 4",
                                        checked=False,
                                        children=[
                                            ParagraphSchema(text="Level 5 - deepest")
                                        ],
                                    )
                                ],
                            )
                        ],
                    )
                ],
            )
        ]
    )
    result = converter.convert(schema)

    assert "# Level 1" in result
    assert "Level 2" in result
    assert "Level 3" in result
    assert "Level 4" in result
    assert "Level 5 - deepest" in result


def test_mixed_list_types(converter: StructuredOutputMarkdownConverter):
    schema = MarkdownDocumentSchema(
        nodes=[
            BulletedListSchema(
                items=[
                    BulletedListItemSchema(text="Bullet 1"),
                    BulletedListItemSchema(text="Bullet 2"),
                ]
            ),
            SpaceSchema(),
            NumberedListSchema(
                items=[
                    NumberedListItemSchema(text="Number 1"),
                    NumberedListItemSchema(text="Number 2"),
                ]
            ),
            SpaceSchema(),
            TodoListSchema(
                items=[
                    TodoSchema(text="Todo 1", checked=True),
                    TodoSchema(text="Todo 2", checked=False),
                ]
            ),
        ]
    )
    result = converter.convert(schema)

    assert "Bullet 1" in result
    assert "Bullet 2" in result
    assert "Number 1" in result
    assert "Number 2" in result
    assert "Todo 1" in result
    assert "Todo 2" in result
