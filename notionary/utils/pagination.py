from collections.abc import Callable, Coroutine
from typing import Any

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    results: list[Any]
    has_more: bool
    next_cursor: str | None


async def paginate_notion_api(
    api_call: Callable[..., Coroutine[Any, Any, PaginatedResponse]],
    **kwargs,
) -> list[Any]:
    all_results = []
    next_cursor = None
    has_more = True

    while has_more:
        current_kwargs = kwargs.copy()
        if next_cursor:
            current_kwargs["start_cursor"] = next_cursor

        response = await api_call(**current_kwargs)

        if response and response.results:
            all_results.extend(response.results)

        has_more = response.has_more if response else False
        next_cursor = response.next_cursor if response else None

    return all_results
