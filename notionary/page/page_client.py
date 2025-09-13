from typing import Any, Optional, Union

from pydantic import BaseModel

from notionary.notion_client import NotionClient
from notionary.blocks.callout.callout_models import EmojiIcon
from notionary.page.page_models import ExternalRessource, NotionPageResponse


class NotionPageClient(NotionClient):
    """
    Client for Notion page-specific operations.
    Inherits base HTTP functionality from NotionClient.
    """

    def __init__(self, page_id: Optional[str] = None, token: Optional[str] = None):
        """Initialize with optional page_id for methods that operate on a specific page."""
        super().__init__(token=token)
        self.page_id = page_id

    async def get_page(self, page_id: str) -> NotionPageResponse:
        """
        Gets metadata for a Notion page by its ID.
        """
        response = await self.get(f"pages/{page_id}")
        return NotionPageResponse.model_validate(response)

    async def create_page(
        self,
        *,
        parent_database_id: Optional[str] = None,
        parent_page_id: Optional[str] = None,
        title: str,
    ) -> NotionPageResponse:
        """
        Creates a new page either in a database or as a child of another page.
        Exactly one of parent_database_id or parent_page_id must be provided.
        Only 'title' is supported here (no icon/cover/children).
        """
        # Exakt einen Parent zulassen
        if (parent_database_id is None) == (parent_page_id is None):
            raise ValueError("Specify exactly one parent: database OR page")

        # Parent bauen
        parent = (
            {"database_id": parent_database_id}
            if parent_database_id
            else {"page_id": parent_page_id}
        )

        properties: dict[str, Any] = {
            "title": {"title": [{"type": "text", "text": {"content": title}}]}
        }

        payload = {"parent": parent, "properties": properties}
        response = await self.post("pages", payload)
        return NotionPageResponse.model_validate(response)

    async def patch_page(
        self, data: Union[dict[str, Any], BaseModel]
    ) -> NotionPageResponse:
        """
        Updates this page with the provided data.
        """
        if isinstance(data, BaseModel):
            data = data.model_dump(exclude_unset=True, exclude_none=True)

        response = await self.patch(f"pages/{self.page_id}", data=data)
        return NotionPageResponse.model_validate(response)

    async def patch_emoji_icon(self, emoji: str) -> NotionPageResponse:
        """
        Updates this page's icon to an emoji.
        """
        emoji_icon = EmojiIcon(emoji=emoji)
        data = {"icon": emoji_icon.model_dump()}
        response = await self.patch(f"pages/{self.page_id}", data=data)
        return NotionPageResponse.model_validate(response)

    async def patch_external_icon(self, icon_url: str) -> NotionPageResponse:
        """
        Updates this page's icon to an external image.
        """
        external_icon = ExternalRessource.from_url(icon_url)
        data = {"icon": external_icon.model_dump()}
        response = await self.patch(f"pages/{self.page_id}", data=data)
        return NotionPageResponse.model_validate(response)

    async def patch_external_cover(self, cover_url: str) -> NotionPageResponse:
        """
        Updates this page's cover to an external image.
        """
        external_cover = ExternalRessource.from_url(cover_url)
        data = {"cover": external_cover.model_dump()}
        response = await self.patch(f"pages/{self.page_id}", data=data)
        return NotionPageResponse.model_validate(response)

    async def remove_icon(self) -> NotionPageResponse:
        """
        Removes the icon from this page.
        """
        data = {"icon": None}
        response = await self.patch(f"pages/{self.page_id}", data=data)
        return NotionPageResponse.model_validate(response)

    async def remove_cover(self) -> NotionPageResponse:
        """
        Removes the cover from this page.
        """
        data = {"cover": None}
        response = await self.patch(f"pages/{self.page_id}", data=data)
        return NotionPageResponse.model_validate(response)

    async def patch_title(self, title: str) -> NotionPageResponse:
        """
        Updates this page's title.
        """
        data = {
            "properties": {
                "title": {"title": [{"type": "text", "text": {"content": title}}]}
            }
        }
        response = await self.patch(f"pages/{self.page_id}", data=data)
        return NotionPageResponse.model_validate(response)

    async def archive_page(self) -> NotionPageResponse:
        """
        Archives this page.
        """
        data = {"archived": True}
        response = await self.patch(f"pages/{self.page_id}", data=data)
        return NotionPageResponse.model_validate(response)

    async def unarchive_page(self) -> NotionPageResponse:
        """
        Unarchives this page.
        """
        data = {"archived": False}
        response = await self.patch(f"pages/{self.page_id}", data=data)
        return NotionPageResponse.model_validate(response)