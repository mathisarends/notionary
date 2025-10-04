from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.database.client import NotionDatabaseHttpClient


@dataclass
class ConverterContext:
    """
    Context object that provides dependencies for block conversion operations.
    """

    page_id: str | None = None
    database_client: NotionDatabaseHttpClient | None = None

    def require_database_client(self) -> NotionDatabaseHttpClient:
        """Get database client or raise if not available."""
        if self.database_client is None:
            raise ValueError("Database client required but not provided in context")
        return self.database_client

    def require_page_id(self) -> str:
        """Get parent page ID or raise if not available."""
        if self.page_id is None:
            raise ValueError("Parent page ID required but not provided in context")
        return self.page_id
