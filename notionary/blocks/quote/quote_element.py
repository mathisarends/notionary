import re
from typing import Dict, Any, Optional, List, Tuple

from notionary.blocks import NotionBlockElement, NotionBlockResult
from notionary.blocks import ElementPromptContent, ElementPromptBuilder

class QuoteElement(NotionBlockElement):
    """
    Handles conversion between Markdown quotes and Notion quote blocks.
    Markdown quote syntax:
    - [quote](Simple quote text)
    """

    # Einzeilig, kein Author, kein Anführungszeichen-Kram mehr!
    PATTERN = re.compile(r'^\[quote\]\(([^\n\r]+)\)$')

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        m = cls.PATTERN.match(text.strip())
        # Nur gültig, wenn etwas nicht-leeres drinsteht
        return bool(m and m.group(1).strip())

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        return block.get("type") == "quote"

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        if not text:
            return None

        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        content = match.group(1).strip()
        if not content:
            return None

        rich_text = [{"type": "text", "text": {"content": content}}]
        return {"type": "quote", "quote": {"rich_text": rich_text, "color": "default"}}

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        if block.get("type") != "quote":
            return None

        rich_text = block.get("quote", {}).get("rich_text", [])
        content = cls._extract_text_content(rich_text)
        if not content.strip():
            return None

        return f"[quote]({content.strip()})"

    @classmethod
    def find_matches(cls, text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        matches = []
        for match in re.finditer(r"^\[quote\]\([^\n\r]+\)$", text, re.MULTILINE):
            candidate = match.group(0)
            block = cls.markdown_to_notion(candidate)
            if block:
                matches.append((match.start(), match.end(), block))
        return matches

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def _extract_text_content(cls, rich_text: List[Dict[str, Any]]) -> str:
        return "".join(
            t.get("text", {}).get("content", "")
            for t in rich_text
            if t.get("type") == "text"
        )

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description("Creates blockquotes that visually distinguish quoted text.")
            .with_usage_guidelines(
                "Use quotes for quoting external sources, highlighting important statements, "
                "or creating visual emphasis for key information."
            )
            .with_syntax('[quote](Quote text)')
            .with_examples([
                "[quote](This is a simple blockquote)",
                "[quote](Knowledge is power)",
            ])
            .build()
        )
