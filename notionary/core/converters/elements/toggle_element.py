import re
from typing import Dict, Any, Optional, List, Tuple, Callable

from notionary.core.converters.elements.notion_block_element import NotionBlockElement


class ToggleElement(NotionBlockElement):
    """
    Verbesserte ToggleElement-Klasse, die Kontext berücksichtigt.
    """

    TOGGLE_PATTERN = re.compile(r"^[+]{3}\s+(.+)$")
    INDENT_PATTERN = re.compile(r"^(\s{2,}|\t+)(.+)$")

    # Ein neues Pattern, um spezifisch nach der "Transcript" Überschrift zu suchen
    TRANSCRIPT_TOGGLE_PATTERN = re.compile(r"^[+]{3}\s+Transcript$")

    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown toggle."""
        return bool(ToggleElement.TOGGLE_PATTERN.match(text.strip()))

    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion toggle."""
        return block.get("type") == "toggle"

    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown toggle to Notion toggle block."""
        toggle_match = ToggleElement.TOGGLE_PATTERN.match(text.strip())
        if not toggle_match:
            return None

        # Extract content
        title = toggle_match.group(1)

        return {
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": title}}],
                "color": "default",
                "children": [],  # Will be populated with nested content
            },
        }

    @staticmethod
    def extract_nested_content(
        lines: List[str], start_index: int
    ) -> Tuple[List[str], int]:
        """
        Extract the nested content of a toggle element.

        Args:
            lines: All lines of text
            start_index: Starting index to look for nested content

        Returns:
            Tuple of (nested_content_lines, next_line_index)
        """
        nested_content = []
        current_index = start_index

        while current_index < len(lines):
            line = lines[current_index]

            # Empty line is still part of toggle content
            if not line.strip():
                nested_content.append("")
                current_index += 1
                continue

            # Check if line is indented (part of toggle content)
            if line.startswith("  ") or line.startswith("\t"):
                # Extract content with indentation removed
                content_line = ToggleElement._remove_indentation(line)
                nested_content.append(content_line)
                current_index += 1
                continue

            # Non-indented, non-empty line marks the end of toggle content
            break

        return nested_content, current_index

    @staticmethod
    def _remove_indentation(line: str) -> str:
        """Remove indentation from a line, handling both spaces and tabs."""
        if line.startswith("\t"):
            return line[1:]
        else:
            # Find number of leading spaces
            leading_spaces = len(line) - len(line.lstrip(" "))
            # Remove at least 2 spaces, but not more than what's there
            return line[min(2, leading_spaces) :]

    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion toggle block to markdown toggle."""
        if block.get("type") != "toggle":
            return None

        toggle_data = block.get("toggle", {})

        # Extract title from rich_text
        title = ToggleElement._extract_text_content(toggle_data.get("rich_text", []))

        # Create the toggle line
        toggle_line = f"+++ {title}"

        # Process children if any
        children = toggle_data.get("children", [])
        if children:
            child_lines = []
            for child_block in children:
                # This would need to be handled by a full converter that can dispatch
                # to the appropriate element type for each child block
                child_markdown = "  [Nested content]"  # Placeholder
                child_lines.append(f"  {child_markdown}")

            return toggle_line + "\n" + "\n".join(child_lines)

        return toggle_line

    @staticmethod
    def is_multiline() -> bool:
        """Toggle blocks can span multiple lines due to their nested content."""
        return True

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

    @classmethod
    def find_matches(
        cls,
        text: str,
        process_nested_content: Callable = None,
        context_aware: bool = True,
    ) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Verbesserte find_matches-Methode, die Kontext beim Finden von Toggles berücksichtigt.

        Args:
            text: Der zu durchsuchende Text
            process_nested_content: Optionale Callback-Funktion zur Verarbeitung verschachtelter Inhalte
            context_aware: Ob der Kontext (vorhergehende Zeilen) beim Finden von Toggles berücksichtigt werden soll

        Returns:
            Liste von (start_pos, end_pos, block) Tupeln
        """
        if not text:
            return []

        toggle_blocks = []
        lines = text.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if line is a toggle
            if not cls.match_markdown(line):
                i += 1
                continue

            is_transcript_toggle = cls.TRANSCRIPT_TOGGLE_PATTERN.match(line.strip())

            if context_aware and is_transcript_toggle:
                if i > 0 and lines[i - 1].strip().startswith("- "):
                    pass
                else:
                    i += 1
                    continue

            start_pos = 0
            for j in range(i):
                start_pos += len(lines[j]) + 1

            toggle_block = cls.markdown_to_notion(line)
            if not toggle_block:
                i += 1
                continue

            # Extract nested content
            nested_content, next_index = cls.extract_nested_content(lines, i + 1)

            # Calculate ending position
            end_pos = start_pos + len(line) + sum(len(l) + 1 for l in nested_content)

            if nested_content and process_nested_content:
                nested_text = "\n".join(nested_content)
                nested_blocks = process_nested_content(nested_text)
                if nested_blocks:
                    toggle_block["toggle"]["children"] = nested_blocks

            toggle_blocks.append((start_pos, end_pos, toggle_block))

            i = next_index

        return toggle_blocks
