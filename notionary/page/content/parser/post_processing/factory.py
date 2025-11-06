from notionary.page.content.parser.post_processing.handlers import (
    RichTextLengthTruncationPostProcessor,
)
from notionary.page.content.parser.post_processing.service import BlockPostProcessor


def create_markdown_to_rich_text_post_processor() -> BlockPostProcessor:
    post_processor = BlockPostProcessor()
    post_processor.register(RichTextLengthTruncationPostProcessor())
    return post_processor
