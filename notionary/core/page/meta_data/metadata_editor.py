import random
from typing import Any, Dict, Optional
from notionary.core.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin


class MetadataEditor(LoggingMixin):
    def __init__(self, page_id: str, client: NotionClient):
        self.page_id = page_id
        self._client = client

    async def set_title(self, title: str) -> Optional[Dict[str, Any]]:
        return await self._client.patch(
            f"pages/{self.page_id}",
            {
                "properties": {
                    "title": {"title": [{"type": "text", "text": {"content": title}}]}
                }
            },
        )

    async def set_icon(
        self, emoji: Optional[str] = None, external_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if emoji:
            icon = {"type": "emoji", "emoji": emoji}
        elif external_url:
            icon = {"type": "external", "external": {"url": external_url}}
        else:
            return None

        return await self._client.patch(f"pages/{self.page_id}", {"icon": icon})

    async def set_cover(self, external_url: str) -> Optional[Dict[str, Any]]:
        return await self._client.patch(
            f"pages/{self.page_id}",
            {"cover": {"type": "external", "external": {"url": external_url}}},
        )
        
    async def set_random_gradient_cover(self) -> Optional[Dict[str, Any]]:
        """
        Sets a random gradient cover from Notion's default gradient covers.
        
        Returns:
            Optional[Dict[str, Any]]: The API response or None if the operation fails
        """
        default_notion_covers = [
            "https://www.notion.so/images/page-cover/gradients_8.png", 
            "https://www.notion.so/images/page-cover/gradients_2.png",
            "https://www.notion.so/images/page-cover/gradients_11.jpg",
            "https://www.notion.so/images/page-cover/gradients_10.jpg",
            "https://www.notion.so/images/page-cover/gradients_5.png",
            "https://www.notion.so/images/page-cover/gradients_3.png"
        ]
        
        random_cover_url = random.choice(default_notion_covers)
        
        return await self.set_cover(random_cover_url)
