# notionary/blocks/context/page_context.py
from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass
from contextvars import ContextVar

if TYPE_CHECKING:
    from notionary.database.client import NotionDatabaseClient
    from notionary.file_upload import NotionFileUploadClient


@dataclass(frozen=True)
class PageContextProvider:
    """Context object that provides dependencies for block conversion operations."""

    page_id: str
    database_client: NotionDatabaseClient
    file_upload_client: NotionFileUploadClient


# Context variable
_page_context: ContextVar[Optional[PageContextProvider]] = ContextVar(
    "page_context", default=None
)


def get_page_context() -> PageContextProvider:
    """Get current page context or raise if not available."""
    context = _page_context.get()
    if context is None:
        raise RuntimeError(
            "No page context available. Use 'async with page_context(...)'"
        )
    return context


def get_page_context_optional() -> Optional[PageContextProvider]:
    """Get current page context or None if not available."""
    return _page_context.get()


class page_context:
    """Async-only context manager for page operations."""

    def __init__(self, provider: PageContextProvider):
        self.provider = provider
        self._token = None

    def _set_context(self) -> PageContextProvider:
        """Helper to set context and return provider."""
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
