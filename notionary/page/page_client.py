from typing import Any, Optional, Union

from pydantic import BaseModel

from notionary.notion_client import NotionClient
from notionary.page.page_models import NotionPageDto, NotionPageUpdateDto
from notionary.shared.models.icon_models import EmojiIcon, ExternalIcon
from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.file_models import ExternalFile


class NotionPageClient(NotionClient):
    """
    Client for Notion page-specific operations.
    Inherits base HTTP functionality from NotionClient.
    """

    def __init__(
        self,
        page_id: str,
        initial_page_schema: NotionPageUpdateDto,
        token: Optional[str] = None,
    ):
        """Initialize with optional page_id for methods that operate on a specific page."""
        super().__init__(token=token)
        self.page_id = page_id
        self._page_schema = initial_page_schema

    async def patch_page(self, data: Union[dict[str, Any], BaseModel]) -> NotionPageDto:
        """
        Updates this page with the provided data.
        """
        if isinstance(data, BaseModel):
            data = data.model_dump(exclude_unset=True, exclude_none=True)

        response = await self.patch(f"pages/{self.page_id}", data=data)
        result = NotionPageDto.model_validate(response)
        self._update_page_schema(result)
        return result

    async def patch_emoji_icon(self, emoji: str) -> NotionPageDto:
        """Updates this page's icon to an emoji using the schema approach."""
        icon = EmojiIcon(emoji=emoji)
        update_dto = NotionPageUpdateDto(icon=icon)

        return await self.patch_page(update_dto)

    async def patch_external_icon(self, icon_url: str) -> NotionPageDto:
        """Updates this page's icon to an external image using the schema approach."""
        external_file = ExternalFile(url=icon_url)
        icon = ExternalIcon(external=external_file)
        update_dto = NotionPageUpdateDto(icon=icon)

        return await self.patch_page(update_dto)

    async def remove_icon(self) -> NotionPageDto:
        """Removes the icon using the schema approach."""
        update_dto = NotionPageUpdateDto(icon=None)

        return await self.patch_page(update_dto)

    async def patch_external_cover(self, cover_url: str) -> NotionPageDto:
        """Updates this page's cover using the schema approach."""
        cover = NotionCover.from_url(cover_url)
        update_dto = NotionPageUpdateDto(cover=cover)

        return await self.patch_page(update_dto)

    async def remove_cover(self) -> NotionPageDto:
        """Removes the cover using the schema approach."""
        update_dto = NotionPageUpdateDto(cover=None)

        return await self.patch_page(update_dto)

    async def patch_title(self, title: str) -> NotionPageDto:
        """Updates this page's title using the schema approach."""
        properties = {
            "title": {"title": [{"type": "text", "text": {"content": title}}]}
        }
        update_dto = NotionPageUpdateDto(properties=properties)

        return await self.patch_page(update_dto)

    async def archive_page(self) -> NotionPageDto:
        """Archives this page using the schema approach."""
        update_dto = NotionPageUpdateDto(archived=True)

        return await self.patch_page(update_dto)

    async def unarchive_page(self) -> NotionPageDto:
        """Unarchives this page using the schema approach."""
        update_dto = NotionPageUpdateDto(archived=False)

        return await self.patch_page(update_dto)

    def _update_page_schema(self, updated: NotionPageDto) -> None:
        """Update internal schema with response from API."""
        self._page_schema = NotionPageUpdateDto.from_notion_page_dto(updated)
