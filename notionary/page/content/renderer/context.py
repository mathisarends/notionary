from collections.abc import Awaitable, Callable

from notionary.blocks.schemas import Block

ConvertChildrenCallback = Callable[[list[Block], int], Awaitable[str]]


class MarkdownRenderingContext:
    MARKDOWN_INDENTATION_MULTIPLIER = 4

    def __init__(
        self,
        block: Block,
        indent_level: int,
        convert_children_callback: ConvertChildrenCallback | None = None,
    ) -> None:
        self.block = block
        self.indent_level = indent_level
        self.convert_children_callback = convert_children_callback

        self.markdown_result: str | None = None

    async def render_children(self) -> str:
        return await self._convert_children_to_markdown(self.indent_level)

    async def render_children_with_additional_indent(self, additional_indent: int) -> str:
        return await self._convert_children_to_markdown(self.indent_level + additional_indent)

    async def _convert_children_to_markdown(self, indent_level: int) -> str:
        if not self._has_children() or not self.convert_children_callback:
            return ""

        return await self.convert_children_callback(self._get_children_blocks(), indent_level)

    def _get_children_blocks(self) -> list[Block]:
        if self._has_children():
            return self.block.children
        return []

    def _has_children(self) -> bool:
        return self.block.has_children and self.block.children and len(self.block.children) > 0

    def indent_text(self, text: str) -> str:
        if not text:
            return text

        spaces = " " * self.MARKDOWN_INDENTATION_MULTIPLIER * self.indent_level
        lines = text.split("\n")
        return "\n".join(f"{spaces}{line}" if line.strip() else line for line in lines)
