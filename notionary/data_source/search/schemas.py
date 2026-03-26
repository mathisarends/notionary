from typing import ClassVar

from notionary.shared.search.schemas import (
    SearchQueryConfig,
    SortDirection,
    SortTimestamp,
)

__all__ = ["DataSourceQueryConfig", "SortDirection", "SortTimestamp"]


class DataSourceQueryConfig(SearchQueryConfig):
    _object_filter: ClassVar[str] = "data_source"
