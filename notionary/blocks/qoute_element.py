import re
from typing import Dict, Any, Optional, List, Tuple

from notionary.blocks import NotionBlockElement
from notionary.blocks import ElementPromptContent, ElementPromptBuilder


class QuoteElement(NotionBlockElement):
    """Class for converting between Markdown blockquotes and Notion quote blocks."""

    # Regular expression pattern to match Markdown blockquote lines
    # Matches lines that start with optional whitespace, followed by '>',
    # then optional whitespace, and captures any text after that
    quote_pattern = re.compile(r"^\s*>\s?(.*)", re.MULTILINE)

    @classmethod
    def find_matches(cls, text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Find all blockquote matches in the text and return their positions and blocks.
        """
        matches = []
        quote_matches = list(QuoteElement.quote_pattern.finditer(text))

        if not quote_matches:
            return []

        current_match_index = 0
        while current_match_index < len(quote_matches):
            start_match = quote_matches[current_match_index]
            start_pos = start_match.start()

            next_match_index = current_match_index + 1
            while next_match_index < len(
                quote_matches
            ) and QuoteElement.is_consecutive_quote(
                text, quote_matches, next_match_index
            ):
                next_match_index += 1

            end_pos = quote_matches[next_match_index - 1].end()
            quote_text = text[start_pos:end_pos]

            block = QuoteElement.markdown_to_notion(quote_text)
            if block:
                matches.append((start_pos, end_pos, block))

            current_match_index = next_match_index

        return matches

    @classmethod
    def is_consecutive_quote(cls, text: str, quote_matches: List, index: int) -> bool:
        """Checks if the current quote is part of the previous quote sequence."""
        prev_end = quote_matches[index - 1].end()
        curr_start = quote_matches[index].start()
        gap_text = text[prev_end:curr_start]

        if gap_text.count("\n") == 1:
            return True

        if gap_text.strip() == "" and gap_text.count("\n") <= 2:
            return True

        return False

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown blockquote to Notion block."""
        if not text:
            return None

        # Check if it's a blockquote
        if not QuoteElement.quote_pattern.search(text):
            return None

        # Extract quote content
        lines = text.split("\n")
        quote_lines = []

        # Extract content from each line
        for line in lines:
            quote_match = QuoteElement.quote_pattern.match(line)
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

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
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

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        return bool(QuoteElement.quote_pattern.search(text))

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.get("type") == "quote"

    @classmethod
    def is_multiline(cls) -> bool:
        """Blockquotes can span multiple lines."""
        return True

    @classmethod
    def _extract_text_content(cls, rich_text: List[Dict[str, Any]]) -> str:
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
        return (
            ElementPromptBuilder()
            .with_description(
                "Creates blockquotes that visually distinguish quoted text."
            )
            .with_usage_guidelines(
                "Use blockquotes for quoting external sources, highlighting important statements, "
                "or creating visual emphasis for key information."
            )
            .with_syntax("> Quoted text")
            .with_examples(
                [
                    "> This is a simple blockquote",
                    "> This is a multi-line quote\n> that continues on the next line",
                    "> Important note:\n> This quote spans\n> multiple lines.",
                ]
            )
            .build()
        )
