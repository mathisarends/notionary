from collections.abc import AsyncGenerator
from typing import Any

from notionary.data_source.schemas import DataSourceDto
from notionary.http.client import NotionHttpClient
from notionary.page.schemas import NotionPageDto
from notionary.utils.pagination import paginate_notion_api_generator
from notionary.workspace.query.models import WorkspaceQueryConfig
from notionary.workspace.schemas import DataSourceSearchResponse, PageSearchResponse


class WorkspaceClient:
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, http_client: NotionHttpClient | None = None) -> None:
        self._http_client = http_client or NotionHttpClient()

    async def query_pages_stream(
        self,
        search_config: WorkspaceQueryConfig,
    ) -> AsyncGenerator[NotionPageDto]:
        """Query pages with the given configuration."""
        async for page in paginate_notion_api_generator(
            self._query_pages,
            search_config=search_config,
        ):
            yield page

    async def query_data_sources_stream(
        self,
        search_config: WorkspaceQueryConfig,
    ) -> AsyncGenerator[DataSourceDto]:
        """Query data sources with the given configuration."""
        async for data_source in paginate_notion_api_generator(
            self._query_data_sources,
            search_config=search_config,
        ):
            yield data_source

    async def _query_pages(
        self,
        search_config: WorkspaceQueryConfig,
        start_cursor: str | None = None,
    ) -> PageSearchResponse:
        if start_cursor:
            search_config.start_cursor = start_cursor

        response = await self._execute_search(search_config)
        return PageSearchResponse.model_validate(response)

    async def _query_data_sources(
        self,
        search_config: WorkspaceQueryConfig,
        start_cursor: str | None = None,
    ) -> DataSourceSearchResponse:
        if start_cursor:
            search_config.start_cursor = start_cursor

        response = await self._execute_search(search_config)
        return DataSourceSearchResponse.model_validate(response)

    async def _execute_search(self, config: WorkspaceQueryConfig) -> dict[str, Any]:
        serialized_config = config.model_dump(exclude_none=True, by_alias=True)
        return await self._http_client.post("search", serialized_config)
