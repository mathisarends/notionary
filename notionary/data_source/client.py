from uuid import UUID

from notionary.data_source.schemas import (
    DataSourceDto,
    UpdateDataSourceDto,
)
from notionary.http.client import HttpClient
from notionary.page import Page
from notionary.page.properties import PageTitleProperty
from notionary.page.schemas import PageDto
from notionary.rich_text import markdown_to_rich_text, rich_text_to_markdown


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

        title_property = next(
            (p for p in dto.properties.values() if isinstance(p, PageTitleProperty)),
            None,
        )
        page_title = rich_text_to_markdown(
            title_property.title if title_property else []
        )

        return Page(
            id=dto.id,
            url=dto.url,
            title=page_title,
            icon=dto.icon,
            cover=dto.cover,
            in_trash=dto.in_trash,
            properties=dto.properties,
            http=self._http,
            created_time=dto.created_time,
            created_by=dto.created_by,
            last_edited_time=dto.last_edited_time,
            last_edited_by=dto.last_edited_by,
        )
