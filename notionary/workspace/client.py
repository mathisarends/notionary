from collections.abc import AsyncGenerator

from notionary.data_source.schemas import DataSourceDto
from notionary.http.client import HttpClient
from notionary.page.schemas import NotionPageDto
from notionary.workspace.query.models import WorkspaceQueryConfig


class WorkspaceClient:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def query_pages_stream(
        self,
        search_config: WorkspaceQueryConfig,
    ) -> AsyncGenerator[NotionPageDto]:
        params = self._to_api_params(search_config)
        async for item in self._http.paginate_stream(
            "search",
            total_results_limit=search_config.total_results_limit,
            **params,
        ):
            yield NotionPageDto.model_validate(item)

    async def query_data_sources_stream(
        self,
        search_config: WorkspaceQueryConfig,
    ) -> AsyncGenerator[DataSourceDto]:
        params = self._to_api_params(search_config)
        async for item in self._http.paginate_stream(
            "search",
            total_results_limit=search_config.total_results_limit,
            **params,
        ):
            yield DataSourceDto.model_validate(item)

    @staticmethod
    def _to_api_params(config: WorkspaceQueryConfig) -> dict:
        params = config.model_dump()
        params.pop("start_cursor", None)  # managed internally by HttpClient
        return params
