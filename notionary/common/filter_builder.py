from __future__ import annotations

from typing import Any, Dict, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class FilterConfig:
    """Einfache Konfiguration für Notion Database Filter."""

    conditions: List[Dict[str, Any]] = field(default_factory=list)
    page_size: int = 100

    def to_filter_dict(self) -> Dict[str, Any]:
        """Konvertiert zu einem Notion-Filter-Dictionary."""
        if len(self.conditions) == 0:
            return {}
        if len(self.conditions) == 1:
            return self.conditions[0]

        return {"and": self.conditions}


class FilterBuilder:
    """
    Builder class for creating complex Notion filters with comprehensive property type support.
    """

    def __init__(self, config: FilterConfig = None):
        self.config = config or FilterConfig()

    # TIMESTAMP FILTERS (Created/Updated)
    def with_created_after(self, date: datetime) -> FilterBuilder:
        """Add condition: created after specific date."""
        self.config.conditions.append(
            {"timestamp": "created_time", "created_time": {"after": date.isoformat()}}
        )
        return self

    def with_created_before(self, date: datetime) -> FilterBuilder:
        """Add condition: created before specific date."""
        self.config.conditions.append(
            {"timestamp": "created_time", "created_time": {"before": date.isoformat()}}
        )
        return self

    def with_updated_after(self, date: datetime) -> FilterBuilder:
        """Add condition: updated after specific date."""
        self.config.conditions.append(
            {
                "timestamp": "last_edited_time",
                "last_edited_time": {"after": date.isoformat()},
            }
        )
        return self

    def with_created_last_n_days(self, days: int) -> FilterBuilder:
        """In den letzten N Tagen erstellt."""
        cutoff = datetime.now() - timedelta(days=days)
        return self.with_created_after(cutoff)

    def with_updated_last_n_hours(self, hours: int) -> FilterBuilder:
        """In den letzten N Stunden bearbeitet."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return self.with_updated_after(cutoff)

    # RICH TEXT FILTERS
    def with_text_contains(self, property_name: str, value: str) -> FilterBuilder:
        """Rich text contains value."""
        self.config.conditions.append(
            {"property": property_name, "rich_text": {"contains": value}}
        )
        return self

    def with_text_equals(self, property_name: str, value: str) -> FilterBuilder:
        """Rich text equals value."""
        self.config.conditions.append(
            {"property": property_name, "rich_text": {"equals": value}}
        )
        return self

    # TITLE FILTERS
    def with_title_contains(self, value: str) -> FilterBuilder:
        """Title contains value."""
        self.config.conditions.append(
            {"property": "title", "title": {"contains": value}}
        )
        return self

    def with_title_equals(self, value: str) -> FilterBuilder:
        """Title equals value."""
        self.config.conditions.append({"property": "title", "title": {"equals": value}})
        return self

    # SELECT FILTERS (Single Select)
    def with_select_equals(self, property_name: str, value: str) -> FilterBuilder:
        """Select equals value."""
        self.config.conditions.append(
            {"property": property_name, "select": {"equals": value}}
        )
        return self

    def with_select_is_empty(self, property_name: str) -> FilterBuilder:
        """Select is empty."""
        self.config.conditions.append(
            {"property": property_name, "select": {"is_empty": True}}
        )
        return self

    def with_multi_select_contains(
        self, property_name: str, value: str
    ) -> FilterBuilder:
        """Multi-select contains value."""
        self.config.conditions.append(
            {"property": property_name, "multi_select": {"contains": value}}
        )
        return self

    def with_status_equals(self, property_name: str, value: str) -> FilterBuilder:
        """Status equals value."""
        self.config.conditions.append(
            {"property": property_name, "status": {"equals": value}}
        )
        return self

    def with_page_size(self, size: int) -> FilterBuilder:
        """Set page size for pagination."""
        self.config.page_size = size
        return self

    def with_or_condition(self, *builders: FilterBuilder) -> FilterBuilder:
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

    def copy(self) -> FilterBuilder:
        """Create a copy of the builder."""
        new_config = FilterConfig(
            conditions=self.config.conditions.copy(), page_size=self.config.page_size
        )
        return FilterBuilder(new_config)

    def reset(self) -> FilterBuilder:
        """Reset all conditions."""
        self.config = FilterConfig()
        return self
