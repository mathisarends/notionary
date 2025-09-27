import asyncio

from notionary.data_source.data_source import NotionDataSource
from notionary.data_source.data_source_models import DataSourceDto, DataSourceSearchResponse
from notionary.http.http_client import NotionHttpClient
from notionary.util.fuzzy import find_best_match


class SearchableEntity(asyncio.Protocol):
    title: str


class SearchClient(NotionHttpClient):
    def __init__(self, timeout: int = 30) -> None:
        super().__init__(timeout)

    async def get_data_source(self, data_source_id: str) -> DataSourceDto:
        response = await self.get(f"data_sources/{data_source_id}")
        return DataSourceDto.model_validate(response)

    async def search_data_sources(
        self, query: str = "", sort_ascending: bool = True, limit: int = 100
    ) -> list[NotionDataSource]:
        search_data = {
            "query": query,
            "filter": {"value": "data_source", "property": "object"},
            "sort": {
                "direction": "ascending" if sort_ascending else "descending",
                "timestamp": "last_edited_time",
            },
            "page_size": limit,
        }

        response = await self.post("search", search_data)
        data_source_search_response = DataSourceSearchResponse.model_validate(response)

        return await asyncio.gather(
            *(NotionDataSource.from_id(data_source.id) for data_source in data_source_search_response.results)
        )

    async def find_data_source(
        self, query: str = "", sort_ascending: bool = True, limit: int = 100, min_similarity: float = 0.6
    ) -> NotionDataSource | None:
        data_sources = await self.search_data_sources(query, sort_ascending, limit)
        return self._get_best_match(data_sources, query, min_similarity=min_similarity)

    async def find_database(
        self, query: str = "", sort_ascending: bool = True, limit: int = 100
    ) -> DataSourceSearchResponse:
        data_sources = await self.search_data_sources(query, sort_ascending, limit)

        potential_databases = [
            data_source.parent_database for data_source in data_sources if data_source.parent_database
        ]

        return self._get_best_match(potential_databases, query)

    def _get_best_match(
        self, search_results: list[SearchableEntity], query: str, min_similarity: float | None = None
    ) -> NotionDataSource | None:
        best_match = find_best_match(
            query=query,
            items=search_results,
            text_extractor=lambda searchable_entity: searchable_entity.title,
            min_similarity=min_similarity,
        )

        if not best_match:
            available_titles = [result.title for result in search_results[:5]]
            raise ValueError(f"No sufficiently similar entity found for '{query}'. Available: {available_titles}")

        return best_match.item
