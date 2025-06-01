import re
from typing import Dict, Any, Optional, List, Tuple, Callable

from notionary.elements.notion_block_element import NotionBlockElement
from notionary.page.formatting.spacer_rules import SPACER_MARKER
from notionary.prompting.element_prompt_content import (
    ElementPromptBuilder,
    ElementPromptContent,
)


class ColumnElement(NotionBlockElement):
    """
    Handles conversion between custom Markdown column syntax and Notion column blocks.

    Markdown column syntax:
    ::: columns
    ::: column
    Content for first column
    :::
    ::: column
    Content for second column
    :::
    :::

    This creates a column layout in Notion with the specified content in each column.
    """

    COLUMNS_START = re.compile(r"^:::\s*columns\s*$")
    COLUMN_START = re.compile(r"^:::\s*column\s*$")
    BLOCK_END = re.compile(r"^:::\s*$")

    _converter_callback = None

    @classmethod
    def set_converter_callback(
        cls, callback: Callable[[str], List[Dict[str, Any]]]
    ) -> None:
        """
        Setze die Callback-Funktion, die zum Konvertieren von Markdown zu Notion-Blöcken verwendet wird.

        Args:
            callback: Funktion, die Markdown-Text annimmt und eine Liste von Notion-Blöcken zurückgibt
        """
        cls._converter_callback = callback

    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text starts a columns block."""
        return bool(ColumnElement.COLUMNS_START.match(text.strip()))

    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion column_list."""
        return block.get("type") == "column_list"

    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """
        Convert markdown column syntax to Notion column blocks.

        Note: This only processes the first line (columns start).
        The full column content needs to be processed separately.
        """
        if not ColumnElement.COLUMNS_START.match(text.strip()):
            return None

        # Create an empty column_list block
        # Child columns will be added by the column processor
        return {"type": "column_list", "column_list": {"children": []}}

    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion column_list block to markdown column syntax."""
        if block.get("type") != "column_list":
            return None

        column_children = block.get("column_list", {}).get("children", [])

        # Start the columns block
        result = ["::: columns"]

        # Process each column
        for column_block in column_children:
            if column_block.get("type") == "column":
                result.append("::: column")

            for _ in column_block.get("column", {}).get("children", []):
                result.append("  [Column content]")  # Placeholder

                result.append(":::")

        # End the columns block
        result.append(":::")

        return "\n".join(result)

    @staticmethod
    def is_multiline() -> bool:
        """Column blocks span multiple lines."""
        return True

    @classmethod
    def find_matches(
        cls, text: str, converter_callback: Optional[Callable] = None
    ) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Find all column block matches in the text and return their positions and blocks.

        Args:
            text: The input markdown text
            converter_callback: Optional callback to convert nested content

        Returns:
            List of tuples (start_pos, end_pos, block)
        """
        # Wenn ein Callback übergeben wurde, nutze diesen, sonst die gespeicherte Referenz
        converter = converter_callback or cls._converter_callback
        if not converter:
            raise ValueError(
                "No converter callback provided for ColumnElement. Call set_converter_callback first or provide converter_callback parameter."
            )

        matches = []
        lines = text.split("\n")
        i = 0

        while i < len(lines):
            # Skip non-column lines
            if not ColumnElement.COLUMNS_START.match(lines[i].strip()):
                i += 1
                continue

            # Process a column block and add to matches
            column_block_info = cls._process_column_block(
                lines=lines, start_index=i, converter_callback=converter
            )
            matches.append(column_block_info)

            # Skip to the end of the processed column block
            i = column_block_info[3]  # i is returned as the 4th element in the tuple

        return [(start, end, block) for start, end, block, _ in matches]

    @classmethod
    def _process_column_block(
        cls, lines: List[str], start_index: int, converter_callback: Callable
    ) -> Tuple[int, int, Dict[str, Any], int]:
        """
        Process a complete column block structure from the given starting line.

        Args:
            lines: All lines of the text
            start_index: Index of the column block start line
            converter_callback: Callback function to convert markdown to notion blocks

        Returns:
            Tuple of (start_pos, end_pos, block, next_line_index)
        """
        columns_start = start_index
        columns_block = cls.markdown_to_notion(lines[start_index].strip())
        columns_children = []

        next_index = cls._collect_columns(
            lines, start_index + 1, columns_children, converter_callback
        )

        # Add columns to the main block
        if columns_children:
            columns_block["column_list"]["children"] = columns_children

        # Calculate positions
        start_pos = sum(len(lines[j]) + 1 for j in range(columns_start))
        end_pos = sum(len(lines[j]) + 1 for j in range(next_index))

        return (start_pos, end_pos, columns_block, next_index)

    @classmethod
    def _collect_columns(
        cls,
        lines: List[str],
        start_index: int,
        columns_children: List[Dict[str, Any]],
        converter_callback: Callable,
    ) -> int:
        """
        Collect all columns within a column block structure.

        Args:
            lines: All lines of the text
            start_index: Index to start collecting from
            columns_children: List to append collected columns to
            converter_callback: Callback function to convert column content

        Returns:
            Next line index after all columns have been processed
        """
        i = start_index
        in_column = False
        column_content = []

        while i < len(lines):
            current_line = lines[i].strip()

            if cls.COLUMNS_START.match(current_line):
                break

            if cls.COLUMN_START.match(current_line):
                cls._finalize_column(
                    column_content, columns_children, in_column, converter_callback
                )
                column_content = []
                in_column = True
                i += 1
                continue

            if cls.BLOCK_END.match(current_line) and in_column:
                cls._finalize_column(
                    column_content, columns_children, in_column, converter_callback
                )
                column_content = []
                in_column = False
                i += 1
                continue

            if cls.BLOCK_END.match(current_line) and not in_column:
                i += 1
                break

            if in_column:
                column_content.append(lines[i])

            i += 1

        cls._finalize_column(
            column_content, columns_children, in_column, converter_callback
        )

        return i

    @staticmethod
    def _finalize_column(
        column_content: List[str],
        columns_children: List[Dict[str, Any]],
        in_column: bool,
        converter_callback: Callable,
    ) -> None:
        """
        Finalize a column by processing its content and adding it to the columns_children list.

        Args:
            column_content: Content lines of the column
            columns_children: List to append the column block to
            in_column: Whether we're currently in a column (if False, does nothing)
            converter_callback: Callback function to convert column content
        """
        if not (in_column and column_content):
            return

        processed_content = ColumnElement._preprocess_column_content(column_content)

        column_blocks = converter_callback("\n".join(processed_content))

        # Create column block
        column_block = {"type": "column", "column": {"children": column_blocks}}
        columns_children.append(column_block)

    @classmethod
    def is_multiline(cls) -> bool:
        """Column blocks span multiple lines."""
        return True

    @staticmethod
    def _preprocess_column_content(lines: List[str]) -> List[str]:
        """
        Preprocess column content to handle special cases like first headings.

        This removes any spacer markers that might have been added before the first
        heading in a column, as each column should have its own heading context.

        Args:
            lines: The lines of content for the column

        Returns:
            Processed lines ready for conversion
        """
        from notionary.page.formatting.markdown_to_notion_converter import (
            MarkdownToNotionConverter,
        )

        processed_lines = []
        found_first_heading = False

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this is a heading line
            if re.match(r"^(#{1,6})\s+(.+)$", line.strip()):
                # If it's the first heading, look ahead to check for spacer
                if (
                    not found_first_heading
                    and i > 0
                    and processed_lines
                    and processed_lines[-1] == SPACER_MARKER
                ):
                    # Remove spacer before first heading in column
                    processed_lines.pop()

                found_first_heading = True

            processed_lines.append(line)
            i += 1

        return processed_lines

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the column layout element.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Creates a multi-column layout that displays content side by side."
            )
            .with_usage_guidelines(
                "Use columns sparingly, only for direct comparisons or when parallel presentation significantly improves readability. "
                "Best for pros/cons lists, feature comparisons, or pairing images with descriptions."
            )
            .with_avoidance_guidelines(
                "Avoid overusing as it can complicate document structure. Do not use for simple content that works better in linear format."
            )
            .with_syntax(
                "::: columns\n"
                "::: column\n"
                "Content for first column\n"
                ":::\n"
                "::: column\n"
                "Content for second column\n"
                ":::\n"
                ":::"
            )
            .with_examples(
                [
                    "::: columns\n"
                    "::: column\n"
                    "## Features\n"
                    "- Fast response time\n"
                    "- Intuitive interface\n"
                    "- Regular updates\n"
                    ":::\n"
                    "::: column\n"
                    "## Benefits\n"
                    "- Increased productivity\n"
                    "- Better collaboration\n"
                    "- Simplified workflows\n"
                    ":::\n"
                    ":::",
                    "::: columns\n"
                    "::: column\n"
                    "![Image placeholder](/api/placeholder/400/320)\n"
                    ":::\n"
                    "::: column\n"
                    "This text appears next to the image, creating a media-with-caption style layout.\n"
                    ":::\n"
                    ":::",
                ]
            )
            .build()
        )
