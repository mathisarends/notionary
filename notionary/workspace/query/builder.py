from typing import Self

from notionary.workspace.query.models import (
    SortDirection,
    SortTimestamp,
    WorkspaceQueryConfig,
    WorkspaceSearchObjectType,
)


class WorkspaceQueryConfigBuilder:
    def __init__(self, config: WorkspaceQueryConfig = None) -> None:
        self.config = config or WorkspaceQueryConfig()

    def with_query(self, query: str) -> Self:
        self.config.query = query
        return self

    def with_pages_only(self) -> Self:
        self.config.object_type = WorkspaceSearchObjectType.PAGE
        return self

    def with_data_sources_only(self) -> Self:
        self.config.object_type = WorkspaceSearchObjectType.DATA_SOURCE
        return self

    def with_sort_direction(self, direction: SortDirection) -> Self:
        self.config.sort_direction = direction
        return self

    def with_sort_ascending(self) -> Self:
        return self.with_sort_direction(SortDirection.ASCENDING)

    def with_sort_descending(self) -> Self:
        return self.with_sort_direction(SortDirection.DESCENDING)

    def with_sort_timestamp(self, timestamp: SortTimestamp) -> Self:
        self.config.sort_timestamp = timestamp
        return self

    def with_sort_by_created_time(self) -> Self:
        return self.with_sort_timestamp(SortTimestamp.CREATED_TIME)

    def with_sort_by_last_edited(self) -> Self:
        return self.with_sort_timestamp(SortTimestamp.LAST_EDITED_TIME)

    def with_page_size(self, size: int) -> Self:
        self.config.page_size = min(size, 100)
        return self

    def with_start_cursor(self, cursor: str | None) -> Self:
        self.config.start_cursor = cursor
        return self

    def without_cursor(self) -> Self:
        self.config.start_cursor = None
        return self

    def build(self) -> WorkspaceQueryConfig:
        return self.config
