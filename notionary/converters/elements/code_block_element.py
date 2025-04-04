from typing import Dict, Any, Optional, List, Tuple
from typing_extensions import override
import re
from notionary.converters.notion_block_element import NotionBlockElement

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
        Includes description, usage guidance, syntax options, and examples.
        """
        return {
            "description": "Creates a code block that displays formatted code with syntax highlighting.",
            "when_to_use": "Use code blocks when you need to include programming code, commands, configuration files, or any content that benefits from monospace formatting and syntax highlighting.",
            "syntax": [
                "```\ncode content\n``` - Code block without language specification (plain text)",
                "```language\ncode content\n``` - Code block with language specification for syntax highlighting"
            ],
            "examples": [
                "```python\ndef hello_world():\n    print('Hello, world!')\n\nhello_world()\n```",
                "```javascript\nconst greeting = 'Hello, world!';\nconsole.log(greeting);\n```",
                "```css\n.container {\n    display: flex;\n    justify-content: center;\n    align-items: center;\n}\n```",
                "```\nThis is plain text in a code block\nwithout any syntax highlighting\n```"
            ]
        }