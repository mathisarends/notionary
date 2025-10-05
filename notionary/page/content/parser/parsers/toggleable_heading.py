import re
from typing import override

from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import (
    BlockColor,
    BlockCreatePayload,
    BlockType,
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
    CreateHeadingBlock,
    HeadingData,
)
from notionary.page.content.parser.parsers import (
    BlockParsingContext,
    LineParser,
    ParentBlockContext,
)


class ToggleableHeadingParser(LineParser):
    HEADING_START_PATTERN = r"^[+]{3}\s*(?P<level>#{1,3})\s*(.+)$"
    HEADING_END_PATTERN = r"^[+]{3}\s*$"

    def __init__(self, rich_text_converter: MarkdownRichTextConverter | None = None) -> None:
        super().__init__()
        self._start_pattern = re.compile(self.HEADING_START_PATTERN, re.IGNORECASE)
        self._end_pattern = re.compile(self.HEADING_END_PATTERN)
        self._rich_text_converter = rich_text_converter or MarkdownRichTextConverter()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        return (
            self._is_toggleable_heading_start(context)
            or self._is_toggleable_heading_end(context)
            or self._is_toggleable_heading_content(context)
        )

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        """Process toggleable heading start, end, or content with unified handling."""

        async def _handle(action):
            await action(context)
            return True

        if self._is_toggleable_heading_start(context):
            return await _handle(self._start_toggleable_heading)
        if self._is_toggleable_heading_end(context):
            return await _handle(self._finalize_toggleable_heading)
        if self._is_toggleable_heading_content(context):
            return await _handle(self._add_toggleable_heading_content)

    def _is_toggleable_heading_start(self, context: BlockParsingContext) -> bool:
        """Check if line starts a toggleable heading (+++# "Title" or +++#"Title")."""
        return self._start_pattern.match(context.line.strip()) is not None

    def _is_toggleable_heading_end(self, context: BlockParsingContext) -> bool:
        """Check if we need to end a toggleable heading (+++)."""
        if not self._end_pattern.match(context.line.strip()):
            return False

        if not context.parent_stack:
            return False

        # Check if top of stack is a ToggleableHeading
        current_parent = context.parent_stack[-1]
        return self._is_heading_block(current_parent.block)

    def _is_heading_block(self, block) -> bool:
        return isinstance(block, (CreateHeading1Block, CreateHeading2Block, CreateHeading3Block))

    async def _start_toggleable_heading(self, context: BlockParsingContext) -> None:
        block = await self._create_toggleable_heading_block(context.line)
        if not block:
            return

        # Push to parent stack
        parent_context = ParentBlockContext(
            block=block,
            element_type=type(block),
            child_lines=[],
        )
        context.parent_stack.append(parent_context)

    async def _create_toggleable_heading_block(self, line: str) -> CreateHeadingBlock | None:
        """Create a toggleable heading block from markdown line."""
        if not (match := self._start_pattern.match(line.strip())):
            return None

        level = len(match.group("level"))  # Count # characters
        content = match.group(2).strip()  # Title text

        if level < 1 or level > 3 or not content:
            return None

        rich_text = await self._rich_text_converter.to_rich_text(content)
        heading_content = HeadingData(rich_text=rich_text, color=BlockColor.DEFAULT, is_toggleable=True, children=[])

        if level == 1:
            return CreateHeading1Block(heading_1=heading_content)
        elif level == 2:
            return CreateHeading2Block(heading_2=heading_content)
        else:
            return CreateHeading3Block(heading_3=heading_content)

    def _is_toggleable_heading_content(self, context: BlockParsingContext) -> bool:
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        if not self._is_heading_block(current_parent.block):
            return False

        # Handle all content inside toggleable heading (not start/end patterns)
        line = context.line.strip()
        return not (self._start_pattern.match(line) or self._end_pattern.match(line))

    async def _add_toggleable_heading_content(self, context: BlockParsingContext) -> None:
        """Add content to the current toggleable heading context."""
        context.parent_stack[-1].add_child_line(context.line)

    async def _finalize_toggleable_heading(self, context: BlockParsingContext) -> None:
        """Finalize a toggleable heading block and add it to result_blocks."""
        heading_context = context.parent_stack.pop()
        await self._assign_heading_children_if_any(heading_context, context)

        # Check if we have a parent context to add this heading to
        if context.parent_stack:
            parent_context = context.parent_stack[-1]
            parent_context.add_child_block(heading_context.block)
        else:
            # No parent, add to top level
            context.result_blocks.append(heading_context.block)

    async def _assign_heading_children_if_any(
        self, heading_context: ParentBlockContext, context: BlockParsingContext
    ) -> None:
        """Collect and assign any children blocks inside this heading."""
        all_children = []

        # Process text lines
        if heading_context.child_lines:
            children_text = "\n".join(heading_context.child_lines)
            text_blocks = await self._parse_nested_content(children_text, context)
            all_children.extend(text_blocks)

        # Add direct child blocks
        if heading_context.child_blocks:
            all_children.extend(heading_context.child_blocks)

        self._assign_children_to_heading(heading_context.block, all_children)

    def _assign_children_to_heading(self, parent_block: BlockCreatePayload, children: list[BlockCreatePayload]) -> None:
        """Assign children to toggleable heading blocks."""
        block_type = parent_block.type

        if block_type == BlockType.HEADING_1:
            parent_block.heading_1.children = children
        elif block_type == BlockType.HEADING_2:
            parent_block.heading_2.children = children
        elif block_type == BlockType.HEADING_3:
            parent_block.heading_3.children = children

    async def _parse_nested_content(self, text: str, context: BlockParsingContext) -> list:
        if not text.strip():
            return []

        return await context.parse_nested_content(text)
