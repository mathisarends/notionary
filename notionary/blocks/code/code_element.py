import re
from typing import Optional, Union

from notionary.blocks.block_models import Block
from notionary.blocks.code.code_models import CodeBlock, CodeLanguage, CreateCodeBlock
from notionary.blocks.notion_block_element import BlockCreateResult, NotionBlockElement
from notionary.blocks.paragraph.paragraph_models import (
    CreateParagraphBlock,
    ParagraphBlock,
)
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.page.formatting.block_position import PositionedBlockList
from notionary.prompts import ElementPromptContent, ElementPromptBuilder


class CodeElement(NotionBlockElement):
    """
    Handles conversion between Markdown code blocks and Notion code blocks.

    Markdown code block syntax:
    ```language
    code content
    ```
    """

    DEFAULT_LANGUAGE = "plain text"

    PATTERN = re.compile(
        r"```(\w*)\n([\s\S]+?)```(?:\n(?:Caption|caption):\s*(.+))?", re.MULTILINE
    )

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text contains a markdown code block."""
        return bool(cls.PATTERN.search(text))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if block is a Notion code block."""
        return block.type == "code"

    @classmethod
    def _create_code_block_from_match(
        cls, language: str, content: str, caption_text: Optional[str] = None
    ) -> list[Union[CreateCodeBlock, CreateParagraphBlock]]:
        """
        Shared logic for creating code blocks from parsed data.
        """
        language = cls._normalize_language(language)

        code_rich = RichTextObject.from_plain_text(content)
        code_block = CodeBlock(rich_text=[code_rich], language=language)

        if caption_text and caption_text.strip():
            cap_rich = RichTextObject.from_plain_text(caption_text.strip())
            code_block.caption = [cap_rich]

        # Create code block
        blocks = [CreateCodeBlock(code=code_block)]

        # Append empty paragraph after code
        empty_paragraph = ParagraphBlock(rich_text=[])
        blocks.append(CreateParagraphBlock(paragraph=empty_paragraph))

        return blocks

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown code block to Notion blocks."""
        match = cls.PATTERN.search(text)
        if not match:
            return None

        # Extract components
        language = (match.group(1) or cls.DEFAULT_LANGUAGE).lower()
        content = match.group(2).rstrip("\n")
        caption_text = match.group(3)

        # Use shared logic
        return cls._create_code_block_from_match(language, content, caption_text)

    @classmethod
    def find_matches(cls, text: str) -> PositionedBlockList:
        """
        Find all code block matches in the text and return them as PositionedBlockList.

        Args:
            text: The text to search in

        Returns:
            PositionedBlockList with code blocks and their positions
        """
        positioned_blocks = PositionedBlockList()

        for match in cls.PATTERN.finditer(text):
            language = (match.group(1) or cls.DEFAULT_LANGUAGE).lower()
            content = match.group(2).rstrip("\n")
            caption_text = match.group(3)

            blocks = cls._create_code_block_from_match(language, content, caption_text)

            for block in blocks:
                positioned_blocks.add(match.start(), match.end(), block)

        return positioned_blocks

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion code block to Markdown."""
        if block.type != "code":
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
    def is_multiline(cls) -> bool:
        return True

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
                "'python', 'json', or 'mermaid'. Useful for displaying code, configurations, command-line "
                "examples, or diagram syntax. Also suitable for explaining or visualizing systems with diagram languages. "
                "Code blocks can include optional captions for better documentation."
            )
            .with_usage_guidelines(
                "Use code blocks when you want to present technical content like code snippets, terminal commands, "
                "JSON structures, or system diagrams. Especially helpful when structure and formatting are essential. "
                "Add captions to provide context, explanations, or titles for your code blocks."
            )
            .with_syntax(
                "```language\ncode content\n```\nCaption: optional caption text\n\n"
                "OR\n\n"
                "```language\ncode content\n```"
            )
            .with_examples(
                [
                    "```python\nprint('Hello, world!')\n```\nCaption: Basic Python greeting example",
                    '```json\n{"name": "Alice", "age": 30}\n```\nCaption: User data structure',
                    "```mermaid\nflowchart TD\n  A --> B\n```\nCaption: Simple flow diagram",
                    '```bash\ngit commit -m "Initial commit"\n```',
                ]
            )
            .with_avoidance_guidelines(
                "NEVER EVER wrap markdown content with ```markdown. Markdown should be written directly without code block formatting. "
                "NEVER use ```markdown under any circumstances. "
                "For Mermaid diagrams, use ONLY the default styling without colors, backgrounds, or custom styling attributes. "
                "Keep Mermaid diagrams simple and minimal without any styling or color modifications. "
                "Captions must appear immediately after the closing ``` on a new line starting with 'Caption:' - "
                "no empty lines between the code block and the caption."
            )
            .build()
        )
