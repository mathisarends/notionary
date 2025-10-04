from notionary.blocks.mappings.code import CodeMapper
from notionary.blocks.mappings.column import ColumnMapper
from notionary.blocks.mappings.column_list import ColumnListMapper
from notionary.page.content.parser.parsers import LineParser, LineProcessingContext


class RegularLineParser(LineParser):
    def _can_handle(self, context: LineProcessingContext) -> bool:
        return context.line.strip()

    async def _process(self, context: LineProcessingContext) -> None:
        if self._is_in_column_context(context):
            self._add_to_column_context(context)
            return

        block_created = await self._process_single_line_content(context)
        if not block_created:
            await self._process_as_paragraph(context)

    def _is_in_column_context(self, context: LineProcessingContext) -> bool:
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        return issubclass(current_parent.element_type, (ColumnListMapper, ColumnMapper))

    def _add_to_column_context(self, context: LineProcessingContext) -> None:
        context.parent_stack[-1].add_child_line(context.line)

    async def _process_single_line_content(self, context: LineProcessingContext) -> bool:
        specialized_elements = self._get_specialized_elements()

        for element in context.block_registry.get_elements():
            if issubclass(element, specialized_elements):
                continue

            result = await element.markdown_to_notion(context.line)
            if not result:
                continue

            context.result_blocks.append(result)

            return True

        return False

    async def _process_as_paragraph(self, context: LineProcessingContext) -> None:
        from notionary.blocks.mappings.paragraph import ParagraphMapper

        paragraph_element = ParagraphMapper()
        result = await paragraph_element.markdown_to_notion(context.line)
        context.result_blocks.append(result)

    def _get_specialized_elements(self):
        from notionary.blocks.mappings.table import TableMapper
        from notionary.blocks.mappings.toggle import ToggleMapper

        return (
            ColumnListMapper,
            CodeMapper,
            ToggleMapper,
            TableMapper,
            CodeMapper,
        )
