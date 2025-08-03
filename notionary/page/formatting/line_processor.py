from __future__ import annotations
import re
from typing import TYPE_CHECKING
from dataclasses import dataclass

from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.page.formatting.block_position import PositionedBlockList

if TYPE_CHECKING:
    from notionary.blocks.block_models import BlockCreateRequest, BlockCreateResult


@dataclass
class ParentBlockContext:
    """Context for a block that expects children."""

    block: BlockCreateRequest
    element_type: NotionBlockElement
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
    """Stack-based LineProcessor with unified | prefix logic - SIMPLE!"""

    def __init__(self, block_registry: BlockRegistry, excluded_ranges: set[int]):
        self._block_registry = block_registry
        self._excluded_ranges = excluded_ranges
        self._parent_stack: list[ParentBlockContext] = []

        # ALLE Elemente die Children haben können, verwenden NUR das "|" Präfix
        # Keine spezielle Behandlung mehr für :::
        self._child_prefixes = {
            "ToggleElement": "|",
            "ToggleableHeadingElement": "|",
            "ColumnListElement": "|",  
            "ColumnElement": "|",     
        }

    def process_lines(self, text: str) -> PositionedBlockList:
        """Processes lines with unified | child support - NO SPECIAL ::: HANDLING!"""
        lines = text.split("\n")
        result_blocks = PositionedBlockList()
        current_pos = 0

        for line in lines:
            line_length = len(line) + 1
            line_end = current_pos + line_length - 1

            if self._overlaps_with_excluded(current_pos, line_end):
                current_pos += line_length
                continue

            # Prüfe auf Child-Content (mit | Präfix) - GENAU WIE BEI TOGGLES
            if self._try_process_as_child(line):
                current_pos += line_length
                continue

            # Finalisiere offene Parents bevor neue Blocks verarbeitet werden
            self._finalize_open_parents(result_blocks, current_pos)

            if line.strip():
                block_created = self._process_regular_line(
                    line, current_pos, line_end, result_blocks
                )
                if not block_created:
                    self._process_as_paragraph(
                        line, current_pos, line_end, result_blocks
                    )

            current_pos += line_length

        self._finalize_open_parents(result_blocks, current_pos)
        return result_blocks

    def _try_process_as_child(self, line: str) -> bool:
        """Process as child content - EXACTLY like toggles."""
        if not self._parent_stack:
            return False

        current_parent = self._parent_stack[-1]
        child_prefix = current_parent.child_prefix

        # Das bewährte Toggle-System - einfach und funktioniert!
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
        """Process a regular line and check for parent blocks."""

        for element in self._block_registry.get_elements():
            if not element.match_markdown(line):
                continue

            result = element.markdown_to_notion(line)
            blocks = self._normalize_to_list(result)

            if not blocks:
                continue

            for block in blocks:
                if not self._can_have_children(block, element):
                    result_blocks.add(current_pos, line_end, block)
                else:
                    child_prefix = self._get_child_prefix(element)

                    context = ParentBlockContext(
                        block=block,
                        element_type=element,
                        child_prefix=child_prefix,
                        child_lines=[],
                        start_position=current_pos,
                    )
                    self._parent_stack.append(context)

            return True

        return False

    def _finalize_open_parents(
        self, result_blocks: PositionedBlockList, current_pos: int
    ):
        """Finalize all open parent blocks - EXACTLY like toggles."""
        while self._parent_stack:
            context = self._parent_stack.pop()

            if context.has_children():
                children_text = "\n".join(context.child_lines)
                children_blocks = self._convert_children_text(children_text)
                
                if context.element_type.__name__ == "ColumnListElement":
                    # Filter Column-Blöcke für ColumnList
                    column_children = [block for block in children_blocks 
                                     if (hasattr(block, 'column') and 
                                         getattr(block, 'type', None) == 'column')]
                    context.block.column_list.children = column_children
                else:
                    self._assign_children(context.block, children_blocks)

            result_blocks.add(context.start_position, current_pos, context.block)

    def _process_as_paragraph(
        self,
        line: str,
        current_pos: int,
        line_end: int,
        result_blocks: PositionedBlockList,
    ):
        """Process a line as a paragraph."""
        result = self._block_registry.markdown_to_notion(line)
        blocks = self._normalize_to_list(result)
        for block in blocks:
            result_blocks.add(current_pos, line_end, block)

    def _can_have_children(
        self, block: BlockCreateRequest, element: NotionBlockElement
    ) -> bool:
        """Check if a block can have children."""
        element_name = element.__name__
        if element_name in self._child_prefixes:
            return True

        if hasattr(block, "toggle") and hasattr(block.toggle, "children"):
            return True
        if hasattr(block, "column_list") and hasattr(block.column_list, "children"):
            return True
        if hasattr(block, "column") and hasattr(block.column, "children"):
            return True
        if hasattr(block, "heading_1") and hasattr(block.heading_1, "children"):
            return True
        if hasattr(block, "heading_2") and hasattr(block.heading_2, "children"):
            return True
        if hasattr(block, "heading_3") and hasattr(block.heading_3, "children"):
            return True

        return False

    def _get_child_prefix(self, element: NotionBlockElement) -> str:
        """Determine the child prefix for the element type."""
        element_name = element.__name__
        return self._child_prefixes.get(element_name, "|")

    def _convert_children_text(self, text: str) -> list[BlockCreateRequest]:
        """Recursively convert children text."""
        if not text.strip():
            return []
        child_processor = LineProcessor(self._block_registry, set())
        child_results = child_processor.process_lines(text)
        return child_results.extract_blocks()

    def _assign_children(
        self, parent_block: BlockCreateRequest, children: list[BlockCreateRequest]
    ):
        """Assign children to a parent block."""

        if hasattr(parent_block, "toggle") and hasattr(parent_block.toggle, "children"):
            parent_block.toggle.children = children
            return

        if hasattr(parent_block, "column_list") and hasattr(
            parent_block.column_list, "children"
        ):
            parent_block.column_list.children = children
            return

        if hasattr(parent_block, "column") and hasattr(parent_block.column, "children"):
            parent_block.column.children = children
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
            return

        if hasattr(parent_block, "children"):
            parent_block.children = children

    def _overlaps_with_excluded(self, start_pos: int, end_pos: int) -> bool:
        """Check for overlap with excluded ranges."""
        return any(
            pos in self._excluded_ranges for pos in range(start_pos, end_pos + 1)
        )

    @staticmethod
    def _normalize_to_list(result: BlockCreateResult) -> list[BlockCreateRequest]:
        """Normalize the result to a list."""
        if result is None:
            return []
        return result if isinstance(result, list) else [result]