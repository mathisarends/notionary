import re
from typing import Dict, Any, Optional, List

from notionary.blocks import NotionBlockElement
from notionary.blocks import (
    ElementPromptContent,
    ElementPromptBuilder,
)
from notionary.blocks.shared.models import Block, ParagraphBlock, RichTextObject


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
    def match_notion(cls, block: Block) -> bool:
        """Check if block contains a mention."""
        supported_block_types = [
            "paragraph",
            "heading_1",
            "heading_2",
            "heading_3",
            "bulleted_list_item",
            "numbered_list_item",
        ]

        if block.type not in supported_block_types:
            return False

        # Get the block content based on block type
        block_content = block.get_block_content()
        if not block_content:
            return False

        rich_text = getattr(block_content, "rich_text", [])
        if not rich_text:
            return False

        for text_item in rich_text:
            if getattr(text_item, "type", None) == "mention" or (
                isinstance(text_item, dict) and text_item.get("type") == "mention"
            ):
                return True

        return False

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown text with mentions to a Notion ParagraphBlock."""
        # Only convert if this element matches the markdown
        if not cls.match_markdown(text):
            return None

        # Process the markdown to produce rich_text items including mentions
        rich_text = cls._process_markdown_with_mentions(text)

        # Return a typed ParagraphBlock
        return ParagraphBlock(rich_text=rich_text, color="default")

    @classmethod
    def _process_markdown_with_mentions(cls, text: str) -> list[dict[str, Any]]:
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
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Extract mentions from Notion block and convert to markdown format."""
        if not block.type:
            return None

        block_content = block.get_block_content()
        if not block_content:
            return None

        rich_text = getattr(block_content, "rich_text", [])
        if not rich_text:
            return None

        processed_text = MentionElement._process_rich_text_with_mentions(rich_text)

        if processed_text:
            return processed_text

        return None

    @classmethod
    def _process_rich_text_with_mentions(cls, rich_text: List[RichTextObject]) -> str:
        """Convert rich text with mentions to markdown string."""
        result = []

        for item in rich_text:
            # Handle RichTextObject (Pydantic model)
            if hasattr(item, "type") and item.type == "mention":
                # For mention objects, we need to access the mention data
                if hasattr(item, "mention"):
                    mention = item.mention
                    mention_type = getattr(mention, "type", None)

                    if mention_type == "page" and hasattr(mention, "page"):
                        result.append(f"@[{mention.page.id}]")
                    elif mention_type == "date" and hasattr(mention, "date"):
                        result.append(f"@date[{mention.date.start}]")
                    elif mention_type == "database" and hasattr(mention, "database"):
                        result.append(f"@db[{mention.database.id}]")
                    else:
                        result.append(item.plain_text or "@[unknown]")
                else:
                    result.append(item.plain_text or "@[unknown]")
            else:
                # Handle regular text items
                result.append(item.plain_text or "")

        return "".join(result)

    @classmethod
    def _process_rich_text_with_mentions_fallback(
        cls, rich_text: List[Dict[str, Any]]
    ) -> str:
        """Fallback method for dict-based rich text (backward compatibility)."""
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
        return (
            ElementPromptBuilder()
            .with_description(
                "References to Notion pages, databases, or dates within text content."
            )
            .with_usage_guidelines(
                "When you want to link to other Notion content within your text."
            )
            .with_syntax("@[page-id]")
            .with_examples(
                [
                    "Check the meeting notes at @[1a6389d5-7bd3-80c5-9a87-e90b034989d0]",
                    "Deadline is @date[2023-12-31]",
                    "Use the structure in @db[1a6389d5-7bd3-80e9-b199-000cfb3fa0b3]",
                ]
            )
            .build()
        )
