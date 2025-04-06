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
