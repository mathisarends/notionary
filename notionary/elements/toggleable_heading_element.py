import re
from typing import Dict, Any, Optional, List, Tuple, Callable

from notionary.elements.notion_block_element import NotionBlockElement
from notionary.elements.prompts.element_prompt_content import ElementPromptContent
from notionary.elements.text_inline_formatter import TextInlineFormatter


class ToggleableHeadingElement(NotionBlockElement):
    """Handles conversion between Markdown collapsible headings and Notion toggleable heading blocks with pipe syntax."""

    PATTERN = re.compile(r"^\+(?P<level>#{1,3})\s+(?P<content>.+)$")
    PIPE_CONTENT_PATTERN = re.compile(r"^\|\s?(.*)$")

    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown collapsible heading."""
        return bool(ToggleableHeadingElement.PATTERN.match(text))

    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion toggleable heading."""
        block_type: str = block.get("type", "")
        if not block_type.startswith("heading_") or block_type[-1] not in "123":
            return False

        # Check if it has the is_toggleable property set to true
        heading_data = block.get(block_type, {})
        return heading_data.get("is_toggleable", False) is True

    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
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
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion toggleable heading block to markdown collapsible heading with pipe syntax."""
        block_type = block.get("type", "")

        if not block_type.startswith("heading_"):
            return None

        try:
            level = int(block_type[-1])
            if not 1 <= level <= 3:
                return None
        except ValueError:
            return None

        heading_data = block.get(block_type, {})

        # Check if it's toggleable
        if not heading_data.get("is_toggleable", False):
            return None

        rich_text = heading_data.get("rich_text", [])
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
    ) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Find all collapsible heading matches in the text with pipe syntax for nested content.

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

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if line is a collapsible heading
            if not cls.match_markdown(line):
                i += 1
                continue

            start_pos = 0
            for j in range(i):
                start_pos += len(lines[j]) + 1

            heading_block = cls.markdown_to_notion(line)
            if not heading_block:
                i += 1
                continue

            # Extract nested content (lines with pipe prefix)
            nested_content = []
            next_index = i + 1

            while next_index < len(lines):
                next_line = lines[next_index]

                # Empty line is still part of nested content if followed by pipe content
                if not next_line.strip():
                    # Look ahead to see if next line is pipe content
                    if (next_index + 1 < len(lines) and 
                        cls.PIPE_CONTENT_PATTERN.match(lines[next_index + 1])):
                        nested_content.append("")
                        next_index += 1
                        continue
                    else:
                        # Empty line not followed by pipe content ends the nested content
                        break

                # Check if line uses pipe syntax (part of nested content)
                pipe_match = cls.PIPE_CONTENT_PATTERN.match(next_line)
                if pipe_match:
                    # Extract content without the pipe
                    content_line = pipe_match.group(1)
                    nested_content.append(content_line)
                    next_index += 1
                    continue

                # Check if the next line is another heading which would end the current content
                if cls.PATTERN.match(next_line):
                    break

                # Non-pipe, non-empty, non-heading line
                break

            # Calculate ending position
            end_pos = start_pos + len(line)
            if nested_content:
                end_pos += sum(len(l) + 1 for l in nested_content)  # +1 for each newline

            # Process nested content if provided
            if nested_content and process_nested_content:
                nested_text = "\n".join(nested_content)
                nested_blocks = process_nested_content(nested_text)
                if nested_blocks:
                    heading_block[heading_block["type"]]["children"] = nested_blocks

            collapsible_blocks.append((start_pos, end_pos, heading_block))
            i = next_index

        return collapsible_blocks

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the collapsible heading element with pipe syntax.
        """
        return {
            "description": "Collapsible headings combine heading structure with toggleable visibility.",
            "when_to_use": "Use when you want to create a structured section that can be expanded or collapsed.",
            "syntax": "+# Collapsible Heading\n| Content with pipe prefix",
            "examples": [
                "+# Main Collapsible Section\n| Content under the section",
                "+## Subsection\n| This content is hidden until expanded",
                "+### Detailed Information\n| Technical details go here",
            ],
        }

    @staticmethod
    def _extract_text_content(rich_text: List[Dict[str, Any]]) -> str:
        """Extract plain text content from Notion rich_text elements."""
        result = ""
        for text_obj in rich_text:
            if text_obj.get("type") == "text":
                result += text_obj.get("text", {}).get("content", "")
            elif "plain_text" in text_obj:
                result += text_obj.get("plain_text", "")
        return result