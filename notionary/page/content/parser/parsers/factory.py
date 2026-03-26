from notionary.page.content.parser.parsers import (
    AudioParser,
    BookmarkParser,
    BreadcrumbParser,
    BulletedListParser,
    CalloutParser,
    CaptionParser,
    CodeParser,
    ColumnListParser,
    ColumnParser,
    DividerParser,
    EmbedParser,
    EquationParser,
    FileParser,
    HeadingParser,
    ImageParser,
    LineParser,
    NumberedListParser,
    ParagraphParser,
    PdfParser,
    QuoteParser,
    SpaceParser,
    TableOfContentsParser,
    TableParser,
    TodoParser,
    ToggleParser,
    VideoParser,
)
from notionary.page.markdown.syntax.definition import SyntaxDefinitionRegistry
from notionary.rich_text.markdown_to_rich_text.converter import (
    MarkdownRichTextConverter,
)
from notionary.rich_text.markdown_to_rich_text.factory import (
    create_markdown_to_rich_text_converter,
)


def create_line_parser(
    rich_text_converter: MarkdownRichTextConverter | None = None,
) -> LineParser:
    rich_text_converter = (
        rich_text_converter or create_markdown_to_rich_text_converter()
    )
    syntax_registry = SyntaxDefinitionRegistry()

    code_parser = CodeParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    equation_parser = EquationParser(syntax_registry=syntax_registry)
    table_parser = TableParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    column_parser = ColumnParser(syntax_registry=syntax_registry)
    column_list_parser = ColumnListParser(syntax_registry=syntax_registry)
    toggle_parser = ToggleParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )

    divider_parser = DividerParser(syntax_registry=syntax_registry)
    breadcrumb_parser = BreadcrumbParser(syntax_registry=syntax_registry)
    table_of_contents_parser = TableOfContentsParser(syntax_registry=syntax_registry)
    space_parser = SpaceParser(syntax_registry=syntax_registry)
    heading_parser = HeadingParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    quote_parser = QuoteParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    callout_parser = CalloutParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    todo_parser = TodoParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    bulleted_list_parser = BulletedListParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    numbered_list_parser = NumberedListParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )

    bookmark_parser = BookmarkParser(syntax_registry=syntax_registry)
    embed_parser = EmbedParser(syntax_registry=syntax_registry)
    image_parser = ImageParser(
        syntax_registry=syntax_registry,
    )
    video_parser = VideoParser(
        syntax_registry=syntax_registry,
    )
    audio_parser = AudioParser(
        syntax_registry=syntax_registry,
    )
    file_parser = FileParser(
        syntax_registry=syntax_registry,
    )
    pdf_parser = PdfParser(
        syntax_registry=syntax_registry,
    )

    caption_parser = CaptionParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    paragraph_parser = ParagraphParser(rich_text_converter=rich_text_converter)

    (
        code_parser.next(equation_parser)
        .next(table_parser)
        .next(column_parser)
        .next(column_list_parser)
        .next(toggle_parser)
        .next(divider_parser)
        .next(breadcrumb_parser)
        .next(table_of_contents_parser)
        .next(space_parser)
        .next(heading_parser)
        .next(quote_parser)
        .next(callout_parser)
        .next(todo_parser)
        .next(bulleted_list_parser)
        .next(numbered_list_parser)
        .next(bookmark_parser)
        .next(embed_parser)
        .next(image_parser)
        .next(video_parser)
        .next(audio_parser)
        .next(file_parser)
        .next(pdf_parser)
        .next(caption_parser)
        .next(paragraph_parser)
    )

    return code_parser
