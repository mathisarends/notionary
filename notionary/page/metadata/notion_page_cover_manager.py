import random
from typing import Any, Dict, Optional
from notionary.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin


class NotionPageCoverManager(LoggingMixin):
    def __init__(self, page_id: str, client: NotionClient):
        self.page_id = page_id
        self._client = client

    async def set_cover(self, external_url: str) -> Optional[str]:
        """
        Sets a cover image from an external URL and returns the new URL if successful.

        Args:
            external_url: The URL to be set as the external cover image.

        Returns:
            The URL of the new cover image, or None if the request failed.
        """
        data = {
            "cover": {
                "type": "external",
                "external": {
                    "url": external_url
                }
            }
        }

        try:
            updated_page = await self._client.patch_page(self.page_id, data=data)
            return updated_page.cover.external.url
        except Exception as e:
            self.logger.error("Failed to set cover image: %s", str(e))
            return None

    async def set_random_gradient_cover(self) -> Optional[Dict[str, Any]]:
        """Sets a random gradient cover from Notion's default gradient covers."""
        default_notion_covers = [
            "https://www.notion.so/images/page-cover/gradients_8.png",
            "https://www.notion.so/images/page-cover/gradients_2.png",
            "https://www.notion.so/images/page-cover/gradients_11.jpg",
            "https://www.notion.so/images/page-cover/gradients_10.jpg",
            "https://www.notion.so/images/page-cover/gradients_5.png",
            "https://www.notion.so/images/page-cover/gradients_3.png",
        ]

        random_cover_url = random.choice(default_notion_covers)

        return await self.set_cover(random_cover_url)

    async def get_cover_url(self) -> str:
        """Retrieves the current cover image URL of the page."""
        page_data = await self._client.get_page(self.page_id)

        if not page_data or not page_data.cover:
            return ""

        if page_data.cover.type == "external":
            return page_data.cover.external.url

        return ""
