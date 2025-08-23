from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.bookmark.bookmark_models import BookmarkBlock, CreateBookmarkBlock
from notionary.blocks.mixins.captions import CaptionMixin
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult, BlockType


class BookmarkElement(BaseBlockElement, CaptionMixin):
    """
    Handles conversion between Markdown bookmarks and Notion bookmark blocks.

    Markdown bookmark syntax:
    - [bookmark](https://example.com) - URL only
    - [bookmark](https://example.com)(caption:This is a caption) - URL with caption
    - (caption:This is a caption)[bookmark](https://example.com) - caption before URL
    """

    # Flexible pattern that can handle caption in any position
    BOOKMARK_PATTERN = re.compile(r"\[bookmark\]\((https?://[^\s\"]+)\)")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.BOOKMARK and block.bookmark

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """
        Convert a markdown bookmark into a Notion BookmarkBlock.
        """
        # First remove captions to get clean text for URL extraction
        clean_text = cls.remove_caption(text.strip())

        # Use our own regex to find the bookmark URL
        bookmark_match = cls.BOOKMARK_PATTERN.search(clean_text)
        if not bookmark_match:
            return None

        url = bookmark_match.group(1)

        caption_text = cls.extract_caption(text.strip())
        caption_rich_text = cls.build_caption_rich_text(caption_text or "")

        bookmark_data = BookmarkBlock(url=url, caption=caption_rich_text)
        return CreateBookmarkBlock(bookmark=bookmark_data)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.BOOKMARK or block.bookmark is None:
            return None

        bm = block.bookmark
        url = bm.url
        if not url:
            return None

        result = f"[bookmark]({url})"

        # Add caption if present
        caption_markdown = cls.format_caption_for_markdown(bm.caption or [])
        if caption_markdown:
            result += caption_markdown

        return result

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
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
