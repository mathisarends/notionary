from notionary.data_source.data_source_models import DataSourceDto
from notionary.http.http_client import NotionHttpClient


class NotionDataSourceHttpClient(NotionHttpClient):
    def __init__(self, data_source_id: str) -> None:
        super().__init__()
        self._data_source_id = data_source_id

    async def get_data_source(self) -> DataSourceDto:
        response = await self.get(f"data_sources/{self._data_source_id}")

        import json

        print("RESPONSE", json.dumps(response, indent=4))

        return DataSourceDto.model_validate(response)
