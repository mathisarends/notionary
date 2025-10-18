from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, override

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.data_source.query.schema import DataSourceQueryParams
from notionary.data_source.schemas import DataSourceDto, QueryDataSourceResponse, UpdateDataSourceDto
from notionary.http.client import NotionHttpClient
from notionary.page.schemas import NotionPageDto
from notionary.shared.entity.entity_metadata_update_client import EntityMetadataUpdateClient
from notionary.shared.typings import JsonDict
from notionary.utils.pagination import paginate_notion_api, paginate_notion_api_generator

if TYPE_CHECKING:
    from notionary import NotionPage


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

    async def query(self, query_params: DataSourceQueryParams | None = None) -> QueryDataSourceResponse:
        query_params_dict = query_params.to_api_params() if query_params else {}
        page_size = query_params.page_size if query_params else None

        all_results = await paginate_notion_api(
            self._make_query_request, query_data=query_params_dict or {}, page_size=page_size
        )

        return QueryDataSourceResponse(
            results=all_results,
            next_cursor=None,
            has_more=False,
        )

    async def query_stream(self, query_params: DataSourceQueryParams | None = None) -> AsyncIterator[Any]:
        query_params_dict = query_params.model_dump() if query_params else {}
        page_size = query_params.page_size if query_params else None

        async for result in paginate_notion_api_generator(
            self._make_query_request, query_data=query_params_dict or {}, page_size=page_size
        ):
            yield result

    async def _make_query_request(
        self, query_data: JsonDict, start_cursor: str | None = None, page_size: int | None = None
    ) -> QueryDataSourceResponse:
        current_query_data = query_data.copy()
        if start_cursor:
            current_query_data["start_cursor"] = start_cursor
        if page_size:
            current_query_data["page_size"] = page_size

        response = await self.post(f"data_sources/{self._data_source_id}/query", data=current_query_data)
        return QueryDataSourceResponse.model_validate(response)

    async def create_blank_page(self, title: str | None = None) -> NotionPage:
        from notionary import NotionPage

        data = {"parent": {"type": "data_source_id", "data_source_id": self._data_source_id}, "properties": {}}

        if title:
            data["properties"]["Name"] = {"title": [{"text": {"content": title}}]}

        response = await self.post("pages", data=data)
        page_creation_response = NotionPageDto.model_validate(response)
        return await NotionPage.from_id(page_creation_response.id)
