import re
from typing import Dict, Any, Optional, List, Tuple
from notionary.elements.notion_block_element import NotionBlockElement
from notionary.elements.prompts.element_prompt_content import ElementPromptContent


class QuoteElement(NotionBlockElement):
    """Class for converting between Markdown blockquotes and Notion quote blocks."""

    @staticmethod
    def find_matches(text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Find all blockquote matches in the text and return their positions and blocks.

        Args:
            text: The input markdown text

        Returns:
            List of tuples (start_pos, end_pos, block)
        """
        quote_pattern = re.compile(r"^\s*>\s?(.*)", re.MULTILINE)
        matches = []

        # Find all potential quote line matches
        quote_matches = list(quote_pattern.finditer(text))
        if not quote_matches:
            return []

        # Group consecutive quote lines
        i = 0
        while i < len(quote_matches):
            start_match = quote_matches[i]
            start_pos = start_match.start()

            # Find consecutive quote lines
            j = i + 1
            while j < len(quote_matches):
                # Check if this is the next line (considering newlines)
                if (
                    text[quote_matches[j - 1].end() : quote_matches[j].start()].count(
                        "\n"
                    )
                    == 1
                    or
                    # Or if it's an empty line followed by a quote line
                    (
                        text[
                            quote_matches[j - 1].end() : quote_matches[j].start()
                        ].strip()
                        == ""
                        and text[
                            quote_matches[j - 1].end() : quote_matches[j].start()
                        ].count("\n")
                        <= 2
                    )
                ):
                    j += 1
                else:
                    break

            end_pos = quote_matches[j - 1].end()
            quote_text = text[start_pos:end_pos]

            # Create the block
            block = QuoteElement.markdown_to_notion(quote_text)
            if block:
                matches.append((start_pos, end_pos, block))

            i = j

        return matches

    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown blockquote to Notion block."""
        if not text:
            return None

        quote_pattern = re.compile(r"^\s*>\s?(.*)", re.MULTILINE)

        # Check if it's a blockquote
        if not quote_pattern.search(text):
            return None

        # Extract quote content
        lines = text.split("\n")
        quote_lines = []

        # Extract content from each line
        for line in lines:
            quote_match = quote_pattern.match(line)
            if quote_match:
                content = quote_match.group(1)
                quote_lines.append(content)
            elif not line.strip() and quote_lines:
                # Allow empty lines within the quote
                quote_lines.append("")

        if not quote_lines:
            return None

        quote_content = "\n".join(quote_lines).strip()

        rich_text = [{"type": "text", "text": {"content": quote_content}}]

        return {"type": "quote", "quote": {"rich_text": rich_text, "color": "default"}}

    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion quote block to markdown."""
        if block.get("type") != "quote":
            return None

        rich_text = block.get("quote", {}).get("rich_text", [])

        # Extract the text content
        content = QuoteElement._extract_text_content(rich_text)

        # Format as markdown blockquote
        lines = content.split("\n")
        formatted_lines = []

        # Add each line with blockquote prefix
        for line in lines:
            formatted_lines.append(f"> {line}")

        return "\n".join(formatted_lines)

    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        quote_pattern = re.compile(r"^\s*>\s?(.*)", re.MULTILINE)
        return bool(quote_pattern.search(text))

    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.get("type") == "quote"

    @staticmethod
    def is_multiline() -> bool:
        """Blockquotes can span multiple lines."""
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
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the quote element.
        """
        return {
            "description": "Creates blockquotes that visually distinguish quoted text.",
            "when_to_use": (
                "Use blockquotes for quoting external sources, highlighting important statements, "
                "or creating visual emphasis for key information."
            ),
            "syntax": "> Quoted text",
            "examples": [
                "> This is a simple blockquote",
                "> This is a multi-line quote\n> that continues on the next line",
                "> Important note:\n> This quote spans\n> multiple lines.",
            ],
        }
