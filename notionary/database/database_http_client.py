from typing import Any

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.database.database_models import (
    NotionDatabaseDto,
    NotionDatabaseUpdateDto,
    NotionQueryDatabaseResponse,
)
from notionary.http.http_client import NotionHttpClient
from notionary.page.page_models import NotionPageDto


class NotionDatabaseHttpClient(NotionHttpClient):
    def __init__(self, database_id: str, timeout: int = 30) -> None:
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

    async def patch_database(self, update_database_dto: NotionDatabaseUpdateDto) -> NotionDatabaseDto:
        update_database_dto_dict = update_database_dto.model_dump(exclude_none=True)

        response = await self.patch(f"databases/{self._database_id}", data=update_database_dto_dict)
        return NotionDatabaseDto.model_validate(response)

    async def query_database(self, query_data: dict[str, Any] | None = None) -> NotionQueryDatabaseResponse:
        response = await self.post(f"databases/{self._database_id}/query", data=query_data)
        return NotionQueryDatabaseResponse.model_validate(response)

    async def query_database_by_title(self, page_title: str) -> NotionQueryDatabaseResponse:
        query_data = {"filter": {"property": "title", "title": {"contains": page_title}}}

        return await self.query_database(query_data=query_data)

    async def create_page(self) -> NotionPageDto:
        page_data = {
            "parent": {"database_id": self._database_id},
            "properties": {},
        }
        response = await self.post("pages", page_data)
        return NotionPageDto.model_validate(response)

    async def update_database_title(self, title: str) -> NotionDatabaseDto:
        markdown_rich_text_formatter = MarkdownRichTextConverter()
        database_rich_text = await markdown_rich_text_formatter.to_rich_text(title)

        database_title_update_dto = NotionDatabaseUpdateDto(title=database_rich_text)
        return await self.patch_database(database_title_update_dto)

    async def update_database_description(self, description: str) -> str:
        markdown_to_rich_text_converter = MarkdownRichTextConverter()
        rich_text_description = await markdown_to_rich_text_converter.to_rich_text(description)

        database_description_update_dto = NotionDatabaseUpdateDto(description=rich_text_description)
        update_database_response = await self.patch_database(database_description_update_dto)

        rich_text_to_markdown_converter = RichTextToMarkdownConverter()
        return await rich_text_to_markdown_converter.to_markdown(update_database_response.description)
