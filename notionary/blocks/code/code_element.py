import re

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.code.code_models import CodeBlock, CodeLanguage, CreateCodeBlock
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.rich_text.rich_text_models import RichText
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


class CodeElement(BaseBlockElement):
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
    CODE_START_WITH_CAPTION_PATTERN = re.compile(r"^```(\w*)\s*(?:\"([^\"]*)\")?\s*$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if block is a Notion code block."""
        return block.type == BlockType.CODE and block.code

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert opening ```language to Notion code block."""
        if not (match := cls.CODE_START_PATTERN.match(text.strip())):
            return None

        language = (match.group(1) or cls.DEFAULT_LANGUAGE).lower()
        language = cls._normalize_language(language)

        # Create empty CodeBlock - content will be added by stack processor
        code_block = CodeBlock(rich_text=[], language=language, caption=[])
        return CreateCodeBlock(code=code_block)

    @classmethod
    def create_from_markdown_block(cls, opening_line: str, code_lines: list[str]) -> BlockCreateResult:
        """
        Create a complete code block from markdown components.
        """
        match = cls.CODE_START_WITH_CAPTION_PATTERN.match(opening_line.strip())
        if not match:
            return None

        language = (match.group(1) or cls.DEFAULT_LANGUAGE).lower()
        language = cls._normalize_language(language)

        caption = match.group(2) if match.group(2) else None

        # Create rich text content from code lines
        rich_text = []
        if code_lines:
            content = "\n".join(code_lines)
            rich_text = [RichText.for_code_block(content)]

        caption_list = []
        if caption:
            caption_list = [RichText.for_caption(caption)]

        code_block = CodeBlock(rich_text=rich_text, language=language, caption=caption_list)

        return CreateCodeBlock(code=code_block)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
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
        result = f"```{language}\n{code_content}\n```" if language else f"```\n{code_content}\n```"

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
    def extract_content(rich_text_list: list[RichText]) -> str:
        """Extract code content from rich_text array."""
        return "".join(rt.plain_text for rt in rich_text_list if rt.plain_text)

    @staticmethod
    def extract_caption(caption_list: list[RichText]) -> str:
        """Extract caption text from caption array."""
        return "".join(rt.plain_text for rt in caption_list if rt.plain_text)

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for code blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Code blocks display syntax-highlighted code with optional language specification and captions",
            syntax_examples=[
                "```\nprint('Hello World')\n```",
                "```python\nprint('Hello World')\n```",
                "```python \"Example code\"\nprint('Hello World')\n```",
                "```javascript\nconsole.log('Hello');\n```",
            ],
            usage_guidelines="Use for displaying code snippets. Language specification enables syntax highlighting. Caption in quotes on first line provides description. Supports many programming languages.",
        )
