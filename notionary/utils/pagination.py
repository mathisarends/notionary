from collections.abc import AsyncGenerator, Callable, Coroutine
from typing import Any

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    results: list[Any]
    has_more: bool
    next_cursor: str | None


async def _fetch_data(
    api_call: Callable[..., Coroutine[Any, Any, PaginatedResponse]],
    **kwargs,
) -> AsyncGenerator[PaginatedResponse]:
    next_cursor = None
    has_more = True

    while has_more:
        current_kwargs = kwargs.copy()
        if next_cursor:
            current_kwargs["start_cursor"] = next_cursor

        response = await api_call(**current_kwargs)
        yield response

        has_more = response.has_more
        next_cursor = response.next_cursor


async def paginate_notion_api(
    api_call: Callable[..., Coroutine[Any, Any, PaginatedResponse]],
    **kwargs,
) -> list[Any]:
    all_results = []
    async for page in _fetch_data(api_call, **kwargs):
        if page.results:
            all_results.extend(page.results)
    return all_results


async def paginate_notion_api_generator(
    api_call: Callable[..., Coroutine[Any, Any, PaginatedResponse]],
    **kwargs,
) -> AsyncGenerator[Any]:
    async for page in _fetch_data(api_call, **kwargs):
        if page.results:
            for item in page.results:
                yield item
