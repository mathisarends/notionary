from typing import ClassVar

from notionary.shared.search.schemas import (
    SearchQueryConfig,
    SortDirection,
    SortTimestamp,
)

__all__ = ["DatabaseQueryConfig", "SortDirection", "SortTimestamp"]


class DatabaseQueryConfig(SearchQueryConfig):
    _object_filter: ClassVar[str] = "database"
