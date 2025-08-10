from __future__ import annotations
import re
from typing import Optional

from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.block_models import Block, BlockType
from notionary.blocks.code.code_models import CodeBlock, CodeLanguage, CreateCodeBlock
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.prompts import ElementPromptContent, ElementPromptBuilder


class CodeElement(NotionBlockElement):
    """
    Handles conversion between Markdown code blocks and Notion code blocks.
    Now integrated into the LineProcessor stack system.

    Markdown code block syntax:
    ```language
    [code content as child lines]
    ```
    """

    DEFAULT_LANGUAGE = "plain text"
    CODE_START_PATTERN = re.compile(r"^```(\w*)\s*$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text starts a code block."""
        return bool(cls.CODE_START_PATTERN.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if block is a Notion code block."""
        return block.type == BlockType.CODE and block.code

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert opening ```language to Notion code block."""
        match = cls.CODE_START_PATTERN.match(text.strip())
        if not match:
            return None

        language = (match.group(1) or cls.DEFAULT_LANGUAGE).lower()
        language = cls._normalize_language(language)

        # Create empty CodeBlock - content will be added by stack processor
        code_block = CodeBlock(rich_text=[], language=language, caption=[])
        return CreateCodeBlock(code=code_block)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion code block to Markdown."""
        if block.type != BlockType.CODE:
            return None

        if not block.code:
            return None

        language_enum = block.code.language
        rich_text = block.code.rich_text or []
        caption = block.code.caption or []

        code_content = cls.extract_content(rich_text)
        caption_text = cls.extract_caption(caption)

        # Convert enum to string value
        language = language_enum.value if language_enum else ""

        # Handle language - convert "plain text" back to empty string for markdown
        if language == cls.DEFAULT_LANGUAGE:
            language = ""

        # Build markdown code block
        if language:
            result = f"```{language}\n{code_content}\n```"
        else:
            result = f"```\n{code_content}\n```"

        # Add caption if present
        if caption_text:
            result += f"\nCaption: {caption_text}"

        return result

    @classmethod
    def _normalize_language(cls, language: str) -> CodeLanguage:
        """
        Normalize the language string to a valid CodeLanguage enum or default.
        """
        # Try to find matching enum by value
        for lang_enum in CodeLanguage:
            if lang_enum.value.lower() == language.lower():
                return lang_enum

        # Return default if not found
        return CodeLanguage.PLAIN_TEXT

    @staticmethod
    def extract_content(rich_text_list: list[RichTextObject]) -> str:
        """Extract code content from rich_text array."""
        return "".join(rt.plain_text for rt in rich_text_list if rt.plain_text)

    @staticmethod
    def extract_caption(caption_list: list[RichTextObject]) -> str:
        """Extract caption text from caption array."""
        return "".join(rt.plain_text for rt in caption_list if rt.plain_text)