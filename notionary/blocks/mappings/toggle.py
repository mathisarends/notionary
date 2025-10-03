import re

from notionary.blocks.mappings.base import BaseBlockElement
from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.mappings.rich_text.models import RichText
from notionary.blocks.schemas import Block, BlockColor, BlockCreateResult, BlockType, CreateToggleBlock, ToggleBlock
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


class ToggleElement(BaseBlockElement):
    """
    Simplified ToggleElement class that works with the stack-based converter.
    Children are automatically handled by the StackBasedMarkdownConverter.
    """

    # Updated pattern for ultra-simplified +++ Title syntax (no quotes!)
    TOGGLE_PATTERN = re.compile(r"^[+]{3}\s+(.+)$", re.IGNORECASE)
    TRANSCRIPT_TOGGLE_PATTERN = re.compile(r"^[+]{3}\s+Transcript$", re.IGNORECASE)

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if the block is a Notion toggle block."""
        return block.type == BlockType.TOGGLE

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """
        Convert markdown toggle line to Notion ToggleBlock.
        Children are automatically handled by the StackBasedMarkdownConverter.
        """
        if not (match := cls.TOGGLE_PATTERN.match(text.strip())):
            return None

        title = match.group(1).strip()
        converter = MarkdownRichTextConverter()
        rich_text = await converter.to_rich_text(title)

        # Create toggle block with empty children - they will be populated automatically
        toggle_content = ToggleBlock(rich_text=rich_text, color=BlockColor.DEFAULT, children=[])

        return CreateToggleBlock(toggle=toggle_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        """
        Converts a Notion toggle block into markdown using the ultra-simplified +++ syntax.
        """
        if block.type != BlockType.TOGGLE:
            return None

        if not block.toggle:
            return None

        toggle_data = block.toggle

        # Extract title from rich_text
        title = cls._extract_text_content(toggle_data.rich_text or [])

        # Create toggle line with ultra-simplified syntax (no quotes!)
        toggle_line = f"+++ {title}"

        # Process children if available
        children = toggle_data.children or []
        if not children:
            return toggle_line + "\n+++"

        # Add a placeholder line for each child
        child_lines = ["[Nested content]" for _ in children]

        return toggle_line + "\n" + "\n".join(child_lines) + "\n+++"

    @classmethod
    def _extract_text_content(cls, rich_text: list[RichText]) -> str:
        """Extracts plain text content from Notion rich_text blocks."""
        result = ""
        for text_obj in rich_text:
            if hasattr(text_obj, "plain_text"):
                result += text_obj.plain_text or ""
            elif hasattr(text_obj, "type") and text_obj.type == "text" and hasattr(text_obj, "text"):
                result += text_obj.text.content or ""
            # Fallback for dict-style access (backward compatibility)
            elif isinstance(text_obj, dict):
                if text_obj.get("type") == "text":
                    result += text_obj.get("text", {}).get("content", "")
                elif "plain_text" in text_obj:
                    result += text_obj.get("plain_text", "")
        return result

    @classmethod
    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for toggle blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Toggle blocks create collapsible sections with expandable content",
            syntax_examples=[
                "+++Title\nContent goes here\n+++",
                "+++Details\nMore information\nAdditional content\n+++",
                "+++FAQ\nFrequently asked questions\n+++",
            ],
            usage_guidelines="Use for collapsible content sections. Start with +++Title, add content, end with +++. Great for FAQs, details, or organizing long content.",
        )
