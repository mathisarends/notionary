from typing import ClassVar

from notionary.shared.search.schemas import (
    SearchQueryConfig,
    SortDirection,
    SortTimestamp,
)

__all__ = ["PageQueryConfig", "SortDirection", "SortTimestamp"]


class PageQueryConfig(SearchQueryConfig):
    _object_filter: ClassVar[str] = "page"
