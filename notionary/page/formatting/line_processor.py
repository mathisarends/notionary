from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass, field


from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.column.column_models import CreateColumnBlock, ColumnBlock
from notionary.page.formatting.block_position import PositionedBlockList

if TYPE_CHECKING:
    from notionary.blocks.block_models import BlockCreateRequest, BlockCreateResult


@dataclass
class ColumnContext:
    """Context für eine einzelne Spalte."""

    content_lines: list[str]

    def add_line(self, line: str):
        """Fügt eine Zeile zur Spalte hinzu."""
        self.content_lines.append(line)

    def has_content(self) -> bool:
        """Prüft ob die Spalte Inhalt hat."""
        return len(self.content_lines) > 0


@dataclass
class ParentBlockContext:
    """Context for a block that expects children."""

    block: BlockCreateRequest
    element_type: type
    child_prefix: str
    child_lines: list[str]
    start_position: int

    is_column_list: bool = False
    current_column: Optional[ColumnContext] = None
    completed_columns: list[ColumnContext] = field(default_factory=list)

    def __post_init__(self):
        if self.completed_columns is None:
            self.completed_columns = []

    def add_child_line(self, content: str):
        """Adds a child line."""
        self.child_lines.append(content)

    def has_children(self) -> bool:
        """Checks if children have been collected."""
        return len(self.child_lines) > 0 or len(self.completed_columns) > 0

    def start_new_column(self):
        """Startet eine neue Spalte."""
        if self.current_column and self.current_column.has_content():
            self.completed_columns.append(self.current_column)
        self.current_column = ColumnContext(content_lines=[])

    def add_to_current_column(self, line: str):
        """Fügt Zeile zur aktuellen Spalte hinzu."""
        if not self.current_column:
            self.start_new_column()
        self.current_column.add_line(line)

    def finalize_current_column(self):
        """Finalisiert die aktuelle Spalte."""
        if self.current_column and self.current_column.has_content():
            self.completed_columns.append(self.current_column)
            self.current_column = None


class LineProcessor:
    """Enhanced LineProcessor mit Column-Stack-Support."""

    def __init__(self, block_registry: BlockRegistry, excluded_ranges: set[int]):
        self._block_registry = block_registry
        self._excluded_ranges = excluded_ranges
        self._parent_stack: list[ParentBlockContext] = []

        self._child_prefixes = {
            "ToggleElement": "|",
            "ToggleableHeadingElement": "|",
            "ColumnElement": ":::",
        }

        # 🎯 Column-spezifische Patterns
        self._column_start_pattern = re.compile(r"^:::\s*column\s*$")
        self._column_end_pattern = re.compile(r"^:::\s*$")

    def process_lines(self, text: str) -> PositionedBlockList:
        """Processes lines with automatic child support including columns."""
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

            # 🎯 Versuche Column-spezifische Verarbeitung
            if self._try_process_as_column_syntax(line):
                current_pos += line_length
                continue

            # Versuche normale Child-Content Verarbeitung
            if self._try_process_as_child(line):
                current_pos += line_length
                continue

            # Finalisiere alle offenen Parent-Blöcke
            self._finalize_open_parents(result_blocks, current_pos)

            # Verarbeite normale Zeile
            if line.strip():
                block_created = self._process_regular_line(
                    line, current_pos, line_end, result_blocks
                )
                if not block_created:
                    self._process_as_paragraph(
                        line, current_pos, line_end, result_blocks
                    )

            current_pos += line_length

        # Finalisiere alle noch offenen Parents
        self._finalize_open_parents(result_blocks, current_pos)
        return result_blocks

    def _try_process_as_column_syntax(self, line: str) -> bool:
        """🎯 Verarbeitet Column-spezifische Syntax."""
        if not self._parent_stack:
            return False

        current_parent = self._parent_stack[-1]

        # Nur für ColumnElement relevant
        if not current_parent.is_column_list:
            return False

        stripped_line = line.strip()

        # `::: column` - Neue Spalte starten
        if self._column_start_pattern.match(stripped_line):
            current_parent.start_new_column()
            return True

        if self._column_end_pattern.match(stripped_line):
            if current_parent.current_column:
                current_parent.finalize_current_column()
            return True

        if current_parent.current_column is not None:
            current_parent.add_to_current_column(line)
            return True

        return False

    def _try_process_as_child(self, line: str) -> bool:
        """Verarbeitet normale Child-Content (Toggle, Heading)."""
        if not self._parent_stack:
            return False

        current_parent = self._parent_stack[-1]

        # Skip Column-Verarbeitung
        if current_parent.is_column_list:
            return False

        child_prefix = current_parent.child_prefix
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
                    is_column_element = element.__name__ == "ColumnElement"

                    context = ParentBlockContext(
                        block=block,
                        element_type=type(element),
                        child_prefix=child_prefix,
                        child_lines=[],
                        start_position=current_pos,
                        is_column_list=is_column_element,
                    )
                    self._parent_stack.append(context)

            return True

        return False

    def _finalize_open_parents(
        self, result_blocks: PositionedBlockList, current_pos: int
    ):
        """Finalizes all open parent blocks including columns."""
        while self._parent_stack:
            context = self._parent_stack.pop()

            if context.is_column_list:
                self._finalize_column_list(context)
            elif context.has_children():
                children_text = "\n".join(context.child_lines)
                children_blocks = self._convert_children_text(children_text)
                self._assign_children(context.block, children_blocks)

            result_blocks.add(context.start_position, current_pos, context.block)

    def _finalize_column_list(self, context: ParentBlockContext):
        """Finalizes a ColumnList with correct structure."""
        context.finalize_current_column()

        column_blocks = []
        for column_context in context.completed_columns:
            column_text = "\n".join(column_context.content_lines)
            column_children = self._convert_children_text(column_text) if column_context.has_content() else []
            
            column_block = CreateColumnBlock(
                column=ColumnBlock(column_ratio=None, children=column_children)
            )
            
            column_blocks.append(column_block)

        context.block.column_list.children = column_blocks

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
        element_name = element.__name__
        if element_name in self._child_prefixes:
            return True

        if hasattr(block, "toggle") and hasattr(block.toggle, "children"):
            return True
        if hasattr(block, "column_list") and hasattr(block.column_list, "children"):
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
        return self._child_prefixes.get(element_name, "|")

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

        if hasattr(parent_block, "column_list") and hasattr(
            parent_block.column_list, "children"
        ):
            # 🎯 Für ColumnList: children sind die CreateColumnBlock Objekte
            parent_block.column_list.children = children
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

        # Fallback: Direkte children
        if hasattr(parent_block, "children"):
            parent_block.children = children

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
