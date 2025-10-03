from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.mappings.rich_text.models import RichText
from notionary.blocks.schemas import (
    Block,
    BlockColor,
    BlockCreatePayload,
    BlockType,
    CreateParagraphBlock,
    ParagraphData,
)
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


class SpaceMapper(NotionMarkdownMapper):
    SPACE_MARKER = "[SPACE]"

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        if block.type != BlockType.PARAGRAPH:
            return False

        if not block.paragraph:
            return False

        # check for empty paragraph because only space element can produce such a block in this conversion logic
        if cls._is_empty_paragraph(block.paragraph.rich_text):
            return True

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreatePayload:
        if text.strip() != cls.SPACE_MARKER:
            return None

        converter = MarkdownRichTextConverter()
        rich = await converter.to_rich_text("")  # create empty paragraph
        paragraph_content = ParagraphData(rich_text=rich, color=BlockColor.DEFAULT)
        return CreateParagraphBlock(paragraph=paragraph_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if not cls.match_notion(block):
            return None

        return cls.SPACE_MARKER

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Space blocks create visual spacing between content",
            syntax_examples=[
                cls.SPACE_MARKER,
            ],
            usage_guidelines=f"Use {cls.SPACE_MARKER} to create visual spacing between paragraphs or other content blocks.",
        )

    @classmethod
    def _is_empty_paragraph(cls, rich_text: list[RichText]) -> bool:
        return not len(rich_text)
