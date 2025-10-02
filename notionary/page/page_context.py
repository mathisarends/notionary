from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.database.database_http_client import NotionDatabaseHttpClient
    from notionary.file_upload import FileUploadHttpClient


@dataclass(frozen=True)
class PageContextProvider:
    """Context object that provides dependencies for block conversion operations."""

    page_id: str
    database_client: NotionDatabaseHttpClient
    file_upload_client: FileUploadHttpClient


# Context variable
_page_context: ContextVar[PageContextProvider | None] = ContextVar("page_context", default=None)


def get_page_context() -> PageContextProvider:
    """Get current page context or raise if not available."""
    context = _page_context.get()
    if context is None:
        raise RuntimeError("No page context available. Use 'async with page_context(...)'")
    return context


class page_context:
    def __init__(self, provider: PageContextProvider) -> None:
        self.provider = provider
        self._token = None

    def _set_context(self) -> PageContextProvider:
        self._token = _page_context.set(self.provider)
        return self.provider

    def _reset_context(self) -> None:
        """Helper to reset context."""
        if self._token is not None:
            _page_context.reset(self._token)

    async def __aenter__(self) -> PageContextProvider:
        return self._set_context()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._reset_context()
        return False
