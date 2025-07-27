import re
from typing import Dict, Any, Optional, List, Tuple

from notionary.blocks import NotionBlockElement, NotionBlockResult
from notionary.blocks import ElementPromptContent, ElementPromptBuilder


class QuoteElement(NotionBlockElement):
    """
    Handles conversion between Markdown quotes and Notion quote blocks.

    Markdown quote syntax:
    - [quote](Simple quote text) - Simple quote with text only
    - [quote](Multi-line quote text "Author") - Quote with text and author

    Where:
    - Text is the required quote content
    - Author is an optional attribution (enclosed in quotes)
    """

    # Regex pattern for quote syntax with optional author
    PATTERN = re.compile(
        r"^\[quote\]\("  # [quote]( prefix
        + r'([^"]+?)'  # Quote text (required)
        + r'(?:\s+"([^"]+)")?'  # Optional author in quotes
        + r"\)$"  # closing parenthesis
    )

    @classmethod
    def find_matches(cls, text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Find all quote matches in the text and return their positions and blocks.
        """
        matches = []
        quote_matches = list(cls.PATTERN.finditer(text))

        if not quote_matches:
            return []

        current_match_index = 0
        while current_match_index < len(quote_matches):
            start_match = quote_matches[current_match_index]
            start_pos = start_match.start()

            next_match_index = current_match_index + 1
            while next_match_index < len(quote_matches) and cls.is_consecutive_quote(
                text, quote_matches, next_match_index
            ):
                next_match_index += 1

            end_pos = quote_matches[next_match_index - 1].end()
            quote_text = text[start_pos:end_pos]

            block = cls.markdown_to_notion(quote_text)
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
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown quote to Notion block."""
        if not text:
            return None

        # Check if it's a quote
        quote_match = cls.PATTERN.match(text.strip())
        if not quote_match:
            return None

        content = quote_match.group(1)
        author = quote_match.group(2)

        if not content:
            return None

        # Build quote text with author if provided
        quote_content = content.strip()
        if author:
            quote_content += f"\n— {author}"

        rich_text = [{"type": "text", "text": {"content": quote_content}}]

        return {"type": "quote", "quote": {"rich_text": rich_text, "color": "default"}}

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion quote block to markdown."""
        if block.get("type") != "quote":
            return None

        rich_text = block.get("quote", {}).get("rich_text", [])

        # Extract the text content
        content = cls._extract_text_content(rich_text)

        # Parse content and author
        content_text, author = cls._parse_quote_content(content)

        if author:
            return f'[quote]({content_text} "{author}")'

        return f"[quote]({content_text})"

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        return text.strip().startswith("[quote]") and bool(
            cls.PATTERN.match(text.strip())
        )

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.get("type") == "quote"

    @classmethod
    def is_multiline(cls) -> bool:
        """Quotes are single-line elements."""
        return False

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
    def _parse_quote_content(cls, content: str) -> tuple[str, str]:
        """Parse quote content to extract text and author."""
        if "\n— " in content:
            parts = content.split("\n— ", 1)
            return parts[0].strip(), parts[1].strip()
        return content.strip(), ""

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
                "Use quotes for quoting external sources, highlighting important statements, "
                "or creating visual emphasis for key information."
            )
            .with_syntax('[quote](Quote text "Optional author")')
            .with_examples(
                [
                    "[quote](This is a simple blockquote)",
                    '[quote](The only way to do great work is to love what you do "Steve Jobs")',
                    "[quote](Knowledge is power)",
                    '[quote](Innovation distinguishes between a leader and a follower "Steve Jobs")',
                ]
            )
            .build()
        )
