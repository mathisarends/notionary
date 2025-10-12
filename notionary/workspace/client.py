from collections.abc import AsyncGenerator

from notionary.data_source.schemas import DataSourceDto
from notionary.http.client import NotionHttpClient
from notionary.page.schemas import NotionPageDto
from notionary.utils.pagination import paginate_notion_api_generator
from notionary.workspace.query.builder import SortDirection, WorkspaceQueryBuilder
from notionary.workspace.schemas import DataSourceSearchResponse, PageSearchResponse


class WorkspaceClient:
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, http_client: NotionHttpClient | None = None) -> None:
        self._http_client = http_client or NotionHttpClient()

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
        search_filter = (
            WorkspaceQueryBuilder()
            .with_query(query)
            .with_pages_only()
            .with_page_size(page_size)
            .with_start_cursor(start_cursor)
        )

        search_data = search_filter.build()
        response = await self._http_client.post("search", search_data)
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
        search_filter = (
            WorkspaceQueryBuilder()
            .with_sort_direction(SortDirection.ASCENDING)
            .with_pages_only()
            .with_page_size(page_size)
            .with_start_cursor(start_cursor)
        )

        search_data = search_filter.build()
        response = await self._http_client.post("search", search_data)
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
        search_filter = (
            WorkspaceQueryBuilder()
            .with_query(query)
            .with_data_sources_only()
            .with_page_size(page_size)
            .with_start_cursor(start_cursor)
        )

        search_data = search_filter.build()
        response = await self._http_client.post("search", search_data)
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
        search_filter = (
            WorkspaceQueryBuilder()
            .with_data_sources_only()
            .with_sort_direction(SortDirection.ASCENDING)
            .with_page_size(page_size)
            .with_start_cursor(start_cursor)
        )

        search_data = search_filter.build()
        response = await self._http_client.post("search", search_data)
        return DataSourceSearchResponse.model_validate(response)
