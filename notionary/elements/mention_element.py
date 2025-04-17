from typing import Dict, Any, Optional, List
from typing_extensions import override

from notionary.elements.notion_block_element import NotionBlockElement

class MentionElement(NotionBlockElement):
    """
    Handles conversion between Markdown mentions and Notion mention elements.
    
    Markdown mention syntax:
    - @[page-id] - Mention a page by its ID
    
    Note: This element primarily supports Notion-to-Markdown conversion,
    as page mentions in Markdown would typically require knowing internal page IDs.
    """
    
    @override
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown mention."""
        return False
    
    @override
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block contains a mention."""
        if block.get("type") not in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item"]:
            return False
            
        block_content = block.get(block.get("type"), {})
        rich_text = block_content.get("rich_text", [])
        
        for text_item in rich_text:
            if text_item.get("type") == "mention":
                return True
                
        return False
    
    @override
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown mention to Notion mention block."""
        # This would be handled within rich text processing rather than as a standalone block
        return None
    
    @override
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Extract mentions from Notion block and convert to markdown format."""
        block_type = block.get("type")
        if not block_type or block_type not in block:
            return None
            
        block_content = block.get(block_type, {})
        rich_text = block_content.get("rich_text", [])
        
        processed_text = MentionElement._process_rich_text_with_mentions(rich_text)
        
        if MentionElement._is_only_mentions(rich_text):
            return processed_text
            
        return None
    
    @staticmethod
    def _process_rich_text_with_mentions(rich_text: List[Dict[str, Any]]) -> str:
        """Process rich text array and convert any mentions to markdown format."""
        result = []
        
        for item in rich_text:
            if item.get("type") == "mention":
                mention = item.get("mention", {})
                mention_type = mention.get("type")
                
                if mention_type == "page":
                    page_id = mention.get("page", {}).get("id", "")
                    result.append(f"@[{page_id}]")
                elif mention_type == "user":
                    user_id = mention.get("user", {}).get("id", "")
                    result.append(f"@user[{user_id}]")
                elif mention_type == "date":
                    date_value = mention.get("date", {}).get("start", "")
                    result.append(f"@date[{date_value}]")
                elif mention_type == "database":
                    db_id = mention.get("database", {}).get("id", "")
                    result.append(f"@db[{db_id}]")
                else:
                    # Unknown mention type, fallback to plain text if available
                    result.append(item.get("plain_text", "@[unknown]"))
            else:
                # Regular text item
                result.append(item.get("plain_text", ""))
                
        return "".join(result)
    
    @staticmethod
    def _is_only_mentions(rich_text: List[Dict[str, Any]]) -> bool:
        """Check if rich_text array contains only mentions."""
        if not rich_text:
            return False
            
        for item in rich_text:
            if item.get("type") != "mention":
                return False
                
        return True
    
    @override
    @staticmethod
    def is_multiline() -> bool:
        return False
    
    @classmethod
    def get_llm_prompt_content(cls) -> dict:
        """
        Returns a dictionary with all information needed for LLM prompts about this element.
        """
        return {
            "description": "References to Notion pages, users, databases, or dates within text content.",
            "when_to_use": "Mentions are typically part of rich text content rather than standalone elements. They're used to link to other Notion content or users.",
            "syntax": [
                "@[page-id] - Reference to a Notion page",
                "@user[user-id] - Reference to a Notion user",
                "@date[YYYY-MM-DD] - Reference to a date",
                "@db[database-id] - Reference to a Notion database"
            ],
            "examples": [
                "Check the meeting notes at @[1a6389d5-7bd3-80c5-9a87-e90b034989d0]",
                "Please review this with @user[d3dbbbd7-ec00-4204-94d9-e4a46e4928db]",
                "Deadline is @date[2023-12-31]"
            ],
            "limitations": [
                "Mentions are typically created through Notion's UI rather than direct markdown input",
                "When converting Notion content to markdown, mentions are represented with their internal IDs"
            ]
        }