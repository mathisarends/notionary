import re
from typing import Any, Dict, List
from notionary.util.logging_mixin import LoggingMixin


class NotionPageContentChunker(LoggingMixin):
    """Handles chunking of markdown text to conform to Notion API limits."""

    def __init__(self, max_text_length: int = 1900):
        self.max_text_length = max_text_length

    def fix_blocks_content_length(
        self, blocks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check each block and ensure text content doesn't exceed Notion's limit."""
        return [self._fix_single_block_content(block) for block in blocks]

    def _fix_single_block_content(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """Fix content length in a single block and its children recursively."""
        block_copy = block.copy()

        block_type = block.get("type")
        if not block_type:
            return block_copy

        content = block.get(block_type)
        if not content:
            return block_copy

        if "rich_text" in content:
            self._fix_rich_text_content(block_copy, block_type, content)

        if "children" in content and content["children"]:
            block_copy[block_type]["children"] = [
                self._fix_single_block_content(child) for child in content["children"]
            ]

        return block_copy

    def _fix_rich_text_content(
        self, block_copy: Dict[str, Any], block_type: str, content: Dict[str, Any]
    ) -> None:
        """Fix rich text content that exceeds the length limit."""
        rich_text = content["rich_text"]
        for i, text_item in enumerate(rich_text):
            if "text" not in text_item or "content" not in text_item["text"]:
                continue

            text_content = text_item["text"]["content"]
            if len(text_content) <= self.max_text_length:
                continue

            self.logger.warning(
                "Truncating text content from %d to %d chars",
                len(text_content),
                self.max_text_length,
            )
            block_copy[block_type]["rich_text"][i]["text"]["content"] = text_content[
                : self.max_text_length
            ]

    def split_to_paragraphs(self, markdown_text: str) -> List[str]:
        """Split markdown into paragraphs."""
        paragraphs = re.split(r"\n\s*\n", markdown_text)
        return [p for p in paragraphs if p.strip()]

    def split_to_sentences(self, paragraph: str) -> List[str]:
        """Split a paragraph into sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        return [s for s in sentences if s.strip()]
