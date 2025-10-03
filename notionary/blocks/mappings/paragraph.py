from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import (
    Block,
    BlockColor,
    BlockType,
    CreateParagraphBlock,
    ParagraphData,
)
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


class ParagraphMapper(NotionMarkdownMapper):
    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.PARAGRAPH and block.paragraph

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreateParagraphBlock:
        """Convert markdown text to a Notion ParagraphBlock."""
        if not text.strip():
            return None

        converter = MarkdownRichTextConverter()
        rich = await converter.to_rich_text(text)

        paragraph_content = ParagraphData(rich_text=rich, color=BlockColor.DEFAULT)
        return CreateParagraphBlock(paragraph=paragraph_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.PARAGRAPH or not block.paragraph:
            return None

        rich_list = block.paragraph.rich_text
        converter = RichTextToMarkdownConverter()
        markdown = await converter.to_markdown(rich_list)

        return markdown or None

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for paragraph blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Paragraph blocks contain regular text content with optional inline formatting",
            syntax_examples=[
                "This is a simple paragraph.",
                "Paragraph with **bold text** and *italic text*.",
                "Paragraph with [link](https://example.com) and `code`.",
                "Multiple sentences in one paragraph. Each sentence flows naturally.",
            ],
            usage_guidelines="Use for regular text content. Supports inline formatting: **bold**, *italic*, `code`, [links](url). Default block type for plain text.",
        )
