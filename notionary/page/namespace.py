from collections.abc import AsyncIterator
from uuid import UUID

from notionary.http.client import HttpClient
from notionary.page import mapper
from notionary.page.exceptions import PageNotFound
from notionary.page.page import Page
from notionary.page.schemas import PageDto
from notionary.page.search import PageSearchClient
from notionary.page.search.schemas import SortDirection, SortTimestamp
from notionary.shared.search import fuzzy_suggestions


class PageNamespace:
    """Scoped access to Notion pages.

    Provides listing, searching, and retrieval of
    :class:`~notionary.page.page.Page` objects.
    """

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
        """Return pages as a list, optionally filtered by a search query.

        Args:
            query: Optional text query to filter pages by title.
            sort_direction: Sort order (ascending or descending).
            sort_timestamp: Sort by ``last_edited_time`` or ``created_time``.
            page_size: Number of results per API request.
            total_results_limit: Maximum total number of pages to return.

        Returns:
            A list of matching :class:`~notionary.page.page.Page` objects.
        """
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
        """Yield pages one by one without loading all results into memory.

        Accepts the same arguments as :meth:`list`.
        """
        async for dto in self._search_client.stream(
            query=query,
            sort_direction=sort_direction,
            sort_timestamp=sort_timestamp,
            page_size=page_size,
            total_results_limit=total_results_limit,
        ):
            yield mapper.to_page(dto, self._http)

    async def find(self, title: str) -> Page:
        """Find a page by its exact title (case-insensitive).

        Args:
            title: The page title to search for.

        Returns:
            The matching :class:`~notionary.page.page.Page`.

        Raises:
            PageNotFound: If no exact match is found. The exception
                includes fuzzy suggestions when available.
        """
        candidates = await self.list(query=title, page_size=10, total_results_limit=10)

        exact = next((p for p in candidates if p.title.lower() == title.lower()), None)
        if exact:
            return exact

        suggestions = fuzzy_suggestions(title, candidates)
        raise PageNotFound(title, suggestions)

    async def from_id(self, page_id: UUID) -> Page:
        """Retrieve a page by its UUID.

        Args:
            page_id: The Notion page UUID.

        Returns:
            The :class:`~notionary.page.page.Page` for the given ID.
        """
        response = await self._http.get(f"pages/{page_id}")
        dto = PageDto.model_validate(response)
        return mapper.to_page(dto, self._http)
