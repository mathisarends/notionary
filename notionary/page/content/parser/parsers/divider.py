from typing import override

from notionary.blocks.schemas import CreateDividerBlock, DividerData
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class DividerParser(LineParser):
    def __init__(self, syntax_registry: SyntaxDefinitionRegistry) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_divider_syntax()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_divider(context.line)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = self._create_divider_block()
        if block:
            context.result_blocks.append(block)

    def _is_divider(self, line: str) -> bool:
        return self._syntax.regex_pattern.match(line) is not None

    def _create_divider_block(self) -> CreateDividerBlock:
        divider_data = DividerData()
        return CreateDividerBlock(divider=divider_data)
