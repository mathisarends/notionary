from typing import Dict, Any, Optional, List, Tuple
from typing_extensions import override
import re
from notionary.core.converters.elements.notion_block_element import NotionBlockElement

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
    
    PATTERN = re.compile(r'```(\w*)\n([\s\S]+?)```', re.MULTILINE)
    
    @override
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text contains a markdown code block."""
        return bool(CodeBlockElement.PATTERN.search(text))
    
    @override
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion code block."""
        return block.get("type") == "code"
    
    @override
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown code block to Notion code block."""
        match = CodeBlockElement.PATTERN.search(text)
        if not match:
            return None
            
        language = match.group(1) or "plain text"
        content = match.group(2)
        
        if content.endswith('\n'):
            content = content[:-1]
            
        return {
            "type": "code",
            "code": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": content
                        },
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default"
                        },
                        "plain_text": content
                    }
                ],
                "language": language
            }
        }
    
    @override
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
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
    
    @staticmethod
    def find_matches(text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
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
            if content.endswith('\n'):
                content = content[:-1]
                
            block = {
                "type": "code",
                "code": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content
                            },
                            "annotations": {
                                "bold": False,
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                                "code": False,
                                "color": "default"
                            },
                            "plain_text": content
                        }
                    ],
                    "language": language
                }
            }
            
            matches.append((match.start(), match.end(), block))
            
        return matches
    
    @override
    @staticmethod
    def is_multiline() -> bool:
        return True
    
    @classmethod
    def get_llm_prompt_content(cls) -> dict:
        """
        Returns a dictionary with all information needed for LLM prompts about this element.
        """
        return {
            "description": "Use fenced code blocks to format content as code. Supports language annotations like 'python', 'json', or 'mermaid'. Use when you want to display code, configurations, command-line examples, or diagram syntax. Also useful when breaking down or visualizing a system or architecture for complex problems (e.g. using mermaid).",
            "examples": [
                "```python\nprint('Hello, world!')\n```",
                "```mermaid\nflowchart TD\n  A --> B\n```"
            ]
        }