from typing import Any

from notionary.data_source.data_source import DataSource
from notionary.data_source.schemas import DataSourceDto
from notionary.http.client import HttpClient
from notionary.page.page import Page
from notionary.page.properties import PageTitleProperty
from notionary.page.schemas import PageDto
from notionary.rich_text import rich_text_to_markdown
from notionary.shared.search import SearchClient, SortDirection, SortTimestamp

type WorkspaceResource = Page | DataSource


class WorkspaceNamespace:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self._search_client = SearchClient(http)

    async def search(
        self,
        query: str | None = None,
        sort_direction: SortDirection = SortDirection.DESCENDING,
        sort_timestamp: SortTimestamp = SortTimestamp.LAST_EDITED_TIME,
        page_size: int = 100,
        total_results_limit: int | None = None,
    ) -> list[WorkspaceResource]:
        results = []
        async for item in self._search_client.stream(
            query=query,
            sort_direction=sort_direction,
            sort_timestamp=sort_timestamp,
            page_size=page_size,
            total_results_limit=total_results_limit,
        ):
            resource = self._resource_from_raw(item)
            if resource is not None:
                results.append(resource)
        return results

    def _resource_from_raw(self, item: dict[str, Any]) -> WorkspaceResource | None:
        object_type = item.get("object")
        if object_type == "page":
            return self._page_from_dto(PageDto.model_validate(item))
        if object_type == "data_source":
            return self._data_source_from_dto(DataSourceDto.model_validate(item))
        return None

    def _page_from_dto(self, dto: PageDto) -> Page:
        title_property = next(
            (p for p in dto.properties.values() if isinstance(p, PageTitleProperty)),
            None,
        )
        title = rich_text_to_markdown(title_property.title if title_property else [])
        return Page(
            id=dto.id,
            url=dto.url,
            title=title,
            icon=dto.icon,
            cover=dto.cover,
            in_trash=dto.in_trash,
            properties=dto.properties,
            http=self._http,
        )

    def _data_source_from_dto(self, dto: DataSourceDto) -> DataSource:
        title = rich_text_to_markdown(dto.title)
        description_text = rich_text_to_markdown(dto.description)
        return DataSource(
            id=dto.id,
            url=dto.url,
            title=title,
            description=description_text if description_text else None,
            icon=dto.icon,
            cover=dto.cover,
            in_trash=dto.in_trash,
            properties=dto.properties,
            http=self._http,
        )
