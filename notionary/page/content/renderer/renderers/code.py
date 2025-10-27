from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block
from notionary.page.content.renderer.renderers.captioned_block import (
    CaptionedBlockRenderer,
)


class CodeRenderer(CaptionedBlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.CODE

    @override
    async def _render_main_content(self, block: Block) -> str:
        language = self._extract_code_language(block)
        code_content = await self._extract_code_content(block)

        if not code_content:
            return ""

        syntax = self._syntax_registry.get_code_syntax()
        code_start = f"{syntax.start_delimiter}{language}"
        code_end = syntax.end_delimiter
        return f"{code_start}\n{code_content}\n{code_end}"

    def _extract_code_language(self, block: Block) -> str:
        if not block.code or not block.code.language:
            return ""
        return block.code.language.value

    async def _extract_code_content(self, block: Block) -> str:
        if not block.code or not block.code.rich_text:
            return ""
        return await self._rich_text_markdown_converter.to_markdown(
            block.code.rich_text
        )
