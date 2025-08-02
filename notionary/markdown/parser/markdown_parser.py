from typing import Any, Optional
from notionary.blocks.block_models import BlockCreateRequest
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.markdown.parser.block_parsing_capabilites import (
    BlockContext,
    BlockParsingCapabilities,
    ParseAction,
    ParseActionType,
    RootBlockContext,
)


class CapabilityBasedMarkdownParser:
    """
    Unified parser using capability-based design and context stack.
    """

    def __init__(self, block_registry: BlockRegistry):
        self.registry = block_registry
        self.context_stack: list[BlockContext] = [RootBlockContext()]

    def convert(self, markdown_text: str) -> list[BlockCreateRequest]:
        """
        Convert markdown text to Notion API block format using capabilities.
        """
        if not markdown_text.strip():
            return []

        # Reset context stack
        self.context_stack = [RootBlockContext()]

        # Get elements sorted by priority (highest first)
        elements = self._get_elements_by_priority()

        # Single pass through text with context awareness
        return self._parse_with_context_stack(markdown_text, elements)

    def _parse_with_context_stack(
        self, text: str, elements: list[Any]
    ) -> list[BlockCreateRequest]:
        """Parse text using context stack approach"""

        lines = text.split("\n")

        for line_num, line in enumerate(lines):
            # Try each element by priority
            action_taken = False

            for element in elements:
                if self._can_element_handle_line(element, line):
                    action = self._get_parse_action(element, line)

                    if action.type != ParseActionType.IGNORE:
                        self._execute_parse_action(action, element)
                        action_taken = True
                        break

            if not action_taken:
                # No element matched - handle as context content
                self._handle_unmatched_line(line)

        return self._build_final_tree()

    def _get_elements_by_priority(self) -> list[Any]:
        """Get elements sorted by parsing priority (highest first)"""
        elements = self.registry.get_elements()

        # Sort by priority (higher priority first)
        return sorted(
            elements, key=lambda e: self._get_element_priority(e), reverse=True
        )

    def _get_element_priority(self, element: NotionBlockElement) -> int:
        """Get priority for an element"""
        if hasattr(element, "get_parsing_capabilities"):
            return element.get_parsing_capabilities().priority

        # Default priority based on characteristics
        if hasattr(element, "is_multiline") and element.is_multiline():
            return 5  # Multiline blocks get higher priority

        return 1  # Default priority

    def _can_element_handle_line(self, element: NotionBlockElement, line: str) -> bool:
        """Check if element can handle the line in current context"""
        if hasattr(element, "can_handle_line"):
            return element.can_handle_line(line, self.context_stack)

        # Fallback to traditional matching
        return element.match_markdown(line)

    def _get_parse_action(self, element: NotionBlockElement, line: str) -> ParseAction:
        """Get the parse action for an element and line"""
        if hasattr(element, "handle_line"):
            return element.handle_line(line, self.context_stack)

        # Fallback: convert to traditional block creation
        result = element.markdown_to_notion(line)
        if not result:
            return ParseAction.ignore()

        capabilities = self._get_element_capabilities(element)
        if capabilities.can_have_children:
            return ParseAction.start_container(result)

        return ParseAction.add_sibling_block(result)

    def _get_element_capabilities(self, element: NotionBlockElement):
        """Get capabilities for an element"""
        if hasattr(element, "get_parsing_capabilities"):
            return element.get_parsing_capabilities()

        # Default capabilities
        return BlockParsingCapabilities(
            multiline=getattr(element, "is_multiline", lambda: False)()
        )

    def _execute_parse_action(self, action: ParseAction, element: Any):
        """Execute a parse action"""
        if action.type == ParseActionType.START_CONTAINER:
            new_context = BlockContext(action.block, element)
            self.context_stack.append(new_context)

        elif action.type == ParseActionType.END_CONTAINER:
            if len(self.context_stack) > 1:
                completed_context = self.context_stack.pop()
                self.context_stack[-1].add_child(completed_context.finalize())

        elif action.type == ParseActionType.ADD_CHILD_CONTENT:
            if len(self.context_stack) > 0:
                self.context_stack[-1].add_content(action.content)

        elif action.type == ParseActionType.ADD_SIBLING_BLOCK:
            if len(self.context_stack) > 0:
                self.context_stack[-1].add_child(action.block)

    def _handle_unmatched_line(self, line: str):
        """Handle lines that no element claimed"""
        if not line.strip():
            return

        paragraph_element = self._find_paragraph_element()
        if not paragraph_element:
            return

        result = paragraph_element.markdown_to_notion(line)
        if not result:
            return

        self.context_stack[-1].add_child(result)

    def _find_paragraph_element(self) -> Optional[Any]:
        """Find the paragraph element in registry"""
        for element in self.registry.get_elements():
            if element.__name__ == "ParagraphElement":
                return element
        return None

    def _build_final_tree(self) -> list[BlockCreateRequest]:
        """Build the final tree from context stack"""
        if not self.context_stack:
            return []

        root_context = self.context_stack[0]
        result = root_context.finalize()

        # Normalize result to list
        if isinstance(result, list):
            return self._flatten_blocks(result)
        else:
            return [result] if result else []

    def _flatten_blocks(self, blocks: list[Any]) -> list[BlockCreateRequest]:
        """Flatten nested block structures"""
        result = []
        for block in blocks:
            if isinstance(block, list):
                result.extend(self._flatten_blocks(block))
            else:
                result.append(block)
        return result
