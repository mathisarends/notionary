from typing import Optional

from notionary.models.notion_page_response import EmojiIcon, ExternalIcon
from notionary.page.client import NotionPageClient
from notionary.util import LoggingMixin


class NotionPageIconManager(LoggingMixin):
    def __init__(self, page_id: str, client: NotionPageClient):
        self.page_id = page_id
        self._client = client

    async def set_emoji_icon(self, emoji: str) -> Optional[str]:
        """
        Sets the page icon to an emoji.

        Args:
            emoji (str): The emoji character to set as the icon.

        Returns:
            Optional[str]: The emoji that was set as the icon, or None if the operation failed.
        """
        icon = {"type": "emoji", "emoji": emoji}
        page_response = await self._client.patch_page(
            page_id=self.page_id, data={"icon": icon}
        )

        if page_response and page_response.icon and page_response.icon.type == "emoji":
            return page_response.icon.emoji
        return None

    async def set_external_icon(self, external_icon_url: str) -> Optional[str]:
        """
        Sets the page icon to an external image.

        Args:
            url (str): The URL of the external image to set as the icon.

        Returns:
            Optional[str]: The URL of the external image that was set as the icon,
                        or None if the operation failed.
        """
        icon = {"type": "external", "external": {"url": external_icon_url}}
        page_response = await self._client.patch_page(
            page_id=self.page_id, data={"icon": icon}
        )

        if (
            page_response
            and page_response.icon
            and page_response.icon.type == "external"
        ):
            return page_response.icon.external.url
        return None

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
        if isinstance(icon, ExternalIcon):
            return icon.external.url

        return None
