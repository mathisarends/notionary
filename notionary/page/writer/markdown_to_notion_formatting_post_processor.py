"""
Post-processor for handling block formatting in Markdown to Notion conversion.

Handles block formatting tasks like adding empty paragraphs before media blocks
and other formatting-related post-processing.
"""
from typing import cast
from notionary.blocks.models import BlockCreateRequest
from notionary.blocks.types import BlockType
from notionary.blocks.paragraph.paragraph_models import CreateParagraphBlock, ParagraphBlock


class MarkdownToNotionFormattingPostProcessor:
    """Handles block formatting post-processing for Notion blocks."""

    BLOCKS_NEEDING_EMPTY_PARAGRAPH = {
        BlockType.DIVIDER,
        BlockType.FILE,
        BlockType.IMAGE, 
        BlockType.PDF,
        BlockType.VIDEO
    }

    def process(self, blocks: list[BlockCreateRequest]) -> list[BlockCreateRequest]:
        """Process blocks with all formatting steps."""
        if not blocks:
            return blocks

        return self._add_empty_paragraphs_for_media_blocks(blocks)

    def _add_empty_paragraphs_for_media_blocks(self, blocks: list[BlockCreateRequest]) -> list[BlockCreateRequest]:
        """Add empty paragraphs before configured block types."""
        if not blocks:
            return blocks

        result = []
        
        for i, block in enumerate(blocks):
            block_type = block.type
            
            if (block_type in self.BLOCKS_NEEDING_EMPTY_PARAGRAPH and 
                i > 0 and 
                not self._is_empty_paragraph(result[-1] if result else None)):
                
                # Create empty paragraph block inline
                empty_paragraph = CreateParagraphBlock(paragraph=ParagraphBlock(rich_text=[]))
                result.append(empty_paragraph)
            
            result.append(block)
        
        return result

    def _is_empty_paragraph(self, block: BlockCreateRequest | None) -> bool:
        if not block or block.type != BlockType.PARAGRAPH:
            return False
        if not isinstance(block, CreateParagraphBlock):
            return False  # Safety: nur Paragraph-Create-Block hat .paragraph

        para_block = cast(CreateParagraphBlock, block)
        paragraph: ParagraphBlock | None = para_block.paragraph
        if not paragraph:
            return False

        return not paragraph.rich_text or len(paragraph.rich_text) == 0