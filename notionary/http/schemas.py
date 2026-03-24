from typing import Any

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    results: list[Any]
    has_more: bool
    next_cursor: str | None
