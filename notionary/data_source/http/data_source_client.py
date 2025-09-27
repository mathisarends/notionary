from notionary.data_source.data_source_models import DataSourceDto, DataSourceSearchResponse
from notionary.http.http_client import NotionHttpClient


class DataSourceClient(NotionHttpClient):
    def __init__(self, timeout: int = 30) -> None:
        super().__init__(timeout)

    async def get_data_source(self, data_source_id: str) -> DataSourceDto:
        response = await self.get(f"data_sources/{data_source_id}")
        return DataSourceDto.model_validate(response)

    async def search_data_sources(
        self, query: str = "", sort_ascending: bool = True, limit: int = 100
    ) -> DataSourceSearchResponse:
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
        return DataSourceSearchResponse.model_validate(response)
