from notionary.blocks.mappings.column import ColumnElement
from notionary.blocks.mappings.column_list import ColumnListElement
from notionary.page.writer.handler import LineHandler, LineProcessingContext


class RegularLineHandler(LineHandler):
    def _can_handle(self, context: LineProcessingContext) -> bool:
        return context.line.strip()

    async def _process(self, context: LineProcessingContext) -> None:
        if self._is_in_column_context(context):
            self._add_to_column_context(context)
            context.was_processed = True
            context.should_continue = True
            return

        block_created = await self._process_single_line_content(context)
        if not block_created:
            await self._process_as_paragraph(context)

        context.was_processed = True

    def _is_in_column_context(self, context: LineProcessingContext) -> bool:
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        return issubclass(current_parent.element_type, (ColumnListElement, ColumnElement))

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
        """Process a line as a paragraph."""
        from notionary.blocks.mappings.paragraph import ParagraphElement

        paragraph_element = ParagraphElement()
        result = await paragraph_element.markdown_to_notion(context.line)
        context.result_blocks.append(result)

    def _get_specialized_elements(self):
        from notionary.blocks.mappings.code import CodeElement
        from notionary.blocks.mappings.table import TableElement
        from notionary.blocks.mappings.toggle import ToggleElement
        from notionary.blocks.mappings.toggleable_heading import ToggleableHeadingElement

        return (
            ColumnListElement,
            ColumnElement,
            ToggleElement,
            ToggleableHeadingElement,
            TableElement,
            CodeElement,
        )
