import re

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.mappings.mixins.captions import CaptionMixin
from notionary.blocks.schemas import Block, BlockType, BookmarkData, CreateBookmarkBlock
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


class BookmarkMapper(NotionMarkdownMapper, CaptionMixin):
    block_type = BlockType.BOOKMARK

    # Flexible pattern that can handle caption in any position
    BOOKMARK_PATTERN = re.compile(r"\[bookmark\]\((https?://[^\s\"]+)\)")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.BOOKMARK and block.bookmark

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreateBookmarkBlock | None:
        clean_text = cls.remove_caption(text.strip())

        # Use our own regex to find the bookmark URL
        bookmark_match = cls.BOOKMARK_PATTERN.search(clean_text)
        if not bookmark_match:
            return None

        url = bookmark_match.group(1)

        caption_text = cls.extract_caption(text.strip())
        caption_rich_text = cls.build_caption_rich_text(caption_text or "")

        bookmark_data = BookmarkData(url=url, caption=caption_rich_text)
        return CreateBookmarkBlock(bookmark=bookmark_data)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.BOOKMARK or block.bookmark is None:
            return None

        bm = block.bookmark
        url = bm.url
        if not url:
            return None

        result = f"[bookmark]({url})"

        # Add caption if present
        caption_markdown = await cls.format_caption_for_markdown(bm.caption or [])
        if caption_markdown:
            result += caption_markdown

        return result

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for bookmark blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Bookmark blocks create previews of web pages with optional captions",
            syntax_examples=[
                "[bookmark](https://example.com)",
                "[bookmark](https://example.com)(caption:This is a caption)",
                "(caption:Check out this repository)[bookmark](https://github.com/user/repo)",
                "[bookmark](https://github.com/user/repo)(caption:Check out this awesome repository)",
            ],
            usage_guidelines="Use for linking to external websites with rich previews. URL is required. Caption supports rich text formatting and is optional.",
        )
