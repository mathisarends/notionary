from collections.abc import AsyncIterator

from notionary.data_source.query.schema import DataSourceQueryParams
from notionary.data_source.schemas import (
    DataSourceDto,
    QueryDataSourceResponse,
    UpdateDataSourceDto,
)
from notionary.http.client import HttpClient
from notionary.page import Page
from notionary.page.schemas import PageDto
from notionary.rich_text.markdown_to_rich_text.factory import (
    create_markdown_to_rich_text_converter,
)


class DataSourceInstanceClient:
    def __init__(self, http: HttpClient, data_source_id: str) -> None:
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

    async def update_title(self, title: str) -> DataSourceDto:
        update_data_source_dto = UpdateDataSourceDto(title=title)
        return await self.patch_metadata(update_data_source_dto)

    async def archive(self) -> None:
        update_data_source_dto = UpdateDataSourceDto(in_trash=True)
        return await self.patch_metadata(update_data_source_dto)

    async def unarchive(self) -> None:
        update_data_source_dto = UpdateDataSourceDto(in_trash=False)
        await self.patch_metadata(update_data_source_dto)

    async def update_description(self, description: str) -> DataSourceDto:
        markdown_rich_text_converter = create_markdown_to_rich_text_converter()
        rich_text_description = await markdown_rich_text_converter.to_rich_text(
            description
        )
        update_data_source_dto = UpdateDataSourceDto(description=rich_text_description)
        return await self.patch_metadata(update_data_source_dto)

    async def query(
        self, query_params: DataSourceQueryParams | None = None
    ) -> QueryDataSourceResponse:
        query_params_dict = query_params.model_dump() if query_params else {}
        total_result_limit = query_params.total_results_limit if query_params else None

        all_results = await self._http.paginate(
            f"data_sources/{self._data_source_id}/query",
            total_results_limit=total_result_limit,
            **(query_params_dict or {}),
        )

        return QueryDataSourceResponse(
            results=[PageDto.model_validate(r) for r in all_results],
            next_cursor=None,
            has_more=False,
        )

    async def query_stream(
        self, query_params: DataSourceQueryParams | None = None
    ) -> AsyncIterator[PageDto]:
        query_params_dict = query_params.model_dump() if query_params else {}
        total_result_limit = query_params.total_results_limit if query_params else None

        async for result in self._http.paginate_stream(
            f"data_sources/{self._data_source_id}/query",
            total_results_limit=total_result_limit,
            **(query_params_dict or {}),
        ):
            yield PageDto.model_validate(result)

    async def create_blank_page(self, title: str | None = None) -> Page:
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
