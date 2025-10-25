from typing import override

from notionary.blocks.schemas import BreadcrumbData, CreateBreadcrumbBlock
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax import SyntaxDefinitionRegistry


class BreadcrumbParser(LineParser):
    def __init__(self, syntax_registry: SyntaxDefinitionRegistry) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_breadcrumb_syntax()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_breadcrumb(context.line)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = self._create_breadcrumb_block()
        if block:
            context.result_blocks.append(block)

    def _is_breadcrumb(self, line: str) -> bool:
        return self._syntax.regex_pattern.match(line) is not None

    def _create_breadcrumb_block(self) -> CreateBreadcrumbBlock:
        breadcrumb_data = BreadcrumbData()
        return CreateBreadcrumbBlock(breadcrumb=breadcrumb_data)
