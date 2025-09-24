from typing import Any

from notionary.database.database_models import (
    NotionDatabaseDto,
    NotionDatabaseSearchResponse,
    NotionDatabaseUpdateDto,
    NotionQueryDatabaseResponse,
)
from notionary.http.http_client import NotionHttpClient
from notionary.page.page_models import NotionPageDto


class NotionDatabseHttpClient(NotionHttpClient):
    def __init__(self, database_id: str, timeout: int = 30):
        super().__init__(timeout)
        self._database_id = database_id

    async def create_database(
        self,
        title: str,
        parent_page_id: str | None,
    ) -> NotionDatabaseDto:
        database_data = {
            "parent": {"page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": title}}],
        }

        response = await self.post("databases", database_data)
        return NotionDatabaseDto.model_validate(response)

    async def get_database(self) -> NotionDatabaseDto:
        response = await self.get(f"databases/{self._database_id}")
        return NotionDatabaseDto.model_validate(response)

    async def patch_database(self, data: dict[str, Any]) -> NotionDatabaseDto:
        response = await self.patch(f"databases/{self._database_id}", data=data)
        return NotionDatabaseDto.model_validate(response)

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

    async def update_database_title(self, title: str) -> NotionDatabaseDto:
        from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter

        markdown_rich_text_formatter = MarkdownRichTextConverter()
        database_rich_text = await markdown_rich_text_formatter.to_rich_text(title)

        database_title_update_dto = NotionDatabaseUpdateDto(title=database_rich_text)
        database_title_update_dto_dict = database_title_update_dto.model_dump(exclude_none=True)

        return await self.patch_database(database_title_update_dto_dict)
