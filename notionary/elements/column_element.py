import re
from typing import Dict, Any, Optional, List, Tuple
from notionary.elements.notion_block_element import NotionBlockElement
from notionary.prompting.element_prompt_content import (
    ElementPromptBuilder,
    ElementPromptContent,
)


# Fix Column Element
class ColumnsElement(NotionBlockElement):
    """
    Handles conversion between Markdown column syntax and Notion column_list blocks.

    Note: Due to Notion's column structure, this element requires special handling.
    It returns a column_list block with placeholder content, as the actual columns
    must be added as children after the column_list is created.
    """

    PATTERN = re.compile(
        r"^::: columns\n((?:::: column\n(?:.*?\n)*?:::\n?)+):::\s*$",
        re.MULTILINE | re.DOTALL,
    )

    COLUMN_PATTERN = re.compile(r"::: column\n(.*?):::", re.DOTALL)

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text contains a columns block."""
        return bool(cls.PATTERN.search(text))

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion column_list block."""
        return block.get("type") == "column_list"

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown columns to Notion column_list block."""
        match = cls.PATTERN.search(text)
        if not match:
            return None

        columns_content = match.group(1)
        column_matches = cls.COLUMN_PATTERN.findall(columns_content)

        if not column_matches:
            return None

        return {"type": "column_list", "column_list": {}}

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion column_list block to markdown columns."""
        if block.get("type") != "column_list":
            return None

        # In a real implementation, you'd need to fetch the child column blocks
        # This is a placeholder showing the expected output format
        markdown = "::: columns\n"

        # Placeholder for column content extraction
        # In reality, you'd iterate through the child blocks
        markdown += "::: column\nColumn content here\n:::\n"

        markdown += ":::"
        return markdown

    @classmethod
    def find_matches(cls, text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Find all column block matches in the text and return their positions.

        Args:
            text: The text to search in

        Returns:
            List of tuples with (start_pos, end_pos, block_data)
        """
        matches = []
        for match in cls.PATTERN.finditer(text):
            block_data = cls.markdown_to_notion(match.group(0))
            if block_data:
                matches.append((match.start(), match.end(), block_data))

        return matches

    @classmethod
    def is_multiline(cls) -> bool:
        return True

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the columns element.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Create multi-column layouts using Pandoc-style fenced divs. Perfect for side-by-side comparisons, "
                "parallel content, or creating newsletter-style layouts. Each column can contain any markdown content "
                "including headers, lists, images, and even nested blocks."
            )
            .with_usage_guidelines(
                "Use columns when you need to present information side-by-side for comparison, create visual balance "
                "in your layout, or organize related content in parallel. Great for pros/cons lists, before/after "
                "comparisons, or displaying multiple related items. Keep column content balanced in length for best "
                "visual results."
            )
            .with_syntax(
                "::: columns\n"
                "::: column\n"
                "Content for first column\n"
                ":::\n"
                "::: column\n"
                "Content for second column\n"
                ":::\n"
                ":::"
            )
            .with_examples(
                [
                    # Simple two-column example
                    "::: columns\n"
                    "::: column\n"
                    "### Pros\n"
                    "- Fast performance\n"
                    "- Easy to use\n"
                    "- Great documentation\n"
                    ":::\n"
                    "::: column\n"
                    "### Cons\n"
                    "- Limited customization\n"
                    "- Requires subscription\n"
                    "- No offline mode\n"
                    ":::\n"
                    ":::",
                    # Three-column example
                    "::: columns\n"
                    "::: column\n"
                    "**Python**\n"
                    "```python\n"
                    "print('Hello')\n"
                    "```\n"
                    ":::\n"
                    "::: column\n"
                    "**JavaScript**\n"
                    "```javascript\n"
                    "console.log('Hello');\n"
                    "```\n"
                    ":::\n"
                    "::: column\n"
                    "**Ruby**\n"
                    "```ruby\n"
                    "puts 'Hello'\n"
                    "```\n"
                    ":::\n"
                    ":::",
                    # Mixed content example
                    "::: columns\n"
                    "::: column\n"
                    "![Image](url)\n"
                    "Product photo\n"
                    ":::\n"
                    "::: column\n"
                    "## Product Details\n"
                    "- Price: $99\n"
                    "- Weight: 2kg\n"
                    "- Color: Blue\n"
                    "\n"
                    "[Order Now](link)\n"
                    ":::\n"
                    ":::",
                ]
            )
            .with_avoidance_guidelines(
                "Avoid nesting column blocks within column blocks - this creates confusing layouts. "
                "Don't use columns for content that should be read sequentially. Keep the number of columns "
                "reasonable (2-4 max) for readability. Ensure each ::: marker is on its own line with proper "
                "nesting. Don't mix column syntax with regular markdown formatting on the same line."
            )
            .build()
        )

    @classmethod
    def get_column_content(cls, text: str) -> List[str]:
        """
        Extract the content of individual columns from the markdown.
        This is a helper method that can be used by the implementation
        to process column content separately.

        Args:
            text: The complete columns markdown block

        Returns:
            List of column content strings
        """
        match = cls.PATTERN.search(text)
        if not match:
            return []

        columns_content = match.group(1)
        return [
            content.strip() for content in cls.COLUMN_PATTERN.findall(columns_content)
        ]
