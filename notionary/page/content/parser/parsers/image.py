"""Parser for image blocks."""

import re
from typing import override

from notionary.blocks.schemas import (
    CreateImageBlock,
    ExternalFile,
    FileData,
    FileType,
)
from notionary.page.content.parser.parsers.base import BlockParsingContext, LineParser


class ImageParser(LineParser):
    IMAGE_PATTERN = re.compile(r"\[image\]\(([^)]+)\)")

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.IMAGE_PATTERN.search(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        url = self._extract_url(context.line)
        if not url:
            return

        image_data = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=url),
            caption=[],
        )
        block = CreateImageBlock(image=image_data)
        context.result_blocks.append(block)

    def _extract_url(self, line: str) -> str | None:
        match = self.IMAGE_PATTERN.search(line)
        return match.group(1).strip() if match else None
