from notionary.data_source.data_source_models import DataSourceDto
from notionary.http.http_client import NotionHttpClient


class DataSourceClient(NotionHttpClient):
    def __init__(self, timeout: int = 30) -> None:
        super().__init__(timeout)

    async def get_data_source(self, data_source_id: str) -> DataSourceDto:
        response = await self.get(f"data_sources/{data_source_id}")
        return DataSourceDto.model_validate(response)
