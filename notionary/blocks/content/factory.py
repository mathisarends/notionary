from notionary.blocks.client import NotionBlockHttpClient
from notionary.blocks.content.service import BlockContentService
from notionary.page.content.parser.factory import create_markdown_to_notion_converter
from notionary.page.content.renderer.factory import create_notion_to_markdown_converter


def create_block_content_service(
    block_id: str,
    block_client: NotionBlockHttpClient,
) -> BlockContentService:
    markdown_converter = create_markdown_to_notion_converter()
    notion_to_markdown_converter = create_notion_to_markdown_converter()

    return BlockContentService(
        block_id=block_id,
        block_client=block_client,
        markdown_converter=markdown_converter,
        notion_to_markdown_converter=notion_to_markdown_converter,
    )
