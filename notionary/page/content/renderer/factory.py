from notionary.page.content.renderer.post_processing.factory import (
    create_markdown_rendering_post_processor,
)
from notionary.page.content.renderer.renderers.factory import create_renderer_chain
from notionary.page.content.renderer.service import NotionToMarkdownConverter


def create_notion_to_markdown_converter() -> NotionToMarkdownConverter:
    renderer_chain = create_renderer_chain()
    post_processor = create_markdown_rendering_post_processor()

    return NotionToMarkdownConverter(renderer_chain, post_processor)
