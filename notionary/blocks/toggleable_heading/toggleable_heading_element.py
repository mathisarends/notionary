import re
from typing import Optional, Tuple, Callable, Any

from notionary.blocks import (
    ElementPromptContent,
    ElementPromptBuilder,
    NotionBlockElement,
    NotionBlockResult,
)
from notionary.blocks.shared.models import Block
from notionary.blocks.shared.text_inline_formatter import TextInlineFormatter


class ToggleableHeadingElement(NotionBlockElement):
    """Handles conversion between Markdown collapsible headings and Notion toggleable heading blocks with pipe syntax."""

    PATTERN = re.compile(r"^\+(?P<level>#{1,3})\s+(?P<content>.+)$")
    PIPE_CONTENT_PATTERN = re.compile(r"^\|\s?(.*)$")

    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown collapsible heading."""
        return bool(ToggleableHeadingElement.PATTERN.match(text))

    @staticmethod
    def match_notion(block: Block) -> bool:
        """Check if block is a Notion toggleable heading."""
        block_type: str = block.type
        if not block_type.startswith("heading_") or block_type[-1] not in "123":
            return False

        # Get the heading content based on block type
        heading_content = block.get_block_content()
        if not heading_content:
            return False

        # Check if it has the is_toggleable property set to true
        return getattr(heading_content, "is_toggleable", False) is True

    @staticmethod
    def markdown_to_notion(text: str) -> NotionBlockResult:
        """Convert markdown collapsible heading to Notion toggleable heading block."""
        header_match = ToggleableHeadingElement.PATTERN.match(text)
        if not header_match:
            return None

        level = len(header_match.group(1))
        content = header_match.group(2)

        return {
            "type": f"heading_{level}",
            f"heading_{level}": {
                "rich_text": TextInlineFormatter.parse_inline_formatting(content),
                "is_toggleable": True,
                "color": "default",
                "children": [],  # Will be populated with nested content if needed
            },
        }

    @staticmethod
    def notion_to_markdown(block: Block) -> Optional[str]:
        """Convert Notion toggleable heading block to markdown collapsible heading with pipe syntax."""
        block_type = block.type

        if not block_type.startswith("heading_"):
            return None

        try:
            level = int(block_type[-1])
            if not 1 <= level <= 3:
                return None
        except ValueError:
            return None

        heading_content = block.get_block_content()
        if not heading_content:
            return None

        # Check if it's toggleable
        if not getattr(heading_content, "is_toggleable", False):
            return None

        rich_text = getattr(heading_content, "rich_text", [])
        text = TextInlineFormatter.extract_text_with_formatting(rich_text)
        prefix = "#" * level
        return f"+{prefix} {text or ''}"

    @staticmethod
    def is_multiline() -> bool:
        """Collapsible headings can have children, so they're multiline elements."""
        return True

    @classmethod
    def find_matches(
        cls,
        text: str,
        process_nested_content: Callable = None,
        context_aware: bool = True,
    ) -> list[Tuple[int, int, dict[str, Any]]]:
        """
        Find all collapsible heading matches in the text with pipe syntax for nested content.
        Improved version with reduced cognitive complexity.

        Args:
            text: The text to process
            process_nested_content: Optional callback function to process nested content
            context_aware: Whether to consider context when finding collapsible headings

        Returns:
            List of (start_pos, end_pos, block) tuples
        """
        if not text:
            return []

        collapsible_blocks = []
        lines = text.split("\n")
        line_index = 0

        while line_index < len(lines):
            current_line = lines[line_index]

            # Skip non-collapsible heading lines
            if not cls._is_collapsible_heading(current_line):
                line_index += 1
                continue

            # Process collapsible heading
            start_position = cls._calculate_line_position(lines, line_index)
            heading_block = cls.markdown_to_notion(current_line)

            if not heading_block:
                line_index += 1
                continue

            # Extract and process nested content
            nested_content, next_line_index = cls._extract_nested_content(
                lines, line_index + 1
            )
            end_position = cls._calculate_block_end_position(
                start_position, current_line, nested_content
            )

            cls._process_nested_content(
                heading_block, nested_content, process_nested_content
            )

            # Add block to results
            collapsible_blocks.append((start_position, end_position, heading_block))
            line_index = next_line_index

        return collapsible_blocks

    @classmethod
    def _is_collapsible_heading(cls, line: str) -> bool:
        """Check if a line represents a collapsible heading."""
        return bool(cls.PATTERN.match(line))

    @staticmethod
    def _calculate_line_position(lines: list[str], current_index: int) -> int:
        """Calculate the character position of a line in the text."""
        position = 0
        for i in range(current_index):
            position += len(lines[i]) + 1  # +1 for newline
        return position

    @classmethod
    def _extract_nested_content(
        cls, lines: list[str], start_index: int
    ) -> Tuple[list[str], int]:
        """
        Extract nested content with pipe syntax from lines following a collapsible heading.

        Args:
            lines: All text lines
            start_index: Index to start looking for nested content

        Returns:
            Tuple of (nested_content, next_line_index)
        """
        nested_content = []
        current_index = start_index

        while current_index < len(lines):
            current_line = lines[current_index]

            # Case 1: Empty line - check if it's followed by pipe content
            if not current_line.strip():
                if cls._is_next_line_pipe_content(lines, current_index):
                    nested_content.append("")
                    current_index += 1
                    continue

            # Case 2: Pipe content line - part of nested content
            pipe_content = cls._extract_pipe_content(current_line)
            if pipe_content is not None:
                nested_content.append(pipe_content)
                current_index += 1
                continue

            # Case 3: Another collapsible heading - ends current heading's content
            if cls.PATTERN.match(current_line):
                break

            # Case 4: Any other line - ends nested content
            break

        return nested_content, current_index

    @classmethod
    def _is_next_line_pipe_content(cls, lines: list[str], current_index: int) -> bool:
        """Check if the next line uses pipe syntax for nested content."""
        next_index = current_index + 1
        if next_index >= len(lines):
            return False
        return bool(cls.PIPE_CONTENT_PATTERN.match(lines[next_index]))

    @classmethod
    def _extract_pipe_content(cls, line: str) -> Optional[str]:
        """Extract content from a line with pipe prefix."""
        pipe_match = cls.PIPE_CONTENT_PATTERN.match(line)
        if not pipe_match:
            return None
        return pipe_match.group(1)

    @staticmethod
    def _calculate_block_end_position(
        start_position: int, heading_line: str, nested_content: list[str]
    ) -> int:
        """Calculate the end position of a collapsible heading block including nested content."""
        block_length = len(heading_line)
        if nested_content:
            # Add length of each nested content line plus newline
            nested_length = sum(len(line) + 1 for line in nested_content)
            block_length += nested_length
        return start_position + block_length

    @classmethod
    def _process_nested_content(
        cls,
        heading_block: dict[str, Any],
        nested_content: list[str],
        processor: Optional[Callable],
    ) -> None:
        """Process nested content with the provided callback function if available."""
        if not (nested_content and processor):
            return

        nested_text = "\n".join(nested_content)
        nested_blocks = processor(nested_text)

        if nested_blocks:
            block_type = heading_block["type"]
            heading_block[block_type]["children"] = nested_blocks

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the collapsible heading element with pipe syntax.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Collapsible headings combine heading structure with toggleable visibility."
            )
            .with_usage_guidelines(
                "Use when you want to create a structured section that can be expanded or collapsed."
            )
            .with_syntax("+# Collapsible Heading\n| Content with pipe prefix")
            .with_examples(
                [
                    "+# Main Collapsible Section\n| Content under the section",
                    "+## Subsection\n| This content is hidden until expanded",
                    "+### Detailed Information\n| Technical details go here",
                ]
            )
            .build()
        )
