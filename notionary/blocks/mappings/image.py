import re

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.mappings.mixins.captions import CaptionMixin
from notionary.blocks.schemas import (
    Block,
    BlockType,
    CreateImageBlock,
    ExternalFile,
    FileData,
    FileType,
)


class ImageMapper(NotionMarkdownMapper, CaptionMixin):
    # Pattern matches both URLs and file paths
    IMAGE_PATTERN = re.compile(r"\[image\]\(([^)]+)\)")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.IMAGE and block.image

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreateImageBlock | None:
        image_path = cls._extract_image_path(text.strip())
        if not image_path:
            return None

        # Extract caption
        caption_text = cls.extract_caption(text.strip())
        caption_rich_text = cls.build_caption_rich_text(caption_text or "")

        # Only support external URLs - no local file upload
        image_block = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=image_path),
            caption=caption_rich_text,
        )

        return CreateImageBlock(image=image_block)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.IMAGE or not block.image:
            return None

        fo = block.image

        # Determine the source for markdown
        if fo.type == FileType.EXTERNAL and fo.external:
            source = fo.external.url
        elif fo.type == FileType.FILE and fo.file:
            source = fo.file.url
        else:
            return None

        result = f"[image]({source})"

        # Add caption if present
        caption_markdown = await cls.format_caption_for_markdown(fo.caption or [])
        if caption_markdown:
            result += caption_markdown

        return result

    @classmethod
    def _extract_image_path(cls, text: str) -> str | None:
        """Extract image path/URL from text, handling caption patterns."""
        clean_text = cls.remove_caption(text)

        match = cls.IMAGE_PATTERN.search(clean_text)
        if match:
            return match.group(1).strip()

        return None
