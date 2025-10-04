import re

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.mappings.rich_text.models import RichText
from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import (
    Block,
    BlockType,
    CreateEmbedBlock,
    EmbedData,
    ExternalFile,
    FileUploadFile,
    NotionHostedFile,
)


class EmbedMapper(NotionMarkdownMapper):
    PATTERN = re.compile(
        r"^\[embed\]\("  # prefix
        r"(https?://[^\s\"]+)"  # URL
        r"(?:\s+\"([^\"]+)\")?"  # optional caption
        r"\)$"
    )

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.EMBED and block.embed

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreateEmbedBlock:
        """Convert markdown embed syntax to Notion EmbedBlock."""
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        url, rich_text = match.group(1), match.group(2) or ""

        # Build EmbedBlock
        embed_block = EmbedData(url=url, caption=[])
        if rich_text.strip():
            rich_text_obj = RichText.from_plain_text(rich_text.strip())
            embed_block.caption = [rich_text_obj]

        return CreateEmbedBlock(embed=embed_block)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.EMBED or not block.embed:
            return None

        fo = block.embed

        if isinstance(fo, (ExternalFile, NotionHostedFile)):
            url = fo.url
        elif isinstance(fo, FileUploadFile):
            return None
        else:
            return None

        if not fo.caption:
            return f"[embed]({url})"

        text_parts = []
        converter = RichTextToMarkdownConverter()
        for rt in fo.caption:
            if rt.plain_text:
                text_parts.append(rt.plain_text)
            else:
                formatted_text = await converter.to_markdown([rt])
                text_parts.append(formatted_text)
        text = "".join(text_parts)

        return f'[embed]({url} "{text}")'
