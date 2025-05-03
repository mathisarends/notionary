import re
from typing import Dict, Any, Optional, List, Tuple
from notionary.elements.notion_block_element import NotionBlockElement
from notionary.elements.prompts.element_prompt_content import ElementPromptContent


class CodeBlockElement(NotionBlockElement):
    """
    Handles conversion between Markdown code blocks and Notion code blocks.

    Markdown code block syntax:
    ```language
    code content
    ```

    Where:
    - language is optional and specifies the programming language
    - code content is the code to be displayed
    """

    PATTERN = re.compile(r"```(\w*)\n([\s\S]+?)```", re.MULTILINE)

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text contains a markdown code block."""
        return bool(CodeBlockElement.PATTERN.search(text))

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion code block."""
        return block.get("type") == "code"

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown code block to Notion code block."""
        match = CodeBlockElement.PATTERN.search(text)
        if not match:
            return None

        language = match.group(1) or "plain text"
        content = match.group(2)

        if content.endswith("\n"):
            content = content[:-1]

        return {
            "type": "code",
            "code": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": content},
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default",
                        },
                        "plain_text": content,
                    }
                ],
                "language": language,
            },
        }

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion code block to markdown code block."""
        if block.get("type") != "code":
            return None

        code_data = block.get("code", {})
        rich_text = code_data.get("rich_text", [])

        # Extract the code content
        content = ""
        for text_block in rich_text:
            content += text_block.get("plain_text", "")

        language = code_data.get("language", "")

        # Format as a markdown code block
        return f"```{language}\n{content}\n```"

    @classmethod
    def find_matches(cls, text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Find all code block matches in the text and return their positions.

        Args:
            text: The text to search in

        Returns:
            List of tuples with (start_pos, end_pos, block)
        """
        matches = []
        for match in CodeBlockElement.PATTERN.finditer(text):
            language = match.group(1) or "plain text"
            content = match.group(2)

            # Remove trailing newline if present
            if content.endswith("\n"):
                content = content[:-1]

            block = {
                "type": "code",
                "code": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": content},
                            "annotations": {
                                "bold": False,
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                                "code": False,
                                "color": "default",
                            },
                            "plain_text": content,
                        }
                    ],
                    "language": language,
                },
            }

            matches.append((match.start(), match.end(), block))

        return matches

    @classmethod
    def is_multiline(cls) -> bool:
        return True

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the code block element.
        """
        return {
            "description": (
                "Use fenced code blocks to format content as code. Supports language annotations like "
                "'python', 'json', or 'mermaid'. Useful for displaying code, configurations, command-line "
                "examples, or diagram syntax. Also suitable for explaining or visualizing systems with diagram languages."
            ),
            "when_to_use": (
                "Use code blocks when you want to present technical content like code snippets, terminal commands, "
                "JSON structures, or system diagrams. Especially helpful when structure and formatting are essential."
            ),
            "syntax": "```language\ncode content\n```",
            "examples": [
                "```python\nprint('Hello, world!')\n```",
                '```json\n{"name": "Alice", "age": 30}\n```',
                "```mermaid\nflowchart TD\n  A --> B\n```",
            ],
            "avoid": (
                "NEVER EVER wrap markdown content with ```markdown. Markdown should be written directly without code block formatting. "
                "NEVER use ```markdown under any circumstances. "
                "For Mermaid diagrams, use ONLY the default styling without colors, backgrounds, or custom styling attributes. "
                "Keep Mermaid diagrams simple and minimal without any styling or color modifications."
            ),
        }
