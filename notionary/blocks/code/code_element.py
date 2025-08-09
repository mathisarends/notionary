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

        language = block.code.language or ""
        rich_text = block.code.rich_text or []
        caption = block.code.caption or []

        code_content = cls.extract_content(rich_text)
        caption_text = cls.extract_caption(caption)

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
    def _normalize_language(cls, language: str) -> str:
        """
        Normalize the language string to a valid CodeLanguage value or default.
        """
        valid_languages = [lang.value.lower() for lang in CodeLanguage]
        if language not in valid_languages:
            return cls.DEFAULT_LANGUAGE
        return language

    @staticmethod
    def extract_content(rich_text_list: list[RichTextObject]) -> str:
        """Extract code content from rich_text array."""
        return "".join(rt.plain_text for rt in rich_text_list if rt.plain_text)

    @staticmethod
    def extract_caption(caption_list: list[RichTextObject]) -> str:
        """Extract caption text from caption array."""
        return "".join(rt.plain_text for rt in caption_list if rt.plain_text)

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the code block element.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Use fenced code blocks to format content as code. Supports language annotations like "
                "'python', 'json', or 'mermaid'. Code blocks now work within columns and tables using the | prefix system."
            )
            .with_usage_guidelines(
                "Use code blocks when you want to present technical content like code snippets, terminal commands, "
                "JSON structures, or system diagrams. Can be embedded in columns, tables, and other parent elements."
            )
            .with_syntax(
                "```language\n| code line 1\n| code line 2\n```\nCaption: optional caption\n\n"
                "OR for standalone:\n\n"
                "```language\ncode content\n```"
            )
            .with_examples(
                [
                    "```python\n| print('Hello, world!')\n| return 42\n```",
                    '```json\n| {\n|   "name": "Alice",\n|   "age": 30\n| }\n```',
                ]
            )
            .build()
        )
