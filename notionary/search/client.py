import asyncio

from notionary.http.http_client import NotionHttpClient
from notionary.search.filter.builder import SearchFilterBuilder, SortDirection
from notionary.search.schemas import DataSourceSearchResponse, PageSearchResponse


class SearchableEntity(asyncio.Protocol):
    title: str


class SearchClient:
    def __init__(self, http_client: NotionHttpClient | None = None) -> None:
        self._http_client = http_client or NotionHttpClient()

    async def fetch_pages(
        self,
        query: str,
    ) -> PageSearchResponse:
        search_filter = (
            SearchFilterBuilder()
            .with_query(query)
            .with_sort_direction(SortDirection.ASCENDING)
            .with_pages_only()
            .with_page_size(5)
        )

        search_data = search_filter.build()
        response = await self._http_client.post("search", search_data)
        return PageSearchResponse.model_validate(response)

    async def fetch_data_sources(
        self,
        query: str,
    ) -> DataSourceSearchResponse:
        search_filter = (
            SearchFilterBuilder()
            .with_query(query)
            .with_data_sources_only()
            .with_sort_direction(SortDirection.ASCENDING)
            .with_page_size(5)
        )

        search_data = search_filter.build()
        response = await self._http_client.post("search", search_data)
        return DataSourceSearchResponse.model_validate(response)
