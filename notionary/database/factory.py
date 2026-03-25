import asyncio

from notionary.database.client import DatabaseHttpClient
from notionary.database.schemas import DatabaseDto
from notionary.database.service import Database
from notionary.http.client import HttpClient
from notionary.shared.entity.dto_parsers import extract_description, extract_title
from notionary.shared.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)


class DatabaseFactory:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def from_id(self, database_id: str) -> Database:
        dto = await self._fetch_dto(database_id)
        return await self.from_dto(dto)

    async def from_dto(self, dto: DatabaseDto) -> Database:
        converter = RichTextToMarkdownConverter()
        title, description = await asyncio.gather(
            extract_title(dto, converter),
            extract_description(dto, converter),
        )

        client = DatabaseHttpClient(database_id=dto.id)

        return Database(
            dto=dto,
            title=title,
            description=description,
            data_source_ids=[ds.id for ds in dto.data_sources],
            client=client,
            http=self._http,
        )

    async def _fetch_dto(self, database_id: str) -> DatabaseDto:
        response = await self._http.get(f"databases/{database_id}")
        return DatabaseDto.model_validate(response)
