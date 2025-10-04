import re

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.mappings.mixins.captions import CaptionMixin
from notionary.blocks.schemas import (
    Block,
    BlockType,
    CreatePdfBlock,
    ExternalFile,
    FileData,
    FileType,
)


class PdfMapper(NotionMarkdownMapper, CaptionMixin):
    PDF_PATTERN = re.compile(r"\[pdf\]\(([^)]+)\)")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Match Notion PDF blocks."""
        return block.type == BlockType.PDF and block.pdf

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreatePdfBlock | None:
        pdf_path = cls._extract_pdf_path(text.strip())

        if not pdf_path:
            return None

        # Extract caption
        caption_text = cls.extract_caption(text.strip())
        caption_rich_text = cls.build_caption_rich_text(caption_text or "")

        # Only support external URLs - no local file upload
        pdf_block = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=pdf_path),
            caption=caption_rich_text,
        )

        return CreatePdfBlock(pdf=pdf_block)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.PDF or not block.pdf:
            return None

        pb: FileData = block.pdf

        # Determine the source for markdown
        if pb.type == FileType.EXTERNAL and pb.external:
            source = pb.external.url
        elif pb.type == FileType.FILE and pb.file:
            source = pb.file.url
        else:
            return None

        result = f"[pdf]({source})"

        # Add caption if present
        caption_markdown = await cls.format_caption_for_markdown(pb.caption or [])
        if caption_markdown:
            result += caption_markdown

        return result

    @classmethod
    def _extract_pdf_path(cls, text: str) -> str | None:
        """Extract PDF path/URL from text, handling caption patterns."""
        clean_text = cls.remove_caption(text)

        match = cls.PDF_PATTERN.search(clean_text)
        if match:
            return match.group(1).strip()

        return None
