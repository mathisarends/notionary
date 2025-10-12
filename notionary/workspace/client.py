from collections.abc import AsyncGenerator
from typing import Any

from notionary.data_source.schemas import DataSourceDto
from notionary.http.client import NotionHttpClient
from notionary.page.schemas import NotionPageDto
from notionary.utils.pagination import paginate_notion_api_generator
from notionary.workspace.query.builder import WorkspaceQueryConfigBuilder
from notionary.workspace.query.models import WorkspaceQueryConfig, WorkspaceSearchObjectType
from notionary.workspace.schemas import DataSourceSearchResponse, PageSearchResponse


class WorkspaceClient:
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, http_client: NotionHttpClient | None = None) -> None:
        self._http_client = http_client or NotionHttpClient()

    async def query_stream(
        self,
        search_config: WorkspaceQueryConfig,
    ) -> AsyncGenerator[NotionPageDto | DataSourceDto]:
        async for item in paginate_notion_api_generator(
            self._query,
            search_config=search_config,
        ):
            yield item

    async def _query(
        self,
        search_config: WorkspaceQueryConfig,
        start_cursor: str | None = None,
    ) -> PageSearchResponse | DataSourceSearchResponse:
        if start_cursor:
            search_config.start_cursor = start_cursor

        response = await self._execute_search(search_config)

        if search_config.object_type == WorkspaceSearchObjectType.DATA_SOURCE:
            return DataSourceSearchResponse.model_validate(response)

        return PageSearchResponse.model_validate(response)

    async def search_pages_stream(
        self,
        query: str,
        page_size: int | None = None,
    ) -> AsyncGenerator[NotionPageDto]:
        async for page in paginate_notion_api_generator(
            self._fetch_pages,
            query=query,
            page_size=page_size or self.DEFAULT_PAGE_SIZE,
        ):
            yield page

    async def _fetch_pages(
        self,
        query: str,
        page_size: int,
        start_cursor: str | None = None,
    ) -> PageSearchResponse:
        query_config = (
            WorkspaceQueryConfigBuilder()
            .with_query(query)
            .with_pages_only()
            .with_page_size(page_size)
            .with_start_cursor(start_cursor)
            .build()
        )

        response = await self._execute_search(query_config)
        return PageSearchResponse.model_validate(response)

    async def get_pages_stream(
        self,
        page_size: int | None = None,
    ) -> AsyncGenerator[NotionPageDto]:
        async for page in paginate_notion_api_generator(
            self._list_pages,
            page_size=page_size or self.DEFAULT_PAGE_SIZE,
        ):
            yield page

    async def _list_pages(
        self,
        page_size: int,
        start_cursor: str | None = None,
    ) -> PageSearchResponse:
        query_config = (
            WorkspaceQueryConfigBuilder()
            .with_pages_only()
            .with_sort_ascending()
            .with_page_size(page_size)
            .with_start_cursor(start_cursor)
            .build()
        )

        response = await self._execute_search(query_config)
        return PageSearchResponse.model_validate(response)

    async def search_data_sources_stream(
        self,
        query: str,
        page_size: int | None = None,
    ) -> AsyncGenerator[DataSourceDto]:
        async for data_source in paginate_notion_api_generator(
            self._fetch_data_sources,
            query=query,
            page_size=page_size or self.DEFAULT_PAGE_SIZE,
        ):
            yield data_source

    async def _fetch_data_sources(
        self,
        query: str,
        page_size: int,
        start_cursor: str | None = None,
    ) -> DataSourceSearchResponse:
        query_config = (
            WorkspaceQueryConfigBuilder()
            .with_query(query)
            .with_data_sources_only()
            .with_page_size(page_size)
            .with_start_cursor(start_cursor)
            .build()
        )

        response = await self._execute_search(query_config)
        return DataSourceSearchResponse.model_validate(response)

    async def get_data_sources_stream(
        self,
        page_size: int | None = None,
    ) -> AsyncGenerator[DataSourceDto]:
        async for data_source in paginate_notion_api_generator(
            self._list_data_sources,
            page_size=page_size or self.DEFAULT_PAGE_SIZE,
        ):
            yield data_source

    async def _list_data_sources(
        self,
        page_size: int,
        start_cursor: str | None = None,
    ) -> DataSourceSearchResponse:
        query_config = (
            WorkspaceQueryConfigBuilder()
            .with_data_sources_only()
            .with_sort_ascending()
            .with_page_size(page_size)
            .with_start_cursor(start_cursor)
            .build()
        )

        response = await self._execute_search(query_config)
        return DataSourceSearchResponse.model_validate(response)

    async def _execute_search(self, config: WorkspaceQueryConfig) -> dict[str, Any]:
        serialized_config = config.model_dump(exclude_none=True, by_alias=True)
        return await self._http_client.post("search", serialized_config)
