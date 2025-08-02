import re
from typing import Optional, Tuple, Callable, Any

from notionary.blocks import (
    NotionBlockElement,
    NotionBlockResult,
    ElementPromptContent,
    ElementPromptBuilder,
)
from notionary.blocks.shared.models import Block, RichTextObject


class ToggleElement(NotionBlockElement):
    """
    Improved ToggleElement class using pipe syntax instead of indentation.
    """

    TOGGLE_PATTERN = re.compile(r"^[+]{3}\s+(.+)$")
    PIPE_CONTENT_PATTERN = re.compile(r"^\|\s?(.*)$")

    TRANSCRIPT_TOGGLE_PATTERN = re.compile(r"^[+]{3}\s+Transcript$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if the text is a markdown toggle."""
        return bool(ToggleElement.TOGGLE_PATTERN.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if the block is a Notion toggle block."""
        return block.type == "toggle"

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown toggle line to Notion toggle block."""
        toggle_match = ToggleElement.TOGGLE_PATTERN.match(text.strip())
        if not toggle_match:
            return None

        # Extract toggle title
        title = toggle_match.group(1)

        return {
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": title}}],
                "color": "default",
                "children": [],
            },
        }

    @classmethod
    def extract_nested_content(
        cls, lines: list[str], start_index: int
    ) -> Tuple[list[str], int]:
        """
        Extracts the nested content lines of a toggle block using pipe syntax.

        Args:
            lines: All lines of text.
            start_index: Starting index to look for nested content.

        Returns:
            Tuple of (nested_content_lines, next_line_index)
        """
        nested_content = []
        current_index = start_index

        while current_index < len(lines):
            current_line = lines[current_index]

            # Case 1: Empty line - could be part of the content if next line is a pipe line
            if not current_line.strip():
                if ToggleElement.is_next_line_pipe_content(lines, current_index):
                    nested_content.append("")
                    current_index += 1
                    continue
                else:
                    # Empty line not followed by pipe ends the block
                    break

            # Case 2: Pipe-prefixed line - part of the nested content
            pipe_content = ToggleElement.extract_pipe_content(current_line)
            if pipe_content is not None:
                nested_content.append(pipe_content)
                current_index += 1
                continue

            # Case 3: Regular line - end of nested content
            break

        return nested_content, current_index

    @classmethod
    def is_next_line_pipe_content(cls, lines: list[str], current_index: int) -> bool:
        """Checks if the next line starts with a pipe prefix."""
        next_index = current_index + 1
        return (
            next_index < len(lines)
            and ToggleElement.PIPE_CONTENT_PATTERN.match(lines[next_index]) is not None
        )

    @classmethod
    def extract_pipe_content(cls, line: str) -> Optional[str]:
        """
        Extracts content from a line with pipe prefix.

        Returns:
            The content without the pipe, or None if not a pipe-prefixed line.
        """
        pipe_match = ToggleElement.PIPE_CONTENT_PATTERN.match(line)
        if pipe_match:
            return pipe_match.group(1)
        return None

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """
        Converts a Notion toggle block into markdown using pipe-prefixed lines.
        """
        if block.type != "toggle":
            return None

        if not block.toggle:
            return None

        toggle_data = block.toggle

        # Extract title from rich_text
        title = ToggleElement._extract_text_content(toggle_data.rich_text or [])

        # Create toggle line
        toggle_line = f"+++ {title}"

        # Process children if available
        children = toggle_data.children or []
        if not children:
            return toggle_line

        # Add a placeholder line for each child using pipe syntax
        child_lines = ["| [Nested content]" for _ in children]

        return toggle_line + "\n" + "\n".join(child_lines)

    @classmethod
    def is_multiline(cls) -> bool:
        """Toggle blocks can span multiple lines due to nested content."""
        return True

    @classmethod
    def _extract_text_content(cls, rich_text: list[RichTextObject]) -> str:
        """Extracts plain text content from Notion rich_text blocks."""
        result = ""
        for text_obj in rich_text:
            if hasattr(text_obj, "plain_text"):
                result += text_obj.plain_text or ""
            elif (
                hasattr(text_obj, "type")
                and text_obj.type == "text"
                and hasattr(text_obj, "text")
            ):
                result += text_obj.text.content or ""
            # Fallback for dict-style access (backward compatibility)
            elif isinstance(text_obj, dict):
                if text_obj.get("type") == "text":
                    result += text_obj.get("text", {}).get("content", "")
                elif "plain_text" in text_obj:
                    result += text_obj.get("plain_text", "")
        return result

    @classmethod
    def find_matches(
        cls,
        text: str,
        process_nested_content: Callable = None,
        context_aware: bool = True,
    ) -> list[Tuple[int, int, dict[str, Any]]]:
        """
        Finds all toggle elements in markdown using pipe syntax for nested content.

        Args:
            text: The markdown input.
            process_nested_content: Optional function to parse nested content into blocks.
            context_aware: Whether to skip contextually irrelevant transcript toggles.

        Returns:
            List of (start_pos, end_pos, block) tuples.
        """
        if not text:
            return []

        toggle_blocks = []
        lines = text.split("\n")
        current_line_index = 0

        while current_line_index < len(lines):
            current_line = lines[current_line_index]

            # Check if the current line is a toggle
            if not cls._is_toggle_line(current_line):
                current_line_index += 1
                continue

            # Skip transcript toggles if required by context
            if cls._should_skip_transcript_toggle(
                current_line, lines, current_line_index, context_aware
            ):
                current_line_index += 1
                continue

            # Create toggle block and determine character positions
            start_position = cls._calculate_start_position(lines, current_line_index)
            toggle_block = cls.markdown_to_notion(current_line)

            if not toggle_block:
                current_line_index += 1
                continue

            # Extract nested content
            nested_content, next_line_index = cls.extract_nested_content(
                lines, current_line_index + 1
            )
            end_position = cls._calculate_end_position(
                start_position, current_line, nested_content
            )

            # Process nested content if needed
            cls._process_nested_content_if_needed(
                nested_content, process_nested_content, toggle_block
            )

            # Save result
            toggle_blocks.append((start_position, end_position, toggle_block))
            current_line_index = next_line_index

        return toggle_blocks

    @classmethod
    def _is_toggle_line(cls, line: str) -> bool:
        """Checks whether the given line is a markdown toggle."""
        return bool(ToggleElement.TOGGLE_PATTERN.match(line.strip()))

    @classmethod
    def _should_skip_transcript_toggle(
        cls, line: str, lines: list[str], current_index: int, context_aware: bool
    ) -> bool:
        """Determines if a transcript toggle should be skipped based on the surrounding context."""
        is_transcript_toggle = cls.TRANSCRIPT_TOGGLE_PATTERN.match(line.strip())

        if not (context_aware and is_transcript_toggle):
            return False

        # Only keep transcript toggles that follow a list item
        has_list_item_before = current_index > 0 and lines[
            current_index - 1
        ].strip().startswith("- ")
        return not has_list_item_before

    @classmethod
    def _calculate_start_position(cls, lines: list[str], current_index: int) -> int:
        """Calculates the character start position of a line within the full text."""
        start_pos = 0
        for index in range(current_index):
            start_pos += len(lines[index]) + 1  # +1 for line break
        return start_pos

    @classmethod
    def _calculate_end_position(
        cls, start_pos: int, current_line: str, nested_content: list[str]
    ) -> int:
        """Calculates the end position of a toggle block including nested lines."""
        line_length = len(current_line)
        nested_content_length = sum(
            len(line) + 1 for line in nested_content
        )  # +1 for each line break
        return start_pos + line_length + nested_content_length

    @classmethod
    def _process_nested_content_if_needed(
        cls,
        nested_content: list[str],
        process_function: Optional[Callable],
        toggle_block: dict[str, Any],
    ) -> None:
        """Processes nested content using the provided function if applicable."""
        if not (nested_content and process_function):
            return

        nested_text = "\n".join(nested_content)
        nested_blocks = process_function(nested_text)

        if nested_blocks:
            toggle_block["toggle"]["children"] = nested_blocks

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the toggle element with pipe syntax examples.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Toggle elements are collapsible sections that help organize and hide detailed information."
            )
            .with_usage_guidelines(
                "Use toggles for supplementary information that's not essential for the first reading, "
                "such as details, examples, or technical information."
            )
            .with_syntax("+++ Toggle Title\n| Toggle content with pipe prefix")
            .with_examples(
                [
                    "+++ Key Findings\n| The research demonstrates **three main conclusions**:\n| 1. First important point\n| 2. Second important point",
                    "+++ FAQ\n| **Q: When should I use toggles?**\n| *A: Use toggles for supplementary information.*",
                ]
            )
            .build()
        )
