from dataclasses import dataclass
import re
from notionary.blocks.block_models import BlockCreateRequest
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.notion_block_element import BlockCreateResult, NotionBlockElement
from notionary.page.formatting.block_position import PositionedBlockList


@dataclass
class ParentBlockContext:
    """Context for a block that expects children."""

    block: BlockCreateRequest
    element_type: type
    child_prefix: str
    child_lines: list[str]
    start_position: int

    def add_child_line(self, content: str):
        """Adds a child line."""
        self.child_lines.append(content)

    def has_children(self) -> bool:
        """Checks if children have been collected."""
        return len(self.child_lines) > 0


class LineProcessor:
    """Handles line-by-line processing of markdown text."""

    def __init__(self, block_registry: BlockRegistry, excluded_ranges: set[int]):
        self._block_registry = block_registry
        self._excluded_ranges = excluded_ranges
        self._parent_stack: list[ParentBlockContext] = []

        self._child_prefixes = {
            "ToggleElement": "|",
            "ToggleableHeadingElement": "|",
        }

    def process_lines(self, text: str) -> PositionedBlockList:
        """Processes lines with automatic child support - returns PositionedBlockList directly."""
        lines = text.split("\n")
        result_blocks = PositionedBlockList()
        current_pos = 0

        for line in lines:
            line_length = len(line) + 1  # +1 für newline
            line_end = current_pos + line_length - 1

            # Skip excluded ranges
            if self._overlaps_with_excluded(current_pos, line_end):
                current_pos += line_length
                continue

            # Versuche Child-Content zu verarbeiten
            if self._try_process_as_child(line):
                current_pos += line_length
                continue

            # Finalisiere alle offenen Parent-Blöcke bei neuer nicht-Child-Zeile
            self._finalize_open_parents(result_blocks, current_pos)

            # Verarbeite normale Zeile
            if line.strip():  # Nicht-leere Zeile
                block_created = self._process_regular_line(
                    line, current_pos, line_end, result_blocks
                )
                if not block_created:
                    # Falls kein spezieller Block, als Paragraph behandeln
                    self._process_as_paragraph(
                        line, current_pos, line_end, result_blocks
                    )

            current_pos += line_length

        # Finalisiere alle noch offenen Parents
        self._finalize_open_parents(result_blocks, current_pos)

        return result_blocks

    def _try_process_as_child(self, line: str) -> bool:
        """Tries to process a line as child content."""
        if not self._parent_stack:
            return False

        current_parent = self._parent_stack[-1]
        child_prefix = current_parent.child_prefix

        # Prüfe ob Zeile mit Child-Prefix beginnt
        child_pattern = re.compile(rf"^{re.escape(child_prefix)}\s?(.*?)$")
        match = child_pattern.match(line)

        if match:
            child_content = match.group(1)
            current_parent.add_child_line(child_content)
            return True

        return False

    def _process_regular_line(
        self,
        line: str,
        current_pos: int,
        line_end: int,
        result_blocks: PositionedBlockList,
    ) -> bool:
        """Processes a regular line and checks for parent blocks."""

        # Suche passende Element-Klasse
        for element in self._block_registry.get_elements():
            if not element.match_markdown(line):
                continue

            # Erstelle Block
            result = element.markdown_to_notion(line)
            blocks = self._normalize_to_list(result)

            if not blocks:
                continue

            # Verarbeite jeden erstellten Block
            for block in blocks:
                if not self._can_have_children(block, element):
                    result_blocks.add(current_pos, line_end, block)
                else:
                    child_prefix = self._get_child_prefix(element)
                    context = ParentBlockContext(
                        block=block,
                        element_type=type(element),
                        child_prefix=child_prefix,
                        child_lines=[],
                        start_position=current_pos,
                    )
                    self._parent_stack.append(context)

            return True

        return False

    def _process_as_paragraph(
        self,
        line: str,
        current_pos: int,
        line_end: int,
        result_blocks: PositionedBlockList,
    ):
        """Processes a line as a paragraph."""
        result = self._block_registry.markdown_to_notion(line)
        blocks = self._normalize_to_list(result)

        for block in blocks:
            result_blocks.add(current_pos, line_end, block)

    def _can_have_children(
        self, block: BlockCreateRequest, element: NotionBlockElement
    ) -> bool:
        """Checks if a block can have children."""
        # 1. Prüfe ob Element-Typ bekanntermaßen Children haben kann
        element_name = element.__name__
        if element_name in self._child_prefixes:
            return True

        # 2. Prüfe Block-Struktur auf children-Eigenschaft
        if hasattr(block, "toggle") and hasattr(block.toggle, "children"):
            return True

        if hasattr(block, "heading_1") and hasattr(block.heading_1, "children"):
            return True

        if hasattr(block, "heading_2") and hasattr(block.heading_2, "children"):
            return True

        if hasattr(block, "heading_3") and hasattr(block.heading_3, "children"):
            return True

        return False

    def _get_child_prefix(self, element: NotionBlockElement) -> str:
        """Determines the child prefix for the element type."""
        element_name = element.__class__.__name__
        return self._child_prefixes.get(element_name, "|")  # Default: "|"

    def _finalize_open_parents(
        self, result_blocks: PositionedBlockList, current_pos: int
    ):
        """Finalizes all open parent blocks."""
        while self._parent_stack:
            context = self._parent_stack.pop()

            if context.has_children():
                children_text = "\n".join(context.child_lines)
                children_blocks = self._convert_children_text(children_text)

                self._assign_children(context.block, children_blocks)

            result_blocks.add(context.start_position, current_pos, context.block)

    def _convert_children_text(self, text: str) -> list[BlockCreateRequest]:
        """Recursively converts children text."""
        if not text.strip():
            return []

        child_processor = LineProcessor(self._block_registry, set())
        child_results = child_processor.process_lines(text)

        return child_results.extract_blocks()

    def _assign_children(
        self, parent_block: BlockCreateRequest, children: list[BlockCreateRequest]
    ):
        """Assigns children to a parent block."""
        if hasattr(parent_block, "toggle") and hasattr(parent_block.toggle, "children"):
            parent_block.toggle.children = children
            return

        if hasattr(parent_block, "heading_1") and hasattr(
            parent_block.heading_1, "children"
        ):
            parent_block.heading_1.children = children
            return

        if hasattr(parent_block, "heading_2") and hasattr(
            parent_block.heading_2, "children"
        ):
            parent_block.heading_2.children = children
            return

        if hasattr(parent_block, "heading_3") and hasattr(
            parent_block.heading_3, "children"
        ):
            parent_block.heading_3.children = children

    def _overlaps_with_excluded(self, start_pos: int, end_pos: int) -> bool:
        """Checks for overlap with excluded ranges."""
        return any(
            pos in self._excluded_ranges for pos in range(start_pos, end_pos + 1)
        )

    @staticmethod
    def _normalize_to_list(result: BlockCreateResult) -> list[BlockCreateRequest]:
        """Normalizes the result to a list."""
        if result is None:
            return []
        return result if isinstance(result, list) else [result]
