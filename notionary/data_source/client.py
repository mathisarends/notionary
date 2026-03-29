from uuid import UUID

from notionary.data_source.schemas import (
    DataSourceDto,
    UpdateDataSourceDto,
)
from notionary.http.client import HttpClient
from notionary.page import Page
from notionary.page import mapper as page_mapper
from notionary.page.schemas import PageDto
from notionary.rich_text import markdown_to_rich_text


class DataSourceClient:
    def __init__(self, http: HttpClient, data_source_id: UUID) -> None:
        self._http = http
        self._data_source_id = data_source_id

    async def patch_metadata(
        self, update_data_source_dto: UpdateDataSourceDto
    ) -> DataSourceDto:
        response = await self._http.patch(
            f"data_sources/{self._data_source_id}", data=update_data_source_dto
        )
        return DataSourceDto.model_validate(response)

    async def set_title(self, title: str) -> DataSourceDto:
        rich_text_title = markdown_to_rich_text(title)
        update_data_source_dto = UpdateDataSourceDto(title=rich_text_title)
        return await self.patch_metadata(update_data_source_dto)

    async def create_page(self, title: str | None = None) -> Page:
        data = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": str(self._data_source_id),
            },
            "properties": {},
        }

        if title:
            data["properties"]["Name"] = {"title": [{"text": {"content": title}}]}

        response = await self._http.post("pages", data=data)
        dto = PageDto.model_validate(response)
        return page_mapper.to_page(dto, self._http)
