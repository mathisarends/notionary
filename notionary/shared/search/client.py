from collections.abc import AsyncGenerator
from typing import Any

from notionary.http import HttpClient
from notionary.shared.search.schemas import (
    SearchQueryConfig,
    SortDirection,
    SortTimestamp,
)


class SearchClient:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def stream(
        self,
        query: str | None = None,
        sort_direction: SortDirection = SortDirection.DESCENDING,
        sort_timestamp: SortTimestamp = SortTimestamp.LAST_EDITED_TIME,
        page_size: int = 100,
        total_results_limit: int | None = None,
    ) -> AsyncGenerator[dict[str, Any]]:
        config = SearchQueryConfig(
            query=query,
            sort_direction=sort_direction,
            sort_timestamp=sort_timestamp,
            page_size=page_size,
            total_results_limit=total_results_limit,
        )
        async for item in self._http.paginate_stream(
            endpoint="search",
            total_results_limit=config.total_results_limit,
            **config.model_dump(mode="json"),
        ):
            yield item
