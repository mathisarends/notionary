from notionary.page.content.parser.pre_processsing.handlers import (
    ColumnSyntaxPreProcessor,
    IndentationNormalizer,
    VideoFormatPreProcessor,
    WhitespacePreProcessor,
)
from notionary.page.content.parser.pre_processsing.service import MarkdownPreProcessor


def create_markdown_to_rich_text_pre_processor() -> MarkdownPreProcessor:
    pre_processor = MarkdownPreProcessor()
    pre_processor.register(ColumnSyntaxPreProcessor())
    pre_processor.register(WhitespacePreProcessor())
    pre_processor.register(IndentationNormalizer())
    pre_processor.register(VideoFormatPreProcessor())
    return pre_processor
