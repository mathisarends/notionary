import re
from typing import Any, Dict, List, Optional

from notionary.core.converters.markdown_to_notion_converter import (
    MarkdownToNotionConverter,
)
from notionary.core.converters.notion_to_markdown_converter import (
    NotionToMarkdownConverter,
)
from notionary.core.converters.registry.block_element_registry import (
    BlockElementRegistry,
)
from notionary.core.notion_client import NotionClient
from notionary.core.page.content.notion_page_content_chunker import (
    NotionPageContentChunker,
)
from notionary.util.logging_mixin import LoggingMixin


class PageContentManager(LoggingMixin):
    def __init__(
        self,
        page_id: str,
        client: NotionClient,
        block_registry: Optional[BlockElementRegistry] = None,
    ):
        self.page_id = page_id
        self._client = client
        self._markdown_to_notion_converter = MarkdownToNotionConverter(
            block_registry=block_registry
        )
        self._notion_to_markdown_converter = NotionToMarkdownConverter(
            block_registry=block_registry
        )
        self._chunker = NotionPageContentChunker()

    async def append_markdown(self, markdown_text: str) -> str:
        """
        Append markdown text to a Notion page, automatically handling content length limits.
        """
        try:
            blocks = self._markdown_to_notion_converter.convert(markdown_text)

            fixed_blocks = self._chunker.fix_blocks_content_length(blocks)

            result = await self._client.patch(
                f"blocks/{self.page_id}/children", {"children": fixed_blocks}
            )
            return (
                "Successfully added text to the page."
                if result
                else "Failed to add text."
            )
        except Exception as e:
            error_str = str(e)
            self.logger.error("Error appending markdown: %s", error_str)

            if (
                "400" in error_str
                and "validation_error" in error_str
                and "content.length" in error_str
            ):
                return await self._handle_content_length_error(markdown_text, error_str)

            raise

    async def _handle_content_length_error(
        self, markdown_text: str, error_str: str
    ) -> str:
        """Handle content length validation errors by chunking the markdown."""
        path_match = re.search(
            r"body\.children\[(\d+)\](.+?)content\.length", error_str
        )
        if not path_match:
            return f"Failed to parse error: {error_str}"

        self.logger.info("Splitting markdown and trying again")

        paragraphs = self._chunker.split_to_paragraphs(markdown_text)
        return await self._append_chunks(paragraphs)

    async def _append_chunks(self, chunks: List[str]) -> str:
        """Append a list of markdown chunks, with fallback to sentence chunking if needed."""
        success_count = 0
        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks):
            try:
                blocks = self._markdown_to_notion_converter.convert(chunk)
                fixed_blocks = self._chunker.fix_blocks_content_length(blocks)

                result = await self._client.patch(
                    f"blocks/{self.page_id}/children", {"children": fixed_blocks}
                )

                if result:
                    success_count += 1
                else:
                    self.logger.error("Failed to add chunk %d/%d", i + 1, total_chunks)

            except Exception as e:
                self.logger.error(
                    "Error appending chunk %d/%d: %s", i + 1, total_chunks, str(e)
                )

                if "content.length" in str(e):
                    await self._append_sentences(chunk)

        return f"Processed content in {success_count}/{total_chunks} chunks"

    async def _append_sentences(self, paragraph: str) -> None:
        """Split a paragraph into sentences and append each one separately."""
        sentences = self._chunker.split_to_sentences(paragraph)

        for sentence in sentences:
            if not sentence.strip():
                continue

            try:
                sentence_blocks = self._markdown_to_notion_converter.convert(sentence)
                fixed_blocks = self._chunker.fix_blocks_content_length(sentence_blocks)

                await self._client.patch(
                    f"blocks/{self.page_id}/children", {"children": fixed_blocks}
                )

            except Exception as e:
                self.logger.error("Failed to append sentence: %s", str(e))

    async def clear(self) -> str:
        blocks = await self._client.get(f"blocks/{self.page_id}/children")
        if not blocks:
            return "No content to delete."

        results = blocks.get("results", [])
        if not results:
            return "No content to delete."

        deleted = 0
        skipped = 0
        for block in results:
            if block.get("type") in ["child_database", "database", "linked_database"]:
                skipped += 1
                continue

            if await self._client.delete(f"blocks/{block['id']}"):
                deleted += 1

        return f"Deleted {deleted}/{len(results)} blocks. Skipped {skipped} database blocks."

    async def get_blocks(self) -> List[Dict[str, Any]]:
        result = await self._client.get(f"blocks/{self.page_id}/children")
        if not result:
            self.logger.error("Error retrieving page content: %s", result.error)
            return []
        return result.get("results", [])

    async def get_block_children(self, block_id: str) -> List[Dict[str, Any]]:
        result = await self._client.get(f"blocks/{block_id}/children")
        if not result:
            self.logger.error("Error retrieving block children: %s", result.error)
            return []
        return result.get("results", [])

    async def get_page_blocks_with_children(self) -> List[Dict[str, Any]]:
        blocks = await self.get_blocks()
        for block in blocks:
            if block.get("has_children"):
                block_id = block.get("id")
                if block_id:
                    children = await self.get_block_children(block_id)
                    if children:
                        block["children"] = children
        return blocks

    async def get_text(self) -> str:
        blocks = await self.get_page_blocks_with_children()
        return self._notion_to_markdown_converter.convert(blocks)
