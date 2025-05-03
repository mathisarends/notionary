import re
from typing import Dict, Any, Optional, List
from typing_extensions import override

from notionary.elements.notion_block_element import NotionBlockElement
from notionary.elements.prompts.element_prompt_content import ElementPromptContent


class MentionElement(NotionBlockElement):
    """
    Handles conversion between Markdown mentions and Notion mention elements.

    Markdown mention syntax:
    - @[page-id] - Mention a page by its ID
    - @date[YYYY-MM-DD] - Mention a date
    - @db[database-id] - Mention a database by its ID
    """

    MENTION_TYPES = {
        "page": {
            "pattern": r"@\[([0-9a-f-]+)\]",
            "create_mention": lambda id_value: {
                "type": "mention",
                "mention": {"type": "page", "page": {"id": id_value}},
            },
            "get_plain_text": lambda mention: f"Page {mention['mention']['page']['id']}",
            "to_markdown": lambda mention: f"@[{mention['mention']['page']['id']}]",
        },
        "date": {
            "pattern": r"@date\[(\d{4}-\d{2}-\d{2})\]",
            "create_mention": lambda date_value: {
                "type": "mention",
                "mention": {"type": "date", "date": {"start": date_value, "end": None}},
            },
            "get_plain_text": lambda mention: mention["mention"]["date"]["start"],
            "to_markdown": lambda mention: f"@date[{mention['mention']['date']['start']}]",
        },
        "database": {
            "pattern": r"@db\[([0-9a-f-]+)\]",
            "create_mention": lambda db_id: {
                "type": "mention",
                "mention": {"type": "database", "database": {"id": db_id}},
            },
            "get_plain_text": lambda mention: f"Database {mention['mention']['database']['id']}",
            "to_markdown": lambda mention: f"@db[{mention['mention']['database']['id']}]",
        },
    }

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text contains a markdown mention."""
        for mention_type in MentionElement.MENTION_TYPES.values():
            if re.search(mention_type["pattern"], text):
                return True
        return False

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block contains a mention."""
        supported_block_types = [
            "paragraph",
            "heading_1",
            "heading_2",
            "heading_3",
            "bulleted_list_item",
            "numbered_list_item",
        ]

        if block.get("type") not in supported_block_types:
            return False

        block_content = block.get(block.get("type"), {})
        rich_text = block_content.get("rich_text", [])

        return any(text_item.get("type") == "mention" for text_item in rich_text)

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown text with mentions to a Notion paragraph block."""
        if not MentionElement.match_markdown(text):
            return None

        rich_text = MentionElement._process_markdown_with_mentions(text)

        return {
            "type": "paragraph",
            "paragraph": {"rich_text": rich_text, "color": "default"},
        }

    @classmethod
    def _process_markdown_with_mentions(cls, text: str) -> List[Dict[str, Any]]:
        """Convert markdown mentions to Notion rich_text format."""
        mentions = []

        for mention_type, config in MentionElement.MENTION_TYPES.items():
            for match in re.finditer(config["pattern"], text):
                mentions.append(
                    {
                        "start": match.start(),
                        "end": match.end(),
                        "type": mention_type,
                        "value": match.group(1),
                        "original": match.group(0),
                    }
                )

        mentions.sort(key=lambda m: m["start"])

        # Build rich_text list
        rich_text = []
        position = 0

        for mention in mentions:
            if mention["start"] > position:
                rich_text.append(
                    MentionElement._create_text_item(text[position : mention["start"]])
                )

            # Add the mention
            mention_obj = MentionElement.MENTION_TYPES[mention["type"]][
                "create_mention"
            ](mention["value"])

            # Add annotations and plain text
            mention_obj["annotations"] = MentionElement._default_annotations()
            mention_obj["plain_text"] = MentionElement.MENTION_TYPES[mention["type"]][
                "get_plain_text"
            ](mention_obj)

            rich_text.append(mention_obj)
            position = mention["end"]

        # Add remaining text if any
        if position < len(text):
            rich_text.append(MentionElement._create_text_item(text[position:]))

        return rich_text

    @classmethod
    def _create_text_item(cls, content: str) -> Dict[str, Any]:
        """Create a text item with default annotations."""
        text_item = {
            "type": "text",
            "text": {"content": content, "link": None},
            "annotations": MentionElement._default_annotations(),
            "plain_text": content,
        }
        return text_item

    @classmethod
    def _default_annotations(cls) -> Dict[str, Any]:
        """Return default annotations for rich text."""
        return {
            "bold": False,
            "italic": False,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": "default",
        }

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Extract mentions from Notion block and convert to markdown format."""
        block_type = block.get("type")
        if not block_type or block_type not in block:
            return None

        block_content = block.get(block_type, {})
        rich_text = block_content.get("rich_text", [])

        processed_text = MentionElement._process_rich_text_with_mentions(rich_text)

        if processed_text:
            return processed_text

        return None

    @classmethod
    def _process_rich_text_with_mentions(cls, rich_text: List[Dict[str, Any]]) -> str:
        """Convert rich text with mentions to markdown string."""
        result = []

        for item in rich_text:
            if item.get("type") == "mention":
                mention = item.get("mention", {})
                mention_type = mention.get("type")

                if mention_type in MentionElement.MENTION_TYPES:
                    result.append(
                        MentionElement.MENTION_TYPES[mention_type]["to_markdown"](item)
                    )
                else:
                    result.append(item.get("plain_text", "@[unknown]"))
            else:
                result.append(item.get("plain_text", ""))

        return "".join(result)

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the mention element.
        """
        return {
            "description": "References to Notion pages, databases, or dates within text content.",
            "when_to_use": "When you want to link to other Notion content within your text.",
            "syntax": "@[page-id]",
            "examples": [
                "Check the meeting notes at @[1a6389d5-7bd3-80c5-9a87-e90b034989d0]",
                "Deadline is @date[2023-12-31]",
                "Use the structure in @db[1a6389d5-7bd3-80e9-b199-000cfb3fa0b3]",
            ],
        }
