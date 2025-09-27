from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from notionary import NotionDatabase, NotionPage
    from notionary.database.database_models import NotionQueryDatabaseResponse
    from notionary.page.page_models import NotionPageDto


@dataclass
class FilterConfig:
    conditions: list[dict[str, Any]] = field(default_factory=list)
    page_size: int = 100

    def to_filter_dict(self) -> dict[str, Any]:
        if len(self.conditions) == 0:
            return {}
        if len(self.conditions) == 1:
            return self.conditions[0]

        return {"and": self.conditions}


class DatabaseFilterBuilder:
    def __init__(self, config: FilterConfig = None, database: NotionDatabase = None) -> None:
        self.config = config or FilterConfig()
        self._database = database

    def page_object_filter(self) -> Self:
        self.config.conditions.append({"value": "page", "property": "object"})
        return self

    def database_object_filter(self) -> Self:
        self.config.conditions.append({"value": "database", "property": "object"})
        return self

    def created_after(self, date: datetime) -> Self:
        self.config.conditions.append({"timestamp": "created_time", "created_time": {"after": date.isoformat()}})
        return self

    def created_before(self, date: datetime) -> Self:
        self.config.conditions.append({"timestamp": "created_time", "created_time": {"before": date.isoformat()}})
        return self

    def updated_after(self, date: datetime) -> Self:
        self.config.conditions.append(
            {
                "timestamp": "last_edited_time",
                "last_edited_time": {"after": date.isoformat()},
            }
        )
        return self

    def created_last_days(self, days: int) -> Self:
        cutoff = datetime.now() - timedelta(days=days)
        return self.created_after(cutoff)

    def updated_last_hours(self, hours: int) -> Self:
        cutoff = datetime.now() - timedelta(hours=hours)
        return self.updated_after(cutoff)

    def text_contains(self, property_name: str, value: str) -> Self:
        self.config.conditions.append({"property": property_name, "rich_text": {"contains": value}})
        return self

    def text_equals(self, property_name: str, value: str) -> Self:
        self.config.conditions.append({"property": property_name, "rich_text": {"equals": value}})
        return self

    def title_contains(self, value: str) -> Self:
        self.config.conditions.append({"property": "title", "title": {"contains": value}})
        return self

    def title_equals(self, value: str) -> Self:
        self.config.conditions.append({"property": "title", "title": {"equals": value}})
        return self

    def select_equals(self, property_name: str, value: str) -> Self:
        self.config.conditions.append({"property": property_name, "select": {"equals": value}})
        return self

    def select_is_empty(self, property_name: str) -> Self:
        self.config.conditions.append({"property": property_name, "select": {"is_empty": True}})
        return self

    def multi_select_contains(self, property_name: str, value: str) -> Self:
        self.config.conditions.append({"property": property_name, "multi_select": {"contains": value}})
        return self

    def status_equals(self, property_name: str, value: str) -> Self:
        self.config.conditions.append({"property": property_name, "status": {"equals": value}})
        return self

    def page_size(self, size: int) -> Self:
        self.config.page_size = size
        return self

    def or_condition_with_builders(self, *builders) -> Self:
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

    def or_condition(self, *conditions: Callable[[DatabaseFilterBuilder], None]) -> Self:
        if not self._database:
            raise ValueError("OR conditions require database context. Use database.filter() first.")

        builders = []
        for condition in conditions:
            temp_builder = DatabaseFilterBuilder(database=self._database)
            condition(temp_builder)
            builders.append(temp_builder)

        return self.or_condition_with_builders(*builders)

    # === EXECUTION METHODS ===

    def _ensure_database(self) -> NotionDatabase:
        if self._database is None:
            raise ValueError("Database not set. Use database.filter() to create executable queries.")
        return self._database

    async def execute(self) -> AsyncGenerator[NotionPage]:
        """Execute the query and yield pages one by one"""
        filter_conditions = self.build()
        async for page in self._iter_pages(self.config.page_size, filter_conditions):
            yield page

    async def to_list(self) -> list[NotionPage]:
        """Convert all results to a list"""
        result = []
        async for page in self.execute():
            result.append(page)
        return result

    async def first(self) -> NotionPage | None:
        """Get the first matching page"""
        async for page in self.execute():
            return page
        return None

    async def count(self) -> int:
        """Count matching pages"""
        count = 0
        async for _ in self.execute():
            count += 1
        return count

    async def exists(self) -> bool:
        """Check if any pages match the query"""
        async for _ in self.execute():
            return True
        return False

    async def take(self, limit: int) -> list[NotionPage]:
        """Take only the first N results"""
        result = []
        count = 0
        async for page in self.execute():
            if count >= limit:
                break
            result.append(page)
            count += 1
        return result

    # === PAGINATION LOGIC (moved from Database) ===

    async def _iter_pages(
        self,
        page_size: int = 100,
        filter_conditions: dict[str, Any] | None = None,
    ) -> AsyncGenerator[NotionPage]:
        """Iterate over pages using the database's pagination"""
        self._ensure_database()

        async for batch in self._paginate_database(page_size, filter_conditions):
            for page_response in batch:
                # Import here to avoid circular imports
                from notionary.page.page import NotionPage

                yield await NotionPage.from_id(page_response.id)

    async def _paginate_database(
        self,
        page_size: int = 100,
        filter_conditions: dict[str, Any] | None = None,
    ) -> AsyncGenerator[list[NotionPageDto]]:
        """Central pagination logic for Notion Database queries"""
        database = self._ensure_database()
        start_cursor: str | None = None
        has_more = True

        while has_more:
            query_data: dict[str, Any] = {"page_size": page_size}

            if start_cursor:
                query_data["start_cursor"] = start_cursor
            if filter_conditions:
                query_data["filter"] = filter_conditions

            result: NotionQueryDatabaseResponse = await database.client.query_database(query_data=query_data)

            if not result or not result.results:
                return

            yield result.results

            has_more = result.has_more
            start_cursor = result.next_cursor if has_more else None

    def build(self) -> dict[str, Any]:
        return self.config.to_filter_dict()

    def get_config(self) -> FilterConfig:
        return self.config

    def copy(self) -> DatabaseFilterBuilder:
        new_config = FilterConfig(conditions=self.config.conditions.copy(), page_size=self.config.page_size)
        return DatabaseFilterBuilder(new_config, self._database)

    def reset(self) -> Self:
        self.config = FilterConfig()
        return self
