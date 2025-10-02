from typing import Any, override

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.data_source.schemas import DataSourceDto, QueryDataSourceResponse, UpdateDataSourceDto
from notionary.http.http_client import NotionHttpClient
from notionary.shared.entity.entity_metadata_update_client import EntityMetadataUpdateClient


class DataSourceInstanceClient(NotionHttpClient, EntityMetadataUpdateClient):
    def __init__(self, data_source_id: str, timeout: int = 30) -> None:
        super().__init__(timeout)
        self._data_source_id = data_source_id

    @override
    async def patch_metadata(self, update_data_source_dto: UpdateDataSourceDto) -> DataSourceDto:
        update_data_source_dto_dict = update_data_source_dto.model_dump(exclude_none=True)
        response = await self.patch(f"data_sources/{self._data_source_id}", data=update_data_source_dto_dict)
        return DataSourceDto.model_validate(response)

    async def update_title(self, title: str) -> DataSourceDto:
        update_data_source_dto = UpdateDataSourceDto(title=title)
        return await self.patch_metadata(update_data_source_dto)

    async def archive(self) -> None:
        update_data_source_dto = UpdateDataSourceDto(archived=True)
        return await self.patch_metadata(update_data_source_dto)

    async def unarchive(self) -> None:
        update_data_source_dto = UpdateDataSourceDto(archived=False)
        await self.patch_metadata(update_data_source_dto)

    async def update_description(self, description: str) -> str:
        from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter

        markdown_rich_text_converter = MarkdownRichTextConverter()
        rich_text_description = await markdown_rich_text_converter.to_rich_text(description)
        update_data_source_dto = UpdateDataSourceDto(description=rich_text_description)

        updated_data_source_dto = await self.patch_metadata(update_data_source_dto)

        markdown_rich_text_converter = RichTextToMarkdownConverter()
        updated_markdown_description = (
            await markdown_rich_text_converter.to_markdown(updated_data_source_dto.description)
            if updated_data_source_dto.description
            else None
        )
        return updated_markdown_description

    async def query(self, query_data: dict[str, Any] | None = None) -> QueryDataSourceResponse:
        response = await self.post(f"data_sources/{self._data_source_id}/query", data=query_data)
        return QueryDataSourceResponse.model_validate(response)

    async def create_blank_page(self, title: str | None = None) -> dict[str, Any]:
        data = {"parent": {"type": "data_source_id", "data_source_id": self._data_source_id}, "properties": {}}

        if title:
            data["properties"]["Name"] = {"title": [{"text": {"content": title}}]}

        await self.post("pages", data=data)
