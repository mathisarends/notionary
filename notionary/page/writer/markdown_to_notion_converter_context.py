# notionary/blocks/context/conversion_context.py
from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from notionary.database.database_http_client import NotionDatabseHttpClient


@dataclass
class ConverterContext:
    """
    Context object that provides dependencies for block conversion operations.
    """

    page_id: Optional[str] = None
    database_client: Optional["NotionDatabseHttpClient"] = None

    def require_database_client(self) -> NotionDatabseHttpClient:
        """Get database client or raise if not available."""
        if self.database_client is None:
            raise ValueError("Database client required but not provided in context")
        return self.database_client

    def require_page_id(self) -> str:
        """Get parent page ID or raise if not available."""
        if self.page_id is None:
            raise ValueError("Parent page ID required but not provided in context")
        return self.page_id
