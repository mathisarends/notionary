import json
from typing import Any, Dict, Optional

from notionary.models.notion_page_response import EmojiIcon, ExternalIcon, FileIcon
from notionary.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin


class NotionPageIconManager(LoggingMixin):
    def __init__(self, page_id: str, client: NotionClient):
        self.page_id = page_id
        self._client = client

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

    async def get_icon(self) -> Optional[str]:
        """
        Retrieves the page icon - either emoji or external URL.

        Returns:
            Optional[str]: Emoji character or URL if set, None if no icon.
        """
        page_response = await self._client.get_page(self.page_id)
        if not page_response or not page_response.icon:
            return None

        icon = page_response.icon

        if isinstance(icon, EmojiIcon):
            return icon.emoji
        elif isinstance(icon, ExternalIcon):
            return icon.external.url
        elif isinstance(icon, FileIcon):
            return icon.file.url

        return None
