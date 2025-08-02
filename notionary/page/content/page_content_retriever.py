from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks import NotionBlockClient
from notionary.blocks.shared.models import Block, HeadingBlock, RichTextObject
from notionary.util import LoggingMixin


class PageContentRetriever(LoggingMixin):
    """Retrieves Notion page content and converts it to Markdown."""

    TOGGLE_ELEMENT_TYPES = ["toggle", "toggleable_heading"]
    LIST_ITEM_TYPES = ["numbered_list_item", "bulleted_list_item"]

    def __init__(
        self,
        page_id: str,
        block_registry: BlockRegistry,
    ):
        self.page_id = page_id
        self._block_registry = block_registry
        self.client = NotionBlockClient()

    async def get_page_content(self) -> str:
        """
        Retrieve page content and convert it to Markdown.
        """
        blocks = await self.client.get_blocks_by_page_id_recursively(
            page_id=self.page_id
        )
        return self._convert_blocks_to_markdown(blocks)

    def _convert_blocks_to_markdown(self, blocks: list[Block]) -> str:
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

    def _convert_single_block_with_children(self, block: Block) -> str:
        """
        Process a single block, including any children.
        """
        if not block:
            return ""

        # Use Block object directly with the block registry
        block_markdown = self._block_registry.notion_to_markdown(block)

        if not self._has_children(block):
            return block_markdown

        children_markdown = self._convert_blocks_to_markdown(block.children)
        if not children_markdown:
            return block_markdown

        block_type = block.type

        if block_type in self.TOGGLE_ELEMENT_TYPES:
            return self._format_toggle_with_children(block_markdown, children_markdown)

        if block_type in self.LIST_ITEM_TYPES:
            return self._format_list_item_with_children(
                block_markdown, children_markdown
            )

        return self._format_standard_block_with_children(
            block_markdown, children_markdown
        )

    def _has_children(self, block: Block) -> bool:
        """
        Check if block has children that need processing.
        """
        return block.has_children and block.children is not None

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

    def _extract_toggle_content(self, blocks: list[Block]) -> str:
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
        self, block: Block, result: list[str]
    ) -> None:
        """
        Recursively extract toggle content from a block and its children.
        """
        if self._is_toggle_or_heading_with_children(block):
            self._add_toggle_header_to_result(block, result)
            self._add_toggle_children_to_result(block, result)

        if self._has_children(block):
            for child in block.children:
                self._extract_toggle_content_recursive(child, result)

    def _is_toggle_or_heading_with_children(self, block: Block) -> bool:
        """
        Check if block is a toggle or toggleable_heading with children.
        """
        return block.type in self.TOGGLE_ELEMENT_TYPES and block.children is not None

    def _add_toggle_header_to_result(self, block: Block, result: list[str]) -> None:
        """
        Add toggle header text to result list.
        """
        rich_text = None

        if block.type == "toggle" and getattr(block, "toggle", None):
            rich_text = block.toggle.rich_text
        elif block.type in ("heading_1", "heading_2", "heading_3"):
            heading_obj: HeadingBlock = getattr(block, block.type, None)
            if heading_obj:
                rich_text = heading_obj.rich_text
            else:
                rich_text = None

        toggle_text = self._extract_text_from_rich_text(rich_text or [])

        if toggle_text:
            result.append(f"### {toggle_text}")

    def _add_toggle_children_to_result(self, block: Block, result: list[str]) -> None:
        """
        Add formatted toggle children to result list.
        """
        if not block.children:
            return

        for child in block.children:
            child_content = child.get_block_content()
            if not child_content:
                continue

            # Extract rich_text from the child content
            rich_text = getattr(child_content, "rich_text", None)
            if not rich_text:
                continue

            child_text = self._extract_text_from_rich_text(rich_text)

            if child_text:
                result.append(f"- {child_text}")

    def _extract_text_from_rich_text(self, rich_text: list[RichTextObject]) -> str:
        """
        Extract plain text from Notion's rich text array.
        """
        if not rich_text:
            return ""

        return "".join([rt.plain_text for rt in rich_text])
