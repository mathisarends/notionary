from typing import Dict, Any, List, Optional

from notionary.elements.block_element_registry import (
    BlockElementRegistry,
)
from notionary.elements.block_element_registry_builder import (
    BlockElementRegistryBuilder,
)


class NotionToMarkdownConverter:
    """Converts Notion blocks to Markdown text with support for nested structures."""

    def __init__(self, block_registry: Optional[BlockElementRegistry] = None):
        """
        Initialize the NotionToMarkdownConverter.

        Args:
            block_registry: Optional registry of Notion block elements
        """
        self._block_registry = (
            block_registry or BlockElementRegistryBuilder().create_standard_registry()
        )

    def convert(self, blocks: List[Dict[str, Any]]) -> str:
        """
        Convert Notion blocks to Markdown text, handling nested structures.

        Args:
            blocks: List of Notion blocks

        Returns:
            Markdown text
        """
        if not blocks:
            return ""

        markdown_parts = []

        for block in blocks:
            block_markdown = self._convert_single_block_with_children(block)
            if block_markdown:
                markdown_parts.append(block_markdown)

        return "\n\n".join(filter(None, markdown_parts))

    def _convert_single_block_with_children(self, block: Dict[str, Any]) -> str:
        """
        Process a single block, including any children.

        Args:
            block: Notion block to process

        Returns:
            Markdown representation of the block and its children
        """
        if not block:
            return ""

        block_markdown = self._block_registry.notion_to_markdown(block)

        if not self._has_children(block):
            return block_markdown

        children_markdown = self.convert(block["children"])
        if not children_markdown:
            return block_markdown

        block_type = block.get("type", "")

        if block_type == "toggle":
            return self._format_toggle_with_children(block_markdown, children_markdown)

        if block_type in ["numbered_list_item", "bulleted_list_item"]:
            return self._format_list_item_with_children(
                block_markdown, children_markdown
            )

        if block_type in ["column_list", "column"]:
            return children_markdown

        return self._format_standard_block_with_children(
            block_markdown, children_markdown
        )

    def _has_children(self, block: Dict[str, Any]) -> bool:
        """
        Check if block has children that need processing.

        Args:
            block: Notion block to check

        Returns:
            True if block has children to process
        """
        return block.get("has_children", False) and "children" in block

    def _format_toggle_with_children(
        self, toggle_markdown: str, children_markdown: str
    ) -> str:
        """
        Format toggle block with its children content.

        Args:
            toggle_markdown: Markdown for the toggle itself
            children_markdown: Markdown for toggle's children

        Returns:
            Formatted markdown with indented children
        """
        indented_children = self._indent_text(children_markdown)
        return f"{toggle_markdown}\n{indented_children}"

    def _format_list_item_with_children(
        self, item_markdown: str, children_markdown: str
    ) -> str:
        """
        Format list item with its children content.

        Args:
            item_markdown: Markdown for the list item itself
            children_markdown: Markdown for item's children

        Returns:
            Formatted markdown with indented children
        """
        indented_children = self._indent_text(children_markdown)
        return f"{item_markdown}\n{indented_children}"

    def _format_standard_block_with_children(
        self, block_markdown: str, children_markdown: str
    ) -> str:
        """
        Format standard block with its children content.

        Args:
            block_markdown: Markdown for the block itself
            children_markdown: Markdown for block's children

        Returns:
            Formatted markdown with children after block
        """
        return f"{block_markdown}\n\n{children_markdown}"

    def _indent_text(self, text: str, spaces: int = 4) -> str:
        """
        Indent each line of text with specified number of spaces.

        Args:
            text: Text to indent
            spaces: Number of spaces to use for indentation

        Returns:
            Indented text
        """
        indent = " " * spaces
        return "\n".join([f"{indent}{line}" for line in text.split("\n")])

    def extract_toggle_content(self, blocks: List[Dict[str, Any]]) -> str:
        """
        Extract only the content of toggles from blocks.

        Args:
            blocks: List of Notion blocks

        Returns:
            Markdown text with toggle contents
        """
        if not blocks:
            return ""

        toggle_contents = []

        for block in blocks:
            self._extract_toggle_content_recursive(block, toggle_contents)

        return "\n".join(toggle_contents)

    def _extract_toggle_content_recursive(
        self, block: Dict[str, Any], result: List[str]
    ) -> None:
        """
        Recursively extract toggle content from a block and its children.

        Args:
            block: Block to process
            result: List to collect toggle content
        """
        if self._is_toggle_with_children(block):
            self._add_toggle_header_to_result(block, result)
            self._add_toggle_children_to_result(block, result)

        if self._has_children(block):
            for child in block["children"]:
                self._extract_toggle_content_recursive(child, result)

    def _is_toggle_with_children(self, block: Dict[str, Any]) -> bool:
        """
        Check if block is a toggle with children.

        Args:
            block: Block to check

        Returns:
            True if block is a toggle with children
        """
        return block.get("type") == "toggle" and "children" in block

    def _add_toggle_header_to_result(
        self, block: Dict[str, Any], result: List[str]
    ) -> None:
        """
        Add toggle header text to result list.

        Args:
            block: Toggle block
            result: List to add header to
        """
        toggle_text = self._extract_text_from_rich_text(
            block.get("toggle", {}).get("rich_text", [])
        )

        if toggle_text:
            result.append(f"### {toggle_text}")

    def _add_toggle_children_to_result(
        self, block: Dict[str, Any], result: List[str]
    ) -> None:
        """
        Add formatted toggle children to result list.

        Args:
            block: Toggle block with children
            result: List to add children content to
        """
        for child in block.get("children", []):
            child_type = child.get("type")
            if not (child_type and child_type in child):
                continue

            child_text = self._extract_text_from_rich_text(
                child.get(child_type, {}).get("rich_text", [])
            )

            if child_text:
                result.append(f"- {child_text}")

    def _extract_text_from_rich_text(self, rich_text: List[Dict[str, Any]]) -> str:
        """
        Extract plain text from Notion's rich text array.

        Args:
            rich_text: List of rich text objects

        Returns:
            Concatenated plain text
        """
        if not rich_text:
            return ""

        return "".join([rt.get("plain_text", "") for rt in rich_text])
