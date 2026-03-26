import os
from types import TracebackType
from typing import Self

from notionary.data_source import DataSourceNamespace
from notionary.database import DatabaseNamespace
from notionary.file_upload import FileUploads
from notionary.http import HttpClient
from notionary.page import PageNamespace
from notionary.user import UsersNamespace
from notionary.workspace import WorkspaceNamespace


class Notionary:
    """Async client for the Notion API.

    The API key is read from the ``NOTION_API_KEY`` environment variable
    when ``api_key`` is omitted.
    """

    def __init__(self, api_key: str | None = None) -> None:
        """
        Args:
            api_key: Notion integration token. Falls back to ``NOTION_API_KEY``.

        Raises:
            ValueError: If no API key is provided and ``NOTION_API_KEY`` is not set.
        """
        self._http = HttpClient(self._resolve_api_key(api_key))

        self.users = UsersNamespace(self._http)
        self.pages = PageNamespace(self._http)
        self.data_sources = DataSourceNamespace(self._http)
        self.databases = DatabaseNamespace(self._http)
        self.file_uploads = FileUploads(self._http)
        self.workspace = WorkspaceNamespace(self._http)

    def _resolve_api_key(self, api_key: str | None) -> str:
        resolved = api_key or os.getenv("NOTION_API_KEY")
        if not resolved:
            raise ValueError(
                "No Notion API key found. Pass api_key= or set NOTION_API_KEY."
            )
        return resolved

    async def close(self) -> None:
        """Close the underlying HTTP session and release all resources."""
        await self._http.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()
