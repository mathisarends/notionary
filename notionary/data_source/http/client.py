from notionary.data_source.schemas import DataSourceDto
from notionary.http.client import NotionHttpClient


class DataSourceClient(NotionHttpClient):
    def __init__(self, token: str | None = None, timeout: int = 30) -> None:
        super().__init__(token=token, timeout=timeout)

    async def get_data_source(self, data_source_id: str) -> DataSourceDto:
        response = await self.get(f"data_sources/{data_source_id}")
        return DataSourceDto.model_validate(response)
