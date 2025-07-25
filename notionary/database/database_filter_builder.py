from __future__ import annotations

from typing import Any, Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class FilterConfig:
    """Simple configuration for Notion Database filters."""

    conditions: List[Dict[str, Any]] = field(default_factory=list)
    page_size: int = 100

    def to_filter_dict(self) -> Dict[str, Any]:
        """Convert to a Notion filter dictionary."""
        if len(self.conditions) == 0:
            return {}
        if len(self.conditions) == 1:
            return self.conditions[0]

        return {"and": self.conditions}


class DatabaseFilterBuilder:
    """
    Builder class for creating complex Notion filters with comprehensive property type support.
    """

    def __init__(self, config: FilterConfig = None):
        self.config = config or FilterConfig()

    def with_page_object_filter(self):
        """Filter: Only page objects (Notion API search)."""
        self.config.conditions.append({"value": "page", "property": "object"})
        return self

    def with_database_object_filter(self):
        """Filter: Only database objects (Notion API search)."""
        self.config.conditions.append({"value": "database", "property": "object"})
        return self

    # TIMESTAMP FILTERS (Created/Updated)
    def with_created_after(self, date: datetime):
        """Add condition: created after specific date."""
        self.config.conditions.append(
            {"timestamp": "created_time", "created_time": {"after": date.isoformat()}}
        )
        return self

    def with_created_before(self, date: datetime):
        """Add condition: created before specific date."""
        self.config.conditions.append(
            {"timestamp": "created_time", "created_time": {"before": date.isoformat()}}
        )
        return self

    def with_updated_after(self, date: datetime):
        """Add condition: updated after specific date."""
        self.config.conditions.append(
            {
                "timestamp": "last_edited_time",
                "last_edited_time": {"after": date.isoformat()},
            }
        )
        return self

    def with_created_last_n_days(self, days: int):
        """Created in the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        return self.with_created_after(cutoff)

    def with_updated_last_n_hours(self, hours: int):
        """Updated in the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return self.with_updated_after(cutoff)

    # RICH TEXT FILTERS
    def with_text_contains(self, property_name: str, value: str):
        """Rich text contains value."""
        self.config.conditions.append(
            {"property": property_name, "rich_text": {"contains": value}}
        )
        return self

    def with_text_equals(self, property_name: str, value: str):
        """Rich text equals value."""
        self.config.conditions.append(
            {"property": property_name, "rich_text": {"equals": value}}
        )
        return self

    # TITLE FILTERS
    def with_title_contains(self, value: str):
        """Title contains value."""
        self.config.conditions.append(
            {"property": "title", "title": {"contains": value}}
        )
        return self

    def with_title_equals(self, value: str):
        """Title equals value."""
        self.config.conditions.append({"property": "title", "title": {"equals": value}})
        return self

    # SELECT FILTERS (Single Select)
    def with_select_equals(self, property_name: str, value: str):
        """Select equals value."""
        self.config.conditions.append(
            {"property": property_name, "select": {"equals": value}}
        )
        return self

    def with_select_is_empty(self, property_name: str):
        """Select is empty."""
        self.config.conditions.append(
            {"property": property_name, "select": {"is_empty": True}}
        )
        return self

    def with_multi_select_contains(self, property_name: str, value: str):
        """Multi-select contains value."""
        self.config.conditions.append(
            {"property": property_name, "multi_select": {"contains": value}}
        )
        return self

    def with_status_equals(self, property_name: str, value: str):
        """Status equals value."""
        self.config.conditions.append(
            {"property": property_name, "status": {"equals": value}}
        )
        return self

    def with_page_size(self, size: int):
        """Set page size for pagination."""
        self.config.page_size = size
        return self

    def with_or_condition(self, *builders):
        """Add OR condition with multiple sub-conditions."""
        or_conditions = []
        for builder in builders:
            filter_dict = builder.build()
            if filter_dict:
                or_conditions.append(filter_dict)

        if len(or_conditions) > 1:
            self.config.conditions.append({"or": or_conditions})
        elif len(or_conditions) == 1:
            self.config.conditions.append(or_conditions[0])

        return self

    def build(self) -> Dict[str, Any]:
        """Build the final filter dictionary."""
        return self.config.to_filter_dict()

    def get_config(self) -> FilterConfig:
        """Get the underlying FilterConfig."""
        return self.config

    def copy(self):
        """Create a copy of the builder."""
        new_config = FilterConfig(
            conditions=self.config.conditions.copy(), page_size=self.config.page_size
        )
        return DatabaseFilterBuilder(new_config)

    def reset(self):
        """Reset all conditions."""
        self.config = FilterConfig()
        return self
