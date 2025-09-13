from typing import Any, Optional, Union

from pydantic import BaseModel

from notionary.notion_client import NotionClient
from notionary.page.page_models import NotionPageDto
from notionary.shared.models.cover_models import UpdateCoverDto
from notionary.shared.models.icon_models import UpdateIconDto


class NotionPageClient(NotionClient):
    """
    Client for Notion page-specific operations.
    Inherits base HTTP functionality from NotionClient.
    """

    def __init__(self, page_id: Optional[str] = None, token: Optional[str] = None):
        """Initialize with optional page_id for methods that operate on a specific page."""
        super().__init__(token=token)
        self.page_id = page_id

    async def get_page(self, page_id: str) -> NotionPageDto:
        """
        Gets metadata for a Notion page by its ID.
        """
        response = await self.get(f"pages/{page_id}")
        return NotionPageDto.model_validate(response)

    async def create_page(
        self,
        *,
        parent_database_id: Optional[str] = None,
        parent_page_id: Optional[str] = None,
        title: str,
    ) -> NotionPageDto:
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
        return NotionPageDto.model_validate(response)

    async def patch_page(
        self, data: Union[dict[str, Any], BaseModel]
    ) -> NotionPageDto:
        """
        Updates this page with the provided data.
        """
        if isinstance(data, BaseModel):
            data = data.model_dump(exclude_unset=True, exclude_none=True)

        response = await self.patch(f"pages/{self.page_id}", data=data)
        return NotionPageDto.model_validate(response)

    async def patch_emoji_icon(self, emoji: str) -> NotionPageDto:
        """
        Updates this page's icon to an emoji.
        """
        update_emoji_icon_dto = UpdateIconDto.from_emoji(emoji)
        return await self.patch_page(update_emoji_icon_dto)

    async def remove_icon(self) -> NotionPageDto:
        """
        Removes the icon from this page.
        """
        update_icon_dto = UpdateIconDto(icon=None)
        return await self.patch_page(update_icon_dto)

    async def patch_external_icon(self, icon_url: str) -> NotionPageDto:
        """
        Updates this page's icon to an external image.
        """
        update_external_icon_dto = UpdateIconDto.from_url(icon_url)
        return await self.patch_page(update_external_icon_dto)

    async def patch_external_cover(self, cover_url: str) -> NotionPageDto:
        """
        Updates this page's cover to an external image.
        """
        update_external_cover_dto = UpdateCoverDto.from_url(cover_url)
        return await self.patch_page(update_external_cover_dto)

    async def remove_cover(self) -> NotionPageDto:
        """
        Removes the cover from this page.
        """
        update_external_cover_dto = UpdateCoverDto(cover=None)
        return await self.patch_page(update_external_cover_dto)

    async def patch_title(self, title: str) -> NotionPageDto:
        """
        Updates this page's title.
        """
        data = {
            "properties": {
                "title": {"title": [{"type": "text", "text": {"content": title}}]}
            }
        }
        return await self.patch_page(data)

    async def archive_page(self) -> NotionPageDto:
        """
        Archives this page.
        """
        data = {"archived": True}
        return await self.patch_page(data)

    async def unarchive_page(self) -> NotionPageDto:
        """
        Unarchives this page.
        """
        data = {"archived": False}
        return await self.patch_page(data)