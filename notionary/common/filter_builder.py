from __future__ import annotations

from typing import Any, Dict, List
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
    Builder class for creating complex Notion filters with with_* naming convention.
    """

    def __init__(self, config: FilterConfig = None):
        self.config = config or FilterConfig()

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

    def with_page_size(self, size: int) -> FilterBuilder:
        """Set page size for pagination."""
        self.config.page_size = size
        return self

    def build(self) -> Dict[str, Any]:
        """Build the final filter dictionary."""
        return self.config.to_filter_dict()

    def get_config(self) -> FilterConfig:
        """Get the underlying FilterConfig."""
        return self.config

    def copy(self) -> FilterBuilder:
        """Create a copy of the builder. (e.g. for extending base filter)"""
        new_config = FilterConfig(
            conditions=self.config.conditions.copy(), page_size=self.config.page_size
        )
        return FilterBuilder(new_config)

    def reset(self) -> FilterBuilder:
        """Reset all conditions."""
        self.config = FilterConfig()
        return self
