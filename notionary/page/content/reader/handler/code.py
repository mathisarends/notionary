from typing import override

from notionary.blocks.mappings.code import CodeMapper
from notionary.blocks.schemas import Block
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class CodeRenderer(BlockRenderer):
    CODE_FENCE = "```"

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return CodeMapper.match_notion(context.block)

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        language, code_content = self._extract_code_info(context.block)

        if not code_content:
            context.markdown_result = ""
            context.was_processed = True
            return

        # Build code block
        code_start = f"{self.CODE_FENCE}{language}"
        code_end = self.CODE_FENCE
        code_markdown = f"{code_start}\n{code_content}\n{code_end}"

        if context.indent_level > 0:
            code_markdown = context.indent_text(code_markdown)

        context.markdown_result = code_markdown
        context.was_processed = True

    def _extract_code_info(self, block: Block) -> tuple[str, str]:
        if not block.code:
            return "", ""

        language = block.code.language.value if block.code.language else ""

        # Extract plain text from rich_text
        code_content = ""
        if block.code.rich_text:
            for text_obj in block.code.rich_text:
                if hasattr(text_obj, "plain_text"):
                    code_content += text_obj.plain_text or ""
                elif hasattr(text_obj, "text") and hasattr(text_obj.text, "content"):
                    code_content += text_obj.text.content or ""

        return language, code_content.rstrip()
