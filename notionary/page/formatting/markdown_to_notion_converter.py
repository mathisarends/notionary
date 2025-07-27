from notionary.blocks import ColumnElement, BlockRegistry
from notionary.page.formatting.line_processor import LineProcessor

# TODO: Hier rekursiven Baum Parser verwenden!
class MarkdownToNotionConverter:
    """Clean converter focused on block identification and conversion"""

    def __init__(self, block_registry: BlockRegistry):
        self._block_registry = block_registry
        self._pipe_content_pattern = r"^\|\s?(.*)$"
        self._toggle_element_types = ["ToggleElement", "ToggleableHeadingElement"]

        # Setup column element callback if available
        if self._block_registry.contains(ColumnElement):
            ColumnElement.set_converter_callback(self.convert)

    def convert(self, markdown_text: str) -> list[dict[str, any]]:
        """Convert markdown text to Notion API block format"""
        if not markdown_text:
            return []

        # Main conversion pipeline
        blocks_with_positions = self._identify_all_blocks(markdown_text)
        blocks_with_positions.sort(key=lambda x: x[0])  # Sort by position

        # Flatten blocks (some elements return lists of blocks)
        result = []
        for _, _, block in blocks_with_positions:
            if isinstance(block, list):
                result.extend(block)
            else:
                result.append(block)
        return result

    def _identify_all_blocks(
        self, markdown_text: str
    ) -> list[tuple[int, int, dict[str, any]]]:
        """Main block identification pipeline"""
        all_blocks = []

        # 1. Process complex multiline blocks first (toggles, etc.)
        toggleable_blocks = self._find_toggleable_blocks(markdown_text)
        all_blocks.extend(toggleable_blocks)

        # 2. Process other multiline blocks
        multiline_blocks = self._find_multiline_blocks(markdown_text, toggleable_blocks)
        all_blocks.extend(multiline_blocks)

        # 3. Process remaining text line by line
        processed_blocks = toggleable_blocks + multiline_blocks
        line_blocks = self._process_remaining_lines(markdown_text, processed_blocks)
        all_blocks.extend(line_blocks)

        return all_blocks

    def _find_toggleable_blocks(
        self, text: str
    ) -> list[tuple[int, int, dict[str, any]]]:
        """Find all toggleable blocks (Toggle and ToggleableHeading)"""
        toggleable_elements = self._get_elements_by_type(
            self._toggle_element_types, multiline_only=True
        )

        blocks = []
        for element in toggleable_elements:
            matches = element.find_matches(text, self.convert, context_aware=True)
            if matches:
                blocks.extend(matches)

        return blocks

    def _find_multiline_blocks(
        self, text: str, exclude_blocks: list[tuple[int, int, dict[str, any]]]
    ) -> list[tuple[int, int, dict[str, any]]]:
        """Find all multiline blocks except toggleable ones"""
        multiline_elements = [
            element
            for element in self._block_registry.get_multiline_elements()
            if element.__name__ not in self._toggle_element_types
        ]

        excluded_ranges = self._create_excluded_ranges(exclude_blocks)

        blocks = []
        for element in multiline_elements:
            matches = element.find_matches(text)

            for start_pos, end_pos, block in matches:
                if not self._overlaps_with_ranges(start_pos, end_pos, excluded_ranges):
                    # Handle multiple blocks from single element
                    element_blocks = self._normalize_to_list(block)

                    current_pos = start_pos
                    for i, single_block in enumerate(element_blocks):
                        blocks.append((current_pos, end_pos, single_block))
                        # Increment position for subsequent blocks
                        current_pos = end_pos + i + 1

        return blocks

    def _process_remaining_lines(
        self, text: str, exclude_blocks: list[tuple[int, int, dict[str, any]]]
    ) -> list[tuple[int, int, dict[str, any]]]:
        """Process text line by line, excluding already processed ranges"""
        if not text:
            return []

        excluded_ranges = self._create_excluded_ranges(exclude_blocks)
        processor = LineProcessor(
            block_registry=self._block_registry,
            excluded_ranges=excluded_ranges,
            pipe_pattern=self._pipe_content_pattern,
        )

        return processor.process_lines(text)

    def _get_elements_by_type(
        self, type_names: list[str], multiline_only: bool = False
    ) -> list[any]:
        """Get elements from registry by type names"""
        elements = (
            self._block_registry.get_multiline_elements()
            if multiline_only
            else self._block_registry.get_elements()
        )

        return [
            element
            for element in elements
            if element.__name__ in type_names and hasattr(element, "match_markdown")
        ]

    def _create_excluded_ranges(
        self, exclude_blocks: list[tuple[int, int, dict[str, any]]]
    ) -> set[int]:
        """Create set of excluded positions from block ranges"""
        excluded_positions = set()
        for start_pos, end_pos, _ in exclude_blocks:
            excluded_positions.update(range(start_pos, end_pos + 1))
        return excluded_positions

    def _overlaps_with_ranges(
        self, start_pos: int, end_pos: int, excluded_ranges: set[int]
    ) -> bool:
        """Check if a range overlaps with excluded positions"""
        return any(pos in excluded_ranges for pos in range(start_pos, end_pos + 1))

    @staticmethod
    def _normalize_to_list(result) -> list[dict[str, any]]:
        """Normalize Union[list[dict], dict] to list[dict]"""
        if result is None:
            return []
        return result if isinstance(result, list) else [result]
