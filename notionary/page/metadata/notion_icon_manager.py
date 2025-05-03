from typing import Any, Dict, Optional

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
            Optional[str]: Emoji character or URL if set, None if no icon
        """
        page_data = await self._client.get_page(self.page_id)

        if not page_data:
            return ""

        # Get icon data, default to empty dict if not present or None
        icon_data = page_data.get("icon")

        # If icon is None or not present, return None
        if not icon_data:
            return ""

        icon_type = icon_data.get("type")

        if icon_type == "emoji":
            return icon_data.get("emoji")
        if icon_type == "external":
            return icon_data.get("external", {}).get("url")

        return ""
