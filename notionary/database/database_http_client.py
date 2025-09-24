from typing import Any

from notionary.database.database_models import (
    NoionDatabaseDto,
    NotionDatabaseSearchResponse,
    NotionDatabaseUpdateDto,
    NotionQueryDatabaseResponse,
)
from notionary.http.http_client import NotionHttpClient
from notionary.page.page_models import NotionPageDto
from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.icon_models import EmojiIcon, ExternalIcon


class NotionDatabseHttpClient(NotionHttpClient):
    """
    Specialized Notion client for database operations.
    Inherits connection management and HTTP methods from NotionHttpClient.
    """

    def __init__(self, database_id: str, timeout: int = 30):
        super().__init__(timeout)
        self._database_id = database_id

    async def create_database(
        self,
        title: str,
        parent_page_id: str | None,
    ) -> NoionDatabaseDto:
        database_data = {
            "parent": {"page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": title}}],
        }

        response = await self.post("databases", database_data)
        return NoionDatabaseDto.model_validate(response)

    async def get_database(self) -> NoionDatabaseDto:
        response = await self.get(f"databases/{self._database_id}")
        return NoionDatabaseDto.model_validate(response)

    async def patch_database(self, data: dict[str, Any]) -> NoionDatabaseDto:
        response = await self.patch(f"databases/{self._database_id}", data=data)
        return NoionDatabaseDto.model_validate(response)

    async def query_database(self, query_data: dict[str, Any] | None = None) -> NotionQueryDatabaseResponse:
        response = await self.post(f"databases/{self._database_id}/query", data=query_data)
        return NotionQueryDatabaseResponse.model_validate(response)

    async def query_database_by_title(self, page_title: str) -> NotionQueryDatabaseResponse:
        query_data = {"filter": {"property": "title", "title": {"contains": page_title}}}

        return await self.query_database(query_data=query_data)

    async def search_databases(
        self, query: str = "", sort_ascending: bool = True, limit: int = 100
    ) -> NotionDatabaseSearchResponse:
        search_data = {
            "query": query,
            "filter": {"value": "database", "property": "object"},
            "sort": {
                "direction": "ascending" if sort_ascending else "descending",
                "timestamp": "last_edited_time",
            },
            "page_size": limit,
        }

        response = await self.post("search", search_data)
        return NotionDatabaseSearchResponse.model_validate(response)

    async def create_page(self) -> NotionPageDto:
        page_data = {
            "parent": {"database_id": self._database_id},
            "properties": {},
        }
        response = await self.post("pages", page_data)
        return NotionPageDto.model_validate(response)

    async def update_database_title(self, title: str) -> NoionDatabaseDto:
        from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter

        markdown_rich_text_formatter = MarkdownRichTextConverter()
        database_rich_text = await markdown_rich_text_formatter.to_rich_text(title)

        database_title_update_dto = NotionDatabaseUpdateDto(title=database_rich_text)
        database_title_update_dto_dict = database_title_update_dto.model_dump(exclude_none=True)

        return await self.patch_database(database_title_update_dto_dict)

    async def update_database_emoji_icon(self, emoji: str) -> NoionDatabaseDto:
        emoji_icon = EmojiIcon(emoji=emoji)
        database_emoji_icon_update_dto = NotionDatabaseUpdateDto(icon=emoji_icon)
        database_emoji_icon_update_dto_dict = database_emoji_icon_update_dto.model_dump(exclude_none=True)

        return await self.patch_database(database_emoji_icon_update_dto_dict)

    async def update_database_external_icon(self, icon_url: str) -> NoionDatabaseDto:
        icon = ExternalIcon.from_url(icon_url)
        database_external_icon_update_dto = NotionDatabaseUpdateDto(icon=icon)
        database_external_icon_update_dto_dict = database_external_icon_update_dto.model_dump(exclude_none=True)

        return await self.patch_database(database_external_icon_update_dto_dict)

    async def update_database_cover_image(self, image_url: str) -> NoionDatabaseDto:
        notion_cover = NotionCover.from_url(image_url)
        database_cover_update_dto = NotionDatabaseUpdateDto(cover=notion_cover)
        database_cover_update_dto_dict = database_cover_update_dto.model_dump(exclude_none=True)

        return await self.patch_database(database_cover_update_dto_dict)
