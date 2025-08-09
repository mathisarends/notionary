from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING

from notionary.blocks.bookmark.bookmark_models import BookmarkBlock, CreateBookmarkBlock
from notionary.blocks.block_models import Block, BlockType
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.prompts import ElementPromptBuilder, ElementPromptContent

if TYPE_CHECKING:
    from notionary.blocks.block_models import BlockCreateResult

# BookmarkElement implementation using BlockType enum and TextInlineFormatter
class BookmarkElement(NotionBlockElement):
    """
    Handles conversion between Markdown bookmarks and Notion bookmark blocks.

    Markdown bookmark syntax:
    - [bookmark](https://example.com) - URL only
    - [bookmark](https://example.com "Title") - URL + title
    - [bookmark](https://example.com "Title" "Description") - URL + title + description
    """

    PATTERN = re.compile(
        r"^\[bookmark\]\("  # prefix
        r"(https?://[^\s\"]+)"  # URL
        r"(?:\s+\"([^\"]+)\")?"  # optional Title
        r"(?:\s+\"([^\"]+)\")?"  # optional Description
        r"\)$"
    )

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        text = text.strip()
        return text.startswith("[bookmark]") and bool(cls.PATTERN.match(text))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.BOOKMARK and block.bookmark

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """
        Convert a markdown bookmark into a Notion BookmarkBlock.
        """
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        url, title, description = m.group(1), m.group(2), m.group(3)

        # Build caption texts
        parts: list[str] = []
        if title:
            parts.append(title)
        if description:
            parts.append(description)

        caption = []
        if parts:
            joined = " – ".join(parts)
            caption = TextInlineFormatter.parse_inline_formatting(joined)

        bookmark_data = BookmarkBlock(url=url, caption=caption)
        return CreateBookmarkBlock(bookmark=bookmark_data)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.BOOKMARK or block.bookmark is None:
            return None

        bm = block.bookmark
        url = bm.url
        if not url:
            return None

        captions = bm.caption or []
        if not captions:
            return f"[bookmark]({url})"

        text = TextInlineFormatter.extract_text_with_formatting(captions)
        
        if " - " in text:
            title, desc = map(str.strip, text.split(" - ", 1))
            return f'[bookmark]({url} "{title}" "{desc}")'

        return f'[bookmark]({url} "{text}")'

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description("Creates a bookmark block linking to an external URL.")
            .with_usage_guidelines(
                "Use bookmarks to embed link previews with optional title and description."
            )
            .with_syntax('[bookmark](https://example.com "Title" "Description")')
            .with_examples(
                [
                    "[bookmark](https://example.com)",
                    '[bookmark](https://example.com "Title")',
                    '[bookmark](https://example.com "Title" "Desc")',
                ]
            )
            .build()
        )
