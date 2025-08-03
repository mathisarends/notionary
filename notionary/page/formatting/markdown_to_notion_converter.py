from __future__ import annotations
from typing import TYPE_CHECKING

from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.page.formatting.block_position import PositionedBlockList
from notionary.page.formatting.line_processor import LineProcessor
from notionary.page.content.notion_text_length_utils import fix_blocks_content_length

if TYPE_CHECKING:
    from notionary.blocks.block_models import BlockCreateRequest, BlockCreateResult


class MarkdownToNotionConverter:
    """Converts Markdown text to Notion API block format."""

    def __init__(self, block_registry: BlockRegistry) -> None:
        self._block_registry = block_registry

    def convert(self, markdown_text: str) -> list[BlockCreateRequest]:
        """Konvertiert Markdown zu Notion-Blöcken."""
        if not markdown_text.strip():
            return []

        multiline_blocks = self._find_multiline_blocks(markdown_text)

        excluded_ranges = multiline_blocks.get_excluded_ranges()
        processor = LineProcessor(self._block_registry, excluded_ranges)
        line_blocks = processor.process_lines(markdown_text)

        all_blocks = PositionedBlockList()
        all_blocks.extend(multiline_blocks)
        all_blocks.extend(line_blocks)
        all_blocks.sort_by_position()

        blocks = all_blocks.extract_blocks()
        return fix_blocks_content_length(blocks)

    def _find_multiline_blocks(self, text: str) -> PositionedBlockList:
        """Findet Multiline-Blöcke direkt als PositionedBlockList."""
        all_positioned_blocks = PositionedBlockList()

        multiline_elements = self._block_registry.get_multiline_elements()

        for element in multiline_elements:
            element_blocks = element.find_matches(text)

            all_positioned_blocks.extend(element_blocks)

        return all_positioned_blocks

    @staticmethod
    def _normalize_to_list(result: BlockCreateResult) -> list[BlockCreateRequest]:
        """Normalisiert Ergebnis zu Liste."""
        if result is None:
            return []
        return result if isinstance(result, list) else [result]
