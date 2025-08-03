from notionary.blocks.block_models import BlockCreateRequest
from notionary.blocks.column.column_element import ColumnElement
from notionary.blocks.notion_block_element import BlockCreateResult
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.page.formatting.line_processor import LineProcessor

BlockPosition = tuple[int, int, BlockCreateRequest]
BlockPositionList = list[BlockPosition]


class MarkdownToNotionConverter:
    """
    Converts Markdown text to Notion API block format.
    """

    def __init__(self, block_registry: BlockRegistry) -> None:
        self._block_registry = block_registry
        self._setup_column_element_callback()
    
    def _setup_column_element_callback(self) -> None:
        """Setup für ColumnElement falls verfügbar."""
        if self._block_registry.contains(ColumnElement):
            ColumnElement.set_converter_callback(self.convert)
    
    def convert(self, markdown_text: str) -> list[BlockCreateRequest]:
        """Konvertiert Markdown zu Notion-Blöcken."""
        if not markdown_text.strip():
            return []
        
        # Phase 1: Multiline-Blöcke verarbeiten (Tables, Code, etc.)
        multiline_blocks = self._find_multiline_blocks(markdown_text)
        
        # Phase 2: Restliche Zeilen mit Child-Awareness verarbeiten
        excluded_ranges = self._create_excluded_ranges(multiline_blocks)
        
        processor = LineProcessor(self._block_registry, excluded_ranges)
        line_blocks = processor.process_lines(markdown_text)
        
        # Kombiniere und sortiere alle Blöcke
        all_blocks = multiline_blocks + line_blocks
        all_blocks.sort(key=lambda x: x[0])  # Sortiere nach Start-Position
        
        # Extrahiere nur die Block-Objekte
        return [block for _, _, block in all_blocks]
    
    def _find_multiline_blocks(self, text: str) -> list[tuple[int, int, BlockCreateRequest]]:
        """Findet Multiline-Blöcke wie Tables, Code-Blocks, etc."""
        blocks = []
        
        # Nur "einfache" Multiline-Blöcke, keine Toggles/Headings
        simple_multiline_elements = [
            element for element in self._block_registry.get_multiline_elements()
            if element.__name__ not in ['ToggleElement', 'ToggleableHeadingElement']
        ]
        
        for element in simple_multiline_elements:
            matches = element.find_matches(text)
            for start_pos, end_pos, block_result in matches:
                element_blocks = self._normalize_to_list(block_result)
                for block in element_blocks:
                    blocks.append((start_pos, end_pos, block))
        
        return blocks
    
    def _create_excluded_ranges(self, blocks: list[tuple[int, int, BlockCreateRequest]]) -> set[int]:
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