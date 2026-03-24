import difflib
from collections.abc import AsyncIterator

from notionary.exceptions.search import PageNotFound
from notionary.http.client import HttpClient
from notionary.page.factory import PageFactory
from notionary.page.search import PageSearchClient
from notionary.page.search.schemas import SortDirection, SortTimestamp
from notionary.page.service import Page


def _fuzzy_suggestions(query: str, pages: list[Page], top_n: int = 5) -> list[str]:
    scored = [
        (page, difflib.SequenceMatcher(None, query.lower(), page.title.lower()).ratio())
        for page in pages
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [page.title for page, score in scored[:top_n] if score >= 0.6]


class PageNamespace:
    def __init__(self, http: HttpClient) -> None:
        self._search_client = PageSearchClient(http)
        self._factory = PageFactory(http)

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
            yield await self._factory.from_dto(dto)

    async def from_title(self, title: str) -> Page:
        candidates = await self.list(query=title, page_size=100)

        exact = next((p for p in candidates if p.title.lower() == title.lower()), None)
        if exact:
            return exact

        suggestions = _fuzzy_suggestions(title, candidates)
        raise PageNotFound(title, suggestions)

    async def from_id(self, page_id: str) -> Page:
        return await self._factory.from_id(page_id)
