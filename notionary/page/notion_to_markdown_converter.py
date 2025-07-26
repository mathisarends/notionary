from typing import Dict, Any, List, Optional

from notionary.blocks import BlockRegistry, BlockRegistryBuilder


class NotionToMarkdownConverter:
    """Converts Notion blocks to Markdown text with support for nested structures."""

    TOGGLE_ELEMENT_TYPES = ["toggle", "toggleable_heading"]
    LIST_ITEM_TYPES = ["numbered_list_item", "bulleted_list_item"]

    def __init__(self, block_registry: Optional[BlockRegistry] = None):
        """
        Initialize the NotionToMarkdownConverter.
        """
        self._block_registry = (
            block_registry or BlockRegistryBuilder().create_registry()
        )

    def convert(self, blocks: List[Dict[str, Any]]) -> str:
        """
        Convert Notion blocks to Markdown text, handling nested structures.
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

        if block_type in self.TOGGLE_ELEMENT_TYPES:
            return self._format_toggle_with_children(block_markdown, children_markdown)

        if block_type in self.LIST_ITEM_TYPES:
            return self._format_list_item_with_children(
                block_markdown, children_markdown
            )

        return self._format_standard_block_with_children(
            block_markdown, children_markdown
        )

    def _has_children(self, block: Dict[str, Any]) -> bool:
        """
        Check if block has children that need processing.
        """
        return block.get("has_children", False) and "children" in block

    def _format_toggle_with_children(
        self, toggle_markdown: str, children_markdown: str
    ) -> str:
        """
        Format toggle or toggleable_heading block with its children content.
        """
        indented_children = self._indent_text(children_markdown)
        return f"{toggle_markdown}\n{indented_children}"

    def _format_list_item_with_children(
        self, item_markdown: str, children_markdown: str
    ) -> str:
        """
        Format list item with its children content.
        """
        indented_children = self._indent_text(children_markdown)
        return f"{item_markdown}\n{indented_children}"

    def _format_standard_block_with_children(
        self, block_markdown: str, children_markdown: str
    ) -> str:
        """
        Format standard block with its children content.
        """
        return f"{block_markdown}\n\n{children_markdown}"

    def _indent_text(self, text: str, spaces: int = 4) -> str:
        """
        Indent each line of text with specified number of spaces.
        """
        indent = " " * spaces
        return "\n".join([f"{indent}{line}" for line in text.split("\n")])

    def extract_toggle_content(self, blocks: List[Dict[str, Any]]) -> str:
        """
        Extract only the content of toggles from blocks.
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
        """
        if self._is_toggle_or_heading_with_children(block):
            self._add_toggle_header_to_result(block, result)
            self._add_toggle_children_to_result(block, result)

        if self._has_children(block):
            for child in block["children"]:
                self._extract_toggle_content_recursive(child, result)

    def _is_toggle_or_heading_with_children(self, block: Dict[str, Any]) -> bool:
        """
        Check if block is a toggle or toggleable_heading with children.
        """
        return block.get("type") in self.TOGGLE_ELEMENT_TYPES and "children" in block

    def _add_toggle_header_to_result(
        self, block: Dict[str, Any], result: List[str]
    ) -> None:
        """
        Add toggle header text to result list.
        """
        block_type = block.get("type")
        rich_text = None

        if block_type == "toggle":
            rich_text = block.get("toggle", {}).get("rich_text", [])
        elif block_type == "toggleable_heading":
            rich_text = block.get("toggleable_heading", {}).get("rich_text", [])

        toggle_text = self._extract_text_from_rich_text(rich_text or [])

        if toggle_text:
            result.append(f"### {toggle_text}")

    def _add_toggle_children_to_result(
        self, block: Dict[str, Any], result: List[str]
    ) -> None:
        """
        Add formatted toggle children to result list.
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
        """
        if not rich_text:
            return ""

        return "".join([rt.get("plain_text", "") for rt in rich_text])
