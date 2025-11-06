from notionary.page.content.renderer.post_processing.handlers import (
    NumberedListPlaceholderReplacerPostProcessor,
)
from notionary.page.content.renderer.post_processing.service import (
    MarkdownRenderingPostProcessor,
)


def create_markdown_rendering_post_processor() -> MarkdownRenderingPostProcessor:
    post_processor = MarkdownRenderingPostProcessor()
    post_processor.register(NumberedListPlaceholderReplacerPostProcessor())
    return post_processor
