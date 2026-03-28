from collections.abc import AsyncIterator
from uuid import UUID

from notionary.http.client import HttpClient
from notionary.page.exceptions import PageNotFound
from notionary.page.page import Page
from notionary.page.properties import PageTitleProperty
from notionary.page.schemas import PageDto
from notionary.page.search import PageSearchClient
from notionary.page.search.schemas import SortDirection, SortTimestamp
from notionary.rich_text import rich_text_to_markdown
from notionary.shared.search import fuzzy_suggestions


class PageNamespace:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self._search_client = PageSearchClient(http)

    async def list(
        self,
        query: str | None = None,
        sort_direction: SortDirection = SortDirection.DESCENDING,
        sort_timestamp: SortTimestamp = SortTimestamp.LAST_EDITED_TIME,
        page_size: int = 100,
        total_results_limit: int | None = None,
    ) -> list[Page]:
        return [
            page
            async for page in self.iter(
                query=query,
                sort_direction=sort_direction,
                sort_timestamp=sort_timestamp,
                page_size=page_size,
                total_results_limit=total_results_limit,
            )
        ]

    async def iter(
        self,
        query: str | None = None,
        sort_direction: SortDirection = SortDirection.DESCENDING,
        sort_timestamp: SortTimestamp = SortTimestamp.LAST_EDITED_TIME,
        page_size: int = 100,
        total_results_limit: int | None = None,
    ) -> AsyncIterator[Page]:
        async for dto in self._search_client.stream(
            query=query,
            sort_direction=sort_direction,
            sort_timestamp=sort_timestamp,
            page_size=page_size,
            total_results_limit=total_results_limit,
        ):
            yield self._page_from_dto(dto)

    async def from_title(self, title: str) -> Page:
        candidates = await self.list(query=title, page_size=100)

        exact = next((p for p in candidates if p.title.lower() == title.lower()), None)
        if exact:
            return exact

        suggestions = fuzzy_suggestions(title, candidates)
        raise PageNotFound(title, suggestions)

    async def from_id(self, page_id: UUID) -> Page:
        response = await self._http.get(f"pages/{page_id}")
        dto = PageDto.model_validate(response)
        return self._page_from_dto(dto)

    def _page_from_dto(self, dto: PageDto) -> Page:
        title = self._extract_page_title(dto)
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

    def _extract_page_title(self, dto: PageDto) -> str:
        title_property = next(
            (p for p in dto.properties.values() if isinstance(p, PageTitleProperty)),
            None,
        )
        return rich_text_to_markdown(title_property.title if title_property else [])
