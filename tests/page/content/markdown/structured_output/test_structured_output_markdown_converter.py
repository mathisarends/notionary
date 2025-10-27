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
    HeadingSchema,
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


class TestStructuredOutputMarkdownConverter:
    def test_initialization_with_default_builder(self):
        converter = StructuredOutputMarkdownConverter()
        assert converter.builder is not None
        assert isinstance(converter.builder, MarkdownBuilder)

    def test_initialization_with_custom_builder(self):
        custom_builder = MarkdownBuilder()
        converter = StructuredOutputMarkdownConverter(builder=custom_builder)
        assert converter.builder is custom_builder

    def test_convert_empty_document(self):
        schema = MarkdownDocumentSchema(nodes=[])
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert result == ""

    def test_convert_paragraph(self):
        schema = MarkdownDocumentSchema(nodes=[ParagraphSchema(text="Test paragraph")])
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Test paragraph" in result

    def test_convert_heading_level_1(self):
        schema = MarkdownDocumentSchema(
            nodes=[HeadingSchema(text="Heading 1", level=1)]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "# Heading 1" in result

    def test_convert_heading_level_2(self):
        schema = MarkdownDocumentSchema(
            nodes=[HeadingSchema(text="Heading 2", level=2)]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "## Heading 2" in result

    def test_convert_heading_level_3(self):
        schema = MarkdownDocumentSchema(
            nodes=[HeadingSchema(text="Heading 3", level=3)]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "### Heading 3" in result

    def test_convert_heading_with_children(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                HeadingSchema(
                    text="Parent",
                    level=1,
                    children=[ParagraphSchema(text="Child content")],
                )
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "# Parent" in result
        assert "Child content" in result

    def test_convert_space(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                ParagraphSchema(text="Before"),
                SpaceSchema(),
                ParagraphSchema(text="After"),
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Before" in result
        assert "After" in result

    def test_convert_divider(self):
        schema = MarkdownDocumentSchema(nodes=[DividerSchema()])
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "---" in result

    def test_convert_quote(self):
        schema = MarkdownDocumentSchema(nodes=[QuoteSchema(text="Quote text")])
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "> Quote text" in result

    def test_convert_quote_with_children(self):
        schema = MarkdownDocumentSchema(
            nodes=[QuoteSchema(text="Quote", children=[ParagraphSchema(text="Nested")])]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "> Quote" in result
        assert "Nested" in result

    def test_convert_bulleted_list(self):
        schema = MarkdownDocumentSchema(
            nodes=[BulletedListSchema(items=["Item 1", "Item 2", "Item 3"])]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "- Item 1" in result
        assert "- Item 2" in result
        assert "- Item 3" in result

    def test_convert_bulleted_list_item(self):
        schema = MarkdownDocumentSchema(
            nodes=[BulletedListItemSchema(text="Single item")]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "- Single item" in result

    def test_convert_bulleted_list_item_with_children(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                BulletedListItemSchema(
                    text="Parent item",
                    children=[ParagraphSchema(text="Nested content")],
                )
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "- Parent item" in result
        assert "Nested content" in result

    def test_convert_numbered_list(self):
        schema = MarkdownDocumentSchema(
            nodes=[NumberedListSchema(items=["First", "Second", "Third"])]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "First" in result
        assert "Second" in result
        assert "Third" in result

    def test_convert_numbered_list_item(self):
        schema = MarkdownDocumentSchema(
            nodes=[NumberedListItemSchema(text="Single numbered item")]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Single numbered item" in result

    def test_convert_numbered_list_item_with_children(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                NumberedListItemSchema(
                    text="Numbered item", children=[ParagraphSchema(text="Details")]
                )
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Numbered item" in result
        assert "Details" in result

    def test_convert_todo_unchecked(self):
        schema = MarkdownDocumentSchema(
            nodes=[TodoSchema(text="Task to do", checked=False)]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Task to do" in result

    def test_convert_todo_checked(self):
        schema = MarkdownDocumentSchema(
            nodes=[TodoSchema(text="Completed task", checked=True)]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Completed task" in result

    def test_convert_todo_with_children(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                TodoSchema(
                    text="Task",
                    checked=False,
                    children=[ParagraphSchema(text="Task details")],
                )
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Task" in result
        assert "Task details" in result

    def test_convert_todo_list(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                TodoListSchema(
                    items=["Task 1", "Task 2", "Task 3"], completed=[True, False, False]
                )
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Task 1" in result
        assert "Task 2" in result
        assert "Task 3" in result

    def test_convert_todo_list_without_completion_status(self):
        schema = MarkdownDocumentSchema(
            nodes=[TodoListSchema(items=["Task 1", "Task 2"], completed=None)]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Task 1" in result
        assert "Task 2" in result

    def test_convert_callout_without_children(self):
        schema = MarkdownDocumentSchema(
            nodes=[CalloutSchema(text="Important note", emoji="💡")]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Important note" in result

    def test_convert_callout_with_children(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                CalloutSchema(
                    text="Note",
                    emoji="💡",
                    children=[ParagraphSchema(text="Additional details")],
                )
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Note" in result
        assert "Additional details" in result

    def test_convert_toggle(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                ToggleSchema(
                    title="Toggle title",
                    children=[ParagraphSchema(text="Hidden content")],
                )
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Toggle title" in result
        assert "Hidden content" in result

    def test_convert_image(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                ImageSchema(
                    url="https://example.com/image.png", caption="Image caption"
                )
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "https://example.com/image.png" in result

    def test_convert_video(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                VideoSchema(
                    url="https://example.com/video.mp4", caption="Video caption"
                )
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "https://example.com/video.mp4" in result

    def test_convert_audio(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                AudioSchema(
                    url="https://example.com/audio.mp3", caption="Audio caption"
                )
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "https://example.com/audio.mp3" in result

    def test_convert_file(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                FileSchema(url="https://example.com/file.pdf", caption="File caption")
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "https://example.com/file.pdf" in result

    def test_convert_pdf(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                PdfSchema(url="https://example.com/document.pdf", caption="PDF caption")
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "https://example.com/document.pdf" in result

    def test_convert_bookmark(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                BookmarkSchema(
                    url="https://example.com",
                    title="Example Site",
                    caption="Bookmark caption",
                )
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "https://example.com" in result

    def test_convert_embed(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                EmbedSchema(url="https://example.com/embed", caption="Embed caption")
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "https://example.com/embed" in result

    def test_convert_code(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                CodeSchema(
                    code='print("Hello, World!")',
                    language=CodingLanguage.PYTHON,
                    caption="Python example",
                )
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert 'print("Hello, World!")' in result
        assert "```" in result

    def test_convert_code_without_language(self):
        schema = MarkdownDocumentSchema(
            nodes=[CodeSchema(code="some code", language=None, caption=None)]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "some code" in result

    def test_convert_mermaid(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                MermaidSchema(diagram="graph TD\n    A-->B", caption="Mermaid diagram")
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "graph TD" in result
        assert "A-->B" in result

    def test_convert_table(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                TableSchema(
                    headers=["Name", "Age", "City"],
                    rows=[
                        ["Alice", "30", "Berlin"],
                        ["Bob", "25", "Munich"],
                    ],
                )
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Name" in result
        assert "Age" in result
        assert "City" in result
        assert "Alice" in result
        assert "Bob" in result

    def test_convert_breadcrumb(self):
        schema = MarkdownDocumentSchema(nodes=[BreadcrumbSchema()])
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert result != ""

    def test_convert_equation(self):
        schema = MarkdownDocumentSchema(nodes=[EquationSchema(expression="E = mc^2")])
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "E = mc^2" in result

    def test_convert_table_of_contents(self):
        schema = MarkdownDocumentSchema(nodes=[TableOfContentsSchema()])
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert result != ""

    def test_convert_columns(self):
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
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Column 1" in result
        assert "Column 2" in result

    def test_convert_columns_without_width_ratios(self):
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
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)
        assert "Col A" in result
        assert "Col B" in result

    def test_convert_complex_nested_document(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                HeadingSchema(
                    text="Main Title",
                    level=1,
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
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)

        assert "# Main Title" in result
        assert "Introduction paragraph" in result
        assert "List item" in result
        assert "Item details" in result
        assert "> Important quote" in result
        assert "Follow-up task" in result
        assert "Task notes" in result

    def test_convert_multiple_nodes_in_sequence(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                HeadingSchema(text="Document Title", level=1),
                ParagraphSchema(text="First paragraph"),
                DividerSchema(),
                BulletedListSchema(items=["Alpha", "Beta", "Gamma"]),
                SpaceSchema(),
                CodeSchema(code="x = 42", language=CodingLanguage.PYTHON),
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)

        assert "# Document Title" in result
        assert "First paragraph" in result
        assert "---" in result
        assert "- Alpha" in result
        assert "- Beta" in result
        assert "- Gamma" in result
        assert "x = 42" in result

    def test_convert_complete_realistic_document(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                HeadingSchema(text="Project Documentation", level=1),
                ParagraphSchema(text="Welcome to the project documentation."),
                SpaceSchema(),
                HeadingSchema(text="Features", level=2),
                BulletedListSchema(items=["Fast", "Reliable", "Easy to use"]),
                SpaceSchema(),
                HeadingSchema(text="Installation", level=2),
                NumberedListSchema(
                    items=[
                        "Clone the repository",
                        "Install dependencies",
                        "Run the application",
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
                HeadingSchema(text="Todo", level=2),
                TodoListSchema(
                    items=["Write tests", "Update README", "Release v1.0"],
                    completed=[True, True, False],
                ),
            ]
        )
        converter = StructuredOutputMarkdownConverter()
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

    def test_deeply_nested_structure(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                HeadingSchema(
                    text="Level 1",
                    level=1,
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
                                                ParagraphSchema(
                                                    text="Level 5 - deepest"
                                                )
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
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)

        assert "# Level 1" in result
        assert "Level 2" in result
        assert "Level 3" in result
        assert "Level 4" in result
        assert "Level 5 - deepest" in result

    def test_mixed_list_types(self):
        schema = MarkdownDocumentSchema(
            nodes=[
                BulletedListSchema(items=["Bullet 1", "Bullet 2"]),
                SpaceSchema(),
                NumberedListSchema(items=["Number 1", "Number 2"]),
                SpaceSchema(),
                TodoListSchema(items=["Todo 1", "Todo 2"], completed=[True, False]),
            ]
        )
        converter = StructuredOutputMarkdownConverter()
        result = converter.convert(schema)

        assert "Bullet 1" in result
        assert "Bullet 2" in result
        assert "Number 1" in result
        assert "Number 2" in result
        assert "Todo 1" in result
        assert "Todo 2" in result
