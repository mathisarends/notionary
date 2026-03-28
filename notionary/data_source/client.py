from uuid import UUID

from notionary.data_source.schemas import (
    DataSourceDto,
    UpdateDataSourceDto,
)
from notionary.http.client import HttpClient
from notionary.page import Page
from notionary.page.schemas import PageDto
from notionary.rich_text import markdown_to_rich_text


class DataSourceClient:
    def __init__(self, http: HttpClient, data_source_id: UUID) -> None:
        self._http = http
        self._data_source_id = data_source_id

    async def patch_metadata(
        self, update_data_source_dto: UpdateDataSourceDto
    ) -> DataSourceDto:
        update_data_source_dto_dict = update_data_source_dto.model_dump(
            exclude_none=True
        )
        response = await self._http.patch(
            f"data_sources/{self._data_source_id}", data=update_data_source_dto_dict
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
                "data_source_id": self._data_source_id,
            },
            "properties": {},
        }

        if title:
            data["properties"]["Name"] = {"title": [{"text": {"content": title}}]}

        response = await self._http.post("pages", data=data)
        page_creation_response = PageDto.model_validate(response)
        return await Page.from_id(page_creation_response.id)
