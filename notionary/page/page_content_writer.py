from typing import Callable, Optional, Union

from notionary.blocks.client import NotionBlockClient
from notionary.blocks.divider import DividerElement
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.table_of_contents import TableOfContentsElement
from notionary.markdown.markdown_builder import MarkdownBuilder
from notionary.page.writer.markdown_to_notion_converter import MarkdownToNotionConverter
from notionary.util import LoggingMixin


class PageContentWriter(LoggingMixin):
    def __init__(self, page_id: str, block_registry: BlockRegistry):
        self.page_id = page_id
        self.block_registry = block_registry
        self._block_client = NotionBlockClient()

        self._markdown_to_notion_converter = MarkdownToNotionConverter(
            block_registry=block_registry
        )

    async def append_markdown(
        self,
        content: Union[str, Callable[[MarkdownBuilder], MarkdownBuilder]],
        *,
        append_divider: bool = True,
        prepend_table_of_contents: bool = False,
    ) -> Optional[str]:
        """
        Append markdown content to a Notion page using either text or builder callback.
        """

        if isinstance(content, str):
            final_markdown = content
        elif callable(content):
            builder = MarkdownBuilder()
            content(builder)
            final_markdown = builder.build()
        else:
            raise ValueError(
                "content must be either a string or a callable that takes a MarkdownBuilder"
            )

        # Add optional components
        if prepend_table_of_contents:
            self._ensure_table_of_contents_exists_in_registry()
            final_markdown = "[toc]\n\n" + final_markdown

        if append_divider:
            self._ensure_divider_exists_in_registry()
            final_markdown = final_markdown + "\n\n---\n"

        processed_markdown = self._process_markdown_whitespace(final_markdown)

        try:
            blocks = await self._markdown_to_notion_converter.convert(
                processed_markdown
            )

            result = await self._block_client.append_block_children(
                block_id=self.page_id, children=blocks
            )

            if result:
                self.logger.debug("Successfully appended %d blocks", len(blocks))
                return processed_markdown
            else:
                self.logger.error("Failed to append blocks")
                return None

        except Exception as e:
            self.logger.error("Error appending markdown: %s", str(e), exc_info=True)
            return None

    def _process_markdown_whitespace(self, markdown_text: str) -> str:
        """Process markdown text to normalize whitespace while preserving code blocks."""
        lines = markdown_text.split("\n")
        if not lines:
            return ""

        return self._process_whitespace_lines(lines)

    def _process_whitespace_lines(self, lines: list[str]) -> str:
        """Process all lines and return the processed markdown."""
        processed_lines = []
        in_code_block = False
        current_code_block = []

        for line in lines:
            processed_lines, in_code_block, current_code_block = (
                self._process_single_line(
                    line, processed_lines, in_code_block, current_code_block
                )
            )

        return "\n".join(processed_lines)

    def _process_single_line(
        self,
        line: str,
        processed_lines: list[str],
        in_code_block: bool,
        current_code_block: list[str],
    ) -> tuple[list[str], bool, list[str]]:
        """Process a single line and return updated state."""
        if self._is_code_block_marker(line):
            return self._handle_code_block_marker(
                line, processed_lines, in_code_block, current_code_block
            )
        if in_code_block:
            current_code_block.append(line)
            return processed_lines, in_code_block, current_code_block
        else:
            processed_lines.append(line.lstrip())
            return processed_lines, in_code_block, current_code_block

    def _handle_code_block_marker(
        self,
        line: str,
        processed_lines: list[str],
        in_code_block: bool,
        current_code_block: list[str],
    ) -> tuple[list[str], bool, list[str]]:
        """Handle code block start/end markers."""
        if not in_code_block:
            return self._start_code_block(line, processed_lines)
        else:
            return self._end_code_block(processed_lines, current_code_block)

    def _start_code_block(
        self, line: str, processed_lines: list[str]
    ) -> tuple[list[str], bool, list[str]]:
        """Start a new code block."""
        processed_lines.append(self._normalize_code_block_start(line))
        return processed_lines, True, []

    def _end_code_block(
        self, processed_lines: list[str], current_code_block: list[str]
    ) -> tuple[list[str], bool, list[str]]:
        """End the current code block."""
        processed_lines.extend(self._normalize_code_block_content(current_code_block))
        processed_lines.append("```")
        return processed_lines, False, []

    def _is_code_block_marker(self, line: str) -> bool:
        """Check if line is a code block marker."""
        return line.lstrip().startswith("```")

    def _normalize_code_block_start(self, line: str) -> str:
        """Normalize code block opening marker."""
        language = line.lstrip().replace("```", "", 1).strip()
        return "```" + language

    def _normalize_code_block_content(self, code_lines: list[str]) -> list[str]:
        """Normalize code block indentation."""
        if not code_lines:
            return []

        # Find minimum indentation from non-empty lines
        non_empty_lines = [line for line in code_lines if line.strip()]
        if not non_empty_lines:
            return [""] * len(code_lines)

        min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
        if min_indent == 0:
            return code_lines

        # Remove common indentation
        return ["" if not line.strip() else line[min_indent:] for line in code_lines]

    def _ensure_table_of_contents_exists_in_registry(self) -> None:
        """Ensure TableOfContents is registered in the block registry."""
        self.block_registry.register(TableOfContentsElement)

    def _ensure_divider_exists_in_registry(self) -> None:
        """Ensure DividerBlock is registered in the block registry."""
        self.block_registry.register(DividerElement)
