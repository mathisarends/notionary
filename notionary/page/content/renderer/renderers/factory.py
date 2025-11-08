from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.renderer.renderers import (
    AudioRenderer,
    BlockRenderer,
    BookmarkRenderer,
    BreadcrumbRenderer,
    BulletedListRenderer,
    CalloutRenderer,
    CodeRenderer,
    ColumnListRenderer,
    ColumnRenderer,
    DividerRenderer,
    EmbedRenderer,
    EquationRenderer,
    FallbackRenderer,
    FileRenderer,
    HeadingRenderer,
    ImageRenderer,
    NumberedListRenderer,
    ParagraphRenderer,
    PdfRenderer,
    QuoteRenderer,
    TableOfContentsRenderer,
    TableRenderer,
    TableRowHandler,
    TodoRenderer,
    ToggleRenderer,
    VideoRenderer,
)
from notionary.rich_text.rich_text_to_markdown import (
    create_rich_text_to_markdown_converter,
)


def create_renderer_chain() -> BlockRenderer:
    rich_text_markdown_converter = create_rich_text_to_markdown_converter()
    syntax_registry = SyntaxDefinitionRegistry()
    markdown_grammar = MarkdownGrammar()

    toggle_handler = ToggleRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )
    heading_handler = HeadingRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )

    # Content Blocks
    callout_handler = CalloutRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )
    code_handler = CodeRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )
    quote_handler = QuoteRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )
    todo_handler = TodoRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )
    bulleted_list_handler = BulletedListRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )

    divider_handler = DividerRenderer(syntax_registry=syntax_registry)
    column_list_handler = ColumnListRenderer(syntax_registry=syntax_registry)
    column_handler = ColumnRenderer(syntax_registry=syntax_registry)
    numbered_list_handler = NumberedListRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
        markdown_grammar=markdown_grammar,
    )

    bookmark_handler = BookmarkRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )
    image_handler = ImageRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )
    video_handler = VideoRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )
    audio_handler = AudioRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )
    file_handler = FileRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )
    pdf_handler = PdfRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )
    embed_handler = EmbedRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )

    equation_handler = EquationRenderer(syntax_registry=syntax_registry)
    table_of_contents_handler = TableOfContentsRenderer(syntax_registry=syntax_registry)
    breadcrumb_handler = BreadcrumbRenderer(syntax_registry=syntax_registry)
    table_handler = TableRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )
    table_row_handler = TableRowHandler(syntax_registry=syntax_registry)

    paragraph_handler = ParagraphRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=rich_text_markdown_converter,
    )
    fallback_handler = FallbackRenderer(syntax_registry=syntax_registry)

    # most specific first, fallback last
    (
        toggle_handler.set_next(heading_handler)
        .set_next(callout_handler)
        .set_next(code_handler)
        .set_next(quote_handler)
        .set_next(todo_handler)
        .set_next(bulleted_list_handler)
        .set_next(divider_handler)
        .set_next(column_list_handler)
        .set_next(column_handler)
        .set_next(numbered_list_handler)
        .set_next(bookmark_handler)
        .set_next(image_handler)
        .set_next(video_handler)
        .set_next(audio_handler)
        .set_next(file_handler)
        .set_next(pdf_handler)
        .set_next(embed_handler)
        .set_next(equation_handler)
        .set_next(table_of_contents_handler)
        .set_next(breadcrumb_handler)
        .set_next(table_handler)
        .set_next(table_row_handler)
        .set_next(paragraph_handler)
        .set_next(fallback_handler)
    )

    return toggle_handler
