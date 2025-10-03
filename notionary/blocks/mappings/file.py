import re

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.mappings.mixins.captions import CaptionMixin
from notionary.blocks.schemas import (
    Block,
    BlockType,
    CreateFileBlock,
    ExternalFile,
    FileData,
    FileType,
)
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


class FileMapper(NotionMarkdownMapper, CaptionMixin):
    r"""
    Markdown file syntax:
    - [file](https://example.com/document.pdf) - External URL
    - [file](https://example.com/document.pdf)(caption:Annual Report) - With caption
    """

    FILE_PATTERN = re.compile(r"\[file\]\(([^)]+)\)")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return bool(block.type == BlockType.FILE and block.file)

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreateFileBlock | None:
        """Convert markdown file link to Notion FileBlock."""
        file_path = cls._extract_file_path(text.strip())
        if not file_path:
            return None

        # Extract caption
        caption_text = cls.extract_caption(text.strip())
        caption_rich_text = cls.build_caption_rich_text(caption_text or "")

        # Only support external URLs - no local file upload
        file_block = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=file_path),
            caption=caption_rich_text,
        )

        return CreateFileBlock(file=file_block)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.FILE or not block.file:
            return None

        fb: FileData = block.file

        # Determine the source for markdown
        if fb.type == FileType.EXTERNAL and fb.external:
            source = fb.external.url
        elif fb.type == FileType.FILE and fb.file:
            source = fb.file.url
        else:
            return None

        result = f"[file]({source})"

        # Add caption if present
        caption_markdown = await cls.format_caption_for_markdown(fb.caption or [])
        if caption_markdown:
            result += caption_markdown

        return result

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for file blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="File blocks embed files from external URLs or upload local files with optional captions",
            syntax_examples=[
                "[file](https://example.com/document.pdf)",
                "[file](https://example.com/document.pdf)(caption:Annual Report)",
                "(caption:Q1 Data)[file](https://example.com/spreadsheet.xlsx)",
                "[file](https://example.com/manual.docx)(caption:**User** manual)",
            ],
            usage_guidelines="Use for external URLs only. Caption supports rich text formatting and should describe the file content or purpose.",
        )

    @classmethod
    def _extract_file_path(cls, text: str) -> str | None:
        """Extract file path/URL from text, handling caption patterns."""
        clean_text = cls.remove_caption(text)

        match = cls.FILE_PATTERN.search(clean_text)
        if match:
            return match.group(1).strip()

        return None
