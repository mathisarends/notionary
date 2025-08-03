from notionary.blocks.block_models import BlockCreateRequest
from notionary.blocks.column.column_element import ColumnElement
from notionary.blocks.notion_block_element import BlockCreateResult
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.page.formatting.line_processor import LineProcessor
from notionary.page.content.notion_text_length_utils import fix_blocks_content_length

# Type aliases for better readability
BlockPosition = tuple[int, int, BlockCreateRequest]  # (start_pos, end_pos, block)
BlockPositionList = list[BlockPosition]


class MarkdownToNotionConverter:
    """
    Converts Markdown text to Notion API block format.
    """

    def __init__(self, block_registry: BlockRegistry) -> None:
        self._block_registry = block_registry

    def convert(self, markdown_text: str) -> list[BlockCreateRequest]:
        """Konvertiert Markdown zu Notion-Blöcken."""
        if not markdown_text.strip():
            return []

        multiline_blocks = self._find_multiline_blocks(markdown_text)

        excluded_ranges = self._create_excluded_ranges(multiline_blocks)

        processor = LineProcessor(self._block_registry, excluded_ranges)
        line_blocks = processor.process_lines(markdown_text)

        all_blocks = multiline_blocks + line_blocks
        all_blocks.sort(key=lambda x: x[0])

        blocks = [block for _, _, block in all_blocks]

        return fix_blocks_content_length(blocks)

    def _find_multiline_blocks(
        self, text: str
    ) -> list[tuple[int, int, BlockCreateRequest]]:
        """Findet Multiline-Blöcke wie Tables, Code-Blocks, etc."""
        blocks = []

        multiline_elements = self._block_registry.get_multiline_elements()

        for element in multiline_elements:
            matches = element.find_matches(text)
            for start_pos, end_pos, block_result in matches:
                element_blocks = self._normalize_to_list(block_result)
                for block in element_blocks:
                    blocks.append((start_pos, end_pos, block))

        return blocks

    def _create_excluded_ranges(
        self, blocks: list[tuple[int, int, BlockCreateRequest]]
    ) -> set[int]:
        """Erstellt Set ausgeschlossener Positionen."""
        excluded = set()
        for start_pos, end_pos, _ in blocks:
            excluded.update(range(start_pos, end_pos + 1))
        return excluded

    @staticmethod
    def _normalize_to_list(result: BlockCreateResult) -> list[BlockCreateRequest]:
        """Normalisiert Ergebnis zu Liste."""
        if result is None:
            return []
        return result if isinstance(result, list) else [result]
