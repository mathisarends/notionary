from notionary.page.content.parser.parsers import LineParser
from notionary.page.content.parser.parsers.factory import create_line_parser
from notionary.page.content.parser.post_processing.factory import (
    create_markdown_to_rich_text_post_processor,
)
from notionary.page.content.parser.pre_processsing.factory import (
    create_markdown_to_rich_text_pre_processor,
)
from notionary.page.content.parser.service import MarkdownToNotionConverter


def create_markdown_to_notion_converter(
    line_parser: LineParser | None = None,
) -> MarkdownToNotionConverter:
    line_parser = line_parser or create_line_parser()
    markdown_pre_processor = create_markdown_to_rich_text_pre_processor()
    block_post_processor = create_markdown_to_rich_text_post_processor()

    return MarkdownToNotionConverter(
        line_parser=line_parser,
        pre_processor=markdown_pre_processor,
        post_processor=block_post_processor,
    )
