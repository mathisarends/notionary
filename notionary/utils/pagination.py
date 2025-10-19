from collections.abc import AsyncGenerator, Callable, Coroutine
from typing import Any

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    results: list[Any]
    has_more: bool
    next_cursor: str | None


async def _fetch_data(
    api_call: Callable[..., Coroutine[Any, Any, PaginatedResponse]],
    total_results_limit: int | None = None,
    **kwargs,
) -> AsyncGenerator[PaginatedResponse]:
    next_cursor: str | None = None
    has_more: bool = True
    total_fetched: int = 0
    api_page_size: int = kwargs.get("page_size", 100)

    while has_more and _should_continue_fetching(total_results_limit, total_fetched):
        request_params = _build_request_params(kwargs, next_cursor)
        response = await api_call(**request_params)

        limited_results = _apply_result_limit(response.results, total_results_limit, total_fetched)
        total_fetched += len(limited_results)

        yield _create_limited_response(response, limited_results, api_page_size)

        if _has_reached_limit(total_results_limit, total_fetched):
            break

        has_more = response.has_more
        next_cursor = response.next_cursor


def _should_continue_fetching(total_limit: int | None, total_fetched: int) -> bool:
    if total_limit is None:
        return True
    return total_fetched < total_limit


def _build_request_params(
    base_kwargs: dict[str, Any],
    cursor: str | None,
) -> dict[str, Any]:
    params = base_kwargs.copy()
    if cursor:
        params["start_cursor"] = cursor
    return params


def _apply_result_limit(results: list[Any], total_limit: int | None, total_fetched: int) -> list[Any]:
    if total_limit is None:
        return results

    remaining_space = total_limit - total_fetched
    return results[:remaining_space]


def _has_reached_limit(total_limit: int | None, total_fetched: int) -> bool:
    if total_limit is None:
        return False
    return total_fetched >= total_limit


def _create_limited_response(
    original: PaginatedResponse,
    limited_results: list[Any],
    api_page_size: int,
) -> PaginatedResponse:
    results_were_limited_by_client = len(limited_results) < len(original.results)
    api_returned_full_page = len(original.results) == api_page_size

    has_more_after_limit = original.has_more and not results_were_limited_by_client and api_returned_full_page

    return PaginatedResponse(
        results=limited_results,
        has_more=has_more_after_limit,
        next_cursor=original.next_cursor if has_more_after_limit else None,
    )


async def paginate_notion_api(
    api_call: Callable[..., Coroutine[Any, Any, PaginatedResponse]],
    total_results_limit: int | None = None,
    **kwargs,
) -> list[Any]:
    all_results = []
    async for page in _fetch_data(api_call, total_results_limit=total_results_limit, **kwargs):
        all_results.extend(page.results)
    return all_results


async def paginate_notion_api_generator(
    api_call: Callable[..., Coroutine[Any, Any, PaginatedResponse]],
    total_results_limit: int | None = None,
    **kwargs,
) -> AsyncGenerator[Any]:
    async for page in _fetch_data(api_call, total_results_limit=total_results_limit, **kwargs):
        for item in page.results:
            yield item
