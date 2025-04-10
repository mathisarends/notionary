
import random
from typing import Any, Dict, Optional
from notionary.core.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin

class NotionPageCoverManager(LoggingMixin):
    def __init__(self, page_id: str, client: NotionClient):
        self.page_id = page_id
        self._client = client
        
    async def set_cover(self, external_url: str) -> Optional[Dict[str, Any]]:
        """Sets a cover image from an external URL.
        """
        
        return await self._client.patch(
            f"pages/{self.page_id}",
            {"cover": {"type": "external", "external": {"url": external_url}}},
        )
        
    async def set_random_gradient_cover(self) -> Optional[Dict[str, Any]]:
        """ Sets a random gradient cover from Notion's default gradient covers.
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
    
    
    async def get_cover_url(self) -> str:
        """Retrieves the current cover image URL of the page.
        """
        
        page_data = await self._client.get_page(self.page_id)
        
        if not page_data:
            return ""
        
        return page_data.get("cover", {}).get("external", {}).get("url", "")
    