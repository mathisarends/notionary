import os
from types import TracebackType
from typing import Self

from notionary.data_source import DataSourceNamespace
from notionary.database import DatabaseNamespace
from notionary.file_upload import FileUploads
from notionary.http import HttpClient
from notionary.page import PageNamespace
from notionary.user import UsersNamespace


class Notionary:
    def __init__(self, api_key: str | None = None) -> None:
        self._http = HttpClient(self._resolve_api_key(api_key))

        self.users = UsersNamespace(self._http)
        self.pages = PageNamespace(self._http)
        self.data_sources = DataSourceNamespace(self._http)
        self.databases = DatabaseNamespace(self._http)
        self.file_uploads = FileUploads(self._http)

    def _resolve_api_key(self, api_key: str | None) -> str:
        resolved = api_key or os.getenv("NOTION_API_KEY")
        if not resolved:
            raise ValueError(
                "No Notion API key found. Pass api_key= or set NOTION_API_KEY."
            )
        return resolved

    async def close(self) -> None:
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
