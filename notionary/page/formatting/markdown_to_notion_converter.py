from typing import Any, Callable, Union
from notionary.blocks import ColumnElement, BlockRegistry, NotionBlockElement
from notionary.blocks.block_models import BlockCreateRequest
from notionary.blocks.notion_block_element import BlockCreateResult
from notionary.page.formatting.line_processor import LineProcessor

# Type aliases for better readability
BlockPosition = tuple[int, int, BlockCreateRequest]  # (start_pos, end_pos, block)
BlockPositionList = list[BlockPosition]


class MarkdownToNotionConverter:
    """
    Converts Markdown text to Notion API block format.
    """

    def __init__(self, block_registry: BlockRegistry) -> None:
        self._block_registry = block_registry
        self._pipe_content_pattern = r"^\|\s?(.*)$"
        self._toggle_element_types = ["ToggleElement", "ToggleableHeadingElement"]

        # Setup column element callback if available
        self._setup_column_element_callback()

    def _setup_column_element_callback(self) -> None:
        """Setup the converter callback for ColumnElement if it exists in registry."""
        if self._block_registry.contains(ColumnElement):
            ColumnElement.set_converter_callback(self.convert)

    def convert(self, markdown_text: str) -> list[BlockCreateRequest]:
        """
        Convert markdown text to Notion API block format.
        """
        if not markdown_text.strip():
            return []

        # Step 1: Identify all blocks with their positions
        blocks_with_positions = self._identify_all_blocks(markdown_text)

        # Step 2: Sort blocks by position to maintain document order
        blocks_with_positions.sort(key=lambda block_info: block_info[0])

        # Step 3: Flatten and return block objects
        return self._flatten_blocks(blocks_with_positions)

    def _identify_all_blocks(self, markdown_text: str) -> BlockPositionList:
        """
        Main pipeline to identify all blocks in markdown text.
        """
        all_blocks: BlockPositionList = []

        # Phase 1: Process complex toggleable blocks first
        toggleable_blocks = self._find_toggleable_blocks(markdown_text)
        all_blocks.extend(toggleable_blocks)

        # Phase 2: Process other multiline blocks
        multiline_blocks = self._find_multiline_blocks(
            markdown_text, exclude_blocks=toggleable_blocks
        )
        all_blocks.extend(multiline_blocks)

        # Phase 3: Process remaining text line by line
        processed_blocks = toggleable_blocks + multiline_blocks
        line_blocks = self._process_remaining_lines(markdown_text, processed_blocks)
        all_blocks.extend(line_blocks)

        return all_blocks

    def _find_toggleable_blocks(self, text: str) -> BlockPositionList:
        """
        Find toggle and toggleable heading blocks.
        """
        toggleable_elements = self._get_elements_by_type(
            self._toggle_element_types, multiline_only=True
        )

        blocks: BlockPositionList = []
        for element in toggleable_elements:
            # Use element's find_matches method with conversion callback
            matches = element.find_matches(
                text,
                process_nested_content=self.convert,  # Recursive conversion
                context_aware=True,
            )
            if matches:
                blocks.extend(matches)

        return blocks

    def _find_multiline_blocks(
        self, text: str, exclude_blocks: BlockPositionList
    ) -> BlockPositionList:
        """
        Find multiline blocks like tables, code blocks, columns etc.
        """
        # Get all multiline elements except toggleable ones
        multiline_elements = self._get_non_toggleable_multiline_elements()

        # Create set of excluded positions for efficient lookup
        excluded_ranges = self._create_excluded_ranges(exclude_blocks)

        blocks: BlockPositionList = []
        for element in multiline_elements:
            element_blocks = self._find_element_blocks(element, text, excluded_ranges)
            blocks.extend(element_blocks)

        return blocks

    def _get_non_toggleable_multiline_elements(self) -> list[NotionBlockElement]:
        """Get all multiline elements except toggleable ones."""
        return [
            element
            for element in self._block_registry.get_multiline_elements()
            if element.__name__ not in self._toggle_element_types
        ]

    def _find_element_blocks(
        self, element: NotionBlockElement, text: str, excluded_ranges: set[int]
    ) -> BlockPositionList:
        """
        Find blocks for a specific element type.
        """
        matches = element.find_matches(text)
        blocks: BlockPositionList = []

        for start_pos, end_pos, block_result in matches:
            # Skip if this range overlaps with already processed blocks
            if self._overlaps_with_ranges(start_pos, end_pos, excluded_ranges):
                continue

            # Handle elements that return multiple blocks
            element_blocks = self._normalize_to_list(block_result)

            # Add each block with appropriate position
            current_pos = start_pos
            for i, single_block in enumerate(element_blocks):
                blocks.append((current_pos, end_pos, single_block))
                # Increment position for subsequent blocks from same element
                current_pos = end_pos + i + 1

        return blocks

    def _process_remaining_lines(
        self, text: str, exclude_blocks: BlockPositionList
    ) -> BlockPositionList:
        """
        Process remaining text line by line for simple blocks.
        """
        if not text.strip():
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
    ) -> list[NotionBlockElement]:
        """
        Get block elements from registry by their type names.
            List of matching elements
        """
        elements = (
            self._block_registry.get_multiline_elements()
            if multiline_only
            else self._block_registry.get_elements()
        )

        return [
            element
            for element in elements
            if (element.__name__ in type_names and hasattr(element, "match_markdown"))
        ]

    def _create_excluded_ranges(self, exclude_blocks: BlockPositionList) -> set[int]:
        """
        Create a set of character positions that should be excluded.
        """
        excluded_positions: set[int] = set()
        for start_pos, end_pos, _ in exclude_blocks:
            excluded_positions.update(range(start_pos, end_pos + 1))
        return excluded_positions

    def _overlaps_with_ranges(
        self, start_pos: int, end_pos: int, excluded_ranges: set[int]
    ) -> bool:
        """
        Check if a position range overlaps with excluded positions.
        """
        return any(pos in excluded_ranges for pos in range(start_pos, end_pos + 1))

    def _flatten_blocks(
        self, blocks_with_positions: BlockPositionList
    ) -> list[BlockCreateRequest]:
        """
        Extract and flatten block objects from position information.
        """
        result: list[BlockCreateRequest] = []

        for _, _, block in blocks_with_positions:
            if isinstance(block, list):
                result.extend(block)
            else:
                result.append(block)

        return result

    @staticmethod
    def _normalize_to_list(result: BlockCreateResult) -> list[BlockCreateRequest]:
        """
        Normalize conversion result to a list of block content objects.
        """
        if result is None:
            return []
        return result if isinstance(result, list) else [result]
