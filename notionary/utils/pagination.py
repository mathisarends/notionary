from collections.abc import AsyncGenerator, Callable, Coroutine
from typing import Any

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    results: list[Any]
    has_more: bool
    next_cursor: str | None


async def _fetch_data(
    api_call: Callable[..., Coroutine[Any, Any, PaginatedResponse]],
    page_size: int | None = None,
    **kwargs,
) -> AsyncGenerator[PaginatedResponse]:
    next_cursor = None
    has_more = True
    total_fetched = 0

    while has_more and _should_continue_fetching(page_size, total_fetched):
        request_params = _build_request_params(kwargs, next_cursor, page_size)
        response = await api_call(**request_params)

        limited_results = _apply_result_limit(response.results, page_size, total_fetched)
        total_fetched += len(limited_results)

        yield _create_limited_response(response, limited_results)

        if _has_reached_limit(page_size, total_fetched):
            break

        has_more = response.has_more
        next_cursor = response.next_cursor


def _should_continue_fetching(page_size: int | None, total_fetched: int) -> bool:
    if page_size is None:
        return True
    return total_fetched < page_size


def _build_request_params(
    base_kwargs: dict[str, Any],
    cursor: str | None,
    page_size: int | None,
) -> dict[str, Any]:
    params = base_kwargs.copy()

    if cursor:
        params["start_cursor"] = cursor

    if page_size:
        params["page_size"] = page_size

    return params


def _apply_result_limit(results: list[Any], page_size: int | None, total_fetched: int) -> list[Any]:
    if page_size is None:
        return results

    remaining = page_size - total_fetched
    return results[:remaining]


def _has_reached_limit(page_size: int | None, total_fetched: int) -> bool:
    if page_size is None:
        return False
    return total_fetched >= page_size


def _create_limited_response(original: PaginatedResponse, limited_results: list[Any]) -> PaginatedResponse:
    return PaginatedResponse(
        results=limited_results,
        has_more=original.has_more and len(limited_results) == len(original.results),
        next_cursor=original.next_cursor,
    )


async def paginate_notion_api(
    api_call: Callable[..., Coroutine[Any, Any, PaginatedResponse]],
    page_size: int | None = None,
    **kwargs,
) -> list[Any]:
    all_results = []
    async for page in _fetch_data(api_call, page_size=page_size, **kwargs):
        all_results.extend(page.results)
    return all_results


async def paginate_notion_api_generator(
    api_call: Callable[..., Coroutine[Any, Any, PaginatedResponse]],
    page_size: int | None = None,
    **kwargs,
) -> AsyncGenerator[Any]:
    async for page in _fetch_data(api_call, page_size=page_size, **kwargs):
        for item in page.results:
            yield item
