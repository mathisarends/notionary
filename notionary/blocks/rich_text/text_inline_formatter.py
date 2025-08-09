from typing import Any
import re

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.prompts import ElementPromptBuilder, ElementPromptContent


class TextInlineFormatter:
    """
    Handles conversion between Markdown inline formatting and Notion rich text elements.

    Supports various formatting options:
    - Bold: **text**
    - Italic: *text* or _text_
    - Underline: __text__
    - Strikethrough: ~~text~~
    - Code: `text`
    - Links: [text](url)
    - Mentions: @[<uuid>]
    """

    FORMAT_PATTERNS = [
        (r"\*\*(.+?)\*\*", {"bold": True}),
        (r"\*(.+?)\*", {"italic": True}),
        (r"_(.+?)_", {"italic": True}),
        (r"__(.+?)__", {"underline": True}),
        (r"~~(.+?)~~", {"strikethrough": True}),
        (r"`(.+?)`", {"code": True}),
        (r"\[(.+?)\]\((.+?)\)", {"link": True}),
        (r"@\[([0-9a-f-]+)\]", {"mention": True}),
    ]

    @classmethod
    def parse_inline_formatting(cls, text: str) -> list[RichTextObject]:
        """
        Parse inline text formatting into a list of RichTextObjects.
        """
        if not text:
            return []
        return cls._split_text_into_segments(text, cls.FORMAT_PATTERNS)

    @classmethod
    def _split_text_into_segments(
        cls, text: str, format_patterns: list[tuple[str, dict[str, Any]]]
    ) -> list[RichTextObject]:
        """
        Split text into segments by formatting markers and convert to RichTextObjects.
        """
        segments: list[RichTextObject] = []
        remaining = text

        while remaining:
            # Finde das erste vorkommende Format-Match
            earliest_match, earliest_format, earliest_pos = None, None, len(remaining)
            for pattern, formatting in format_patterns:
                match = re.search(pattern, remaining)
                if match and match.start() < earliest_pos:
                    earliest_match, earliest_format = match, formatting
                    earliest_pos = match.start()

            # Kein weiteres Format gefunden → Rest als Plaintext
            if not earliest_match:
                segments.append(cls._create_text_element(remaining, {}))
                break

            # Text vor dem Match als Plaintext-Element hinzufügen
            if earliest_pos > 0:
                segments.append(cls._create_text_element(remaining[:earliest_pos], {}))

            # Das Match selbst verarbeiten
            if "link" in earliest_format:
                segments.append(
                    cls._create_link_element(
                        earliest_match.group(1), earliest_match.group(2)
                    )
                )
            elif "mention" in earliest_format:
                segments.append(cls._create_mention_element(earliest_match.group(1)))
            else:
                segments.append(
                    cls._create_text_element(
                        earliest_match.group(1), earliest_format
                    )
                )

            # Reststring verkürzen
            remaining = remaining[earliest_pos + len(earliest_match.group(0)) :]

        return segments

    @classmethod
    def _create_text_element(
        cls, text: str, formatting: dict[str, Any]
    ) -> RichTextObject:
        """Create a plain text RichTextObject with optional formatting."""
        return RichTextObject.from_plain_text(text, **formatting)

    @classmethod
    def _create_link_element(cls, text: str, url: str) -> RichTextObject:
        """Create a RichTextObject representing a hyperlink."""
        return RichTextObject.from_plain_text(text, link={"url": url})

    @classmethod
    def _create_mention_element(cls, id: str) -> RichTextObject:
        """Create a RichTextObject representing a page mention."""
        return RichTextObject(
            type="mention",
            mention={"type": "page", "page": {"id": id}},
            annotations=None,
            plain_text="",  # Notion setzt das selbst
        )

    @classmethod
    def extract_text_with_formatting(cls, rich_text: list[RichTextObject]) -> str:
        """
        Convert a list of RichTextObjects back into Markdown.
        """
        formatted_parts: list[str] = []

        for obj in rich_text:
            content = obj.plain_text or obj.text.content

            ann = obj.annotations.model_dump() if obj.annotations else {}
            if ann.get("code"):
                content = f"`{content}`"
            if ann.get("strikethrough"):
                content = f"~~{content}~~"
            if ann.get("underline"):
                content = f"__{content}__"
            if ann.get("italic"):
                content = f"*{content}*"
            if ann.get("bold"):
                content = f"**{content}**"

            if getattr(obj.text, "link", None):
                url = obj.text.link.url
                content = f"[{content}]({url})"

            formatted_parts.append(content)

        return "".join(formatted_parts)

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Inline formatting can be used within most block types to style your text. You can combine multiple formatting options."
            )
            .with_usage_guidelines(
                "Use inline formatting to highlight important words, provide emphasis, show code or paths, or add hyperlinks."
            )
            .with_syntax(
                "**bold**, *italic*, `code`, ~~strikethrough~~, __underline__, [text](url)"
            )
            .with_examples(
                [
                    "This text has a **bold** word.",
                    "This text has an *italic* word.",
                    "This text has `code` formatting.",
                    "This text has ~~strikethrough~~ formatting.",
                    "This text has __underlined__ formatting.",
                    "This has a [hyperlink](https://example.com).",
                    "You can **combine *different* formatting** styles.",
                ]
            )
            .build()
        )
