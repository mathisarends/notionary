from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional


@dataclass
class SearchConfig:
    """Konfiguration für Notion Search API Filter."""

    query: Optional[str] = None
    object_type: Optional[Literal["page", "database"]] = None
    sort_direction: Literal["ascending", "descending"] = "descending"
    sort_timestamp: Literal["last_edited_time", "created_time"] = "last_edited_time"
    page_size: int = 100
    start_cursor: Optional[str] = None

    def to_search_dict(self) -> Dict[str, Any]:
        """Konvertiert zu einem Notion Search API Dictionary."""
        search_dict = {}

        if self.query:
            search_dict["query"] = self.query

        if self.object_type:
            search_dict["filter"] = {"property": "object", "value": self.object_type}

        search_dict["sort"] = {
            "direction": self.sort_direction,
            "timestamp": self.sort_timestamp,
        }

        search_dict["page_size"] = min(self.page_size, 100)

        if self.start_cursor:
            search_dict["start_cursor"] = self.start_cursor

        return search_dict


class SearchFilterBuilder:
    """
    Builder class for creating Notion Search API filters with comprehensive options.
    """

    def __init__(self, config: SearchConfig = None):
        self.config = config or SearchConfig()

    def with_query(self, query: str) -> SearchFilterBuilder:
        """Set the search query string."""
        self.config.query = query
        return self

    def with_pages_only(self) -> SearchFilterBuilder:
        """Filter to only return pages."""
        self.config.object_type = "page"
        return self

    def with_databases_only(self) -> SearchFilterBuilder:
        """Filter to only return databases."""
        self.config.object_type = "database"
        return self

    def with_sort_direction(
        self, direction: Literal["ascending", "descending"]
    ) -> SearchFilterBuilder:
        """Set sort direction (ascending or descending)."""
        self.config.sort_direction = direction
        return self

    def with_sort_ascending(self) -> SearchFilterBuilder:
        """Sort results in ascending order."""
        return self.with_sort_direction("ascending")

    def with_sort_descending(self) -> SearchFilterBuilder:
        """Sort results in descending order."""
        return self.with_sort_direction("descending")

    def with_sort_timestamp(
        self, timestamp: Literal["last_edited_time", "created_time"]
    ) -> SearchFilterBuilder:
        """Set the timestamp field to sort by."""
        self.config.sort_timestamp = timestamp
        return self

    def with_sort_by_created_time(self) -> SearchFilterBuilder:
        """Sort by creation time."""
        return self.with_sort_timestamp("created_time")

    def with_sort_by_last_edited(self) -> SearchFilterBuilder:
        """Sort by last edited time."""
        return self.with_sort_timestamp("last_edited_time")

    def with_page_size(self, size: int) -> SearchFilterBuilder:
        """Set page size for pagination (max 100)."""
        self.config.page_size = min(size, 100)
        return self

    def with_cursor(self, cursor: Optional[str]) -> SearchFilterBuilder:
        """Set start cursor for pagination."""
        self.config.start_cursor = cursor
        return self

    def without_cursor(self) -> SearchFilterBuilder:
        """Remove start cursor (for first page)."""
        self.config.start_cursor = None
        return self

    def build(self) -> Dict[str, Any]:
        """Build the final search filter dictionary. Builder bleibt wiederverwendbar!"""
        return self.config.to_search_dict()

    def get_config(self) -> SearchConfig:
        """Get the underlying SearchConfig."""
        return self.config

    def copy(self) -> SearchFilterBuilder:
        """Create a copy of the builder."""
        new_config = SearchConfig(
            query=self.config.query,
            object_type=self.config.object_type,
            sort_direction=self.config.sort_direction,
            sort_timestamp=self.config.sort_timestamp,
            page_size=self.config.page_size,
            start_cursor=self.config.start_cursor,
        )
        return SearchFilterBuilder(new_config)

    def reset(self) -> SearchFilterBuilder:
        """Reset all configurations to defaults."""
        self.config = SearchConfig()
        return self
