import logging
import os
from types import TracebackType
from typing import Self

from notionary.http import HttpClient
from notionary.namespaces.blocks import BlocksNamespace
from notionary.namespaces.databases import DatabasesNamespace
from notionary.namespaces.pages import PagesNamespace
from notionary.namespaces.workspace import WorkspaceNamespace

logger = logging.getLogger(__name__)


class Notionary:
    def __init__(self, token: str | None = None) -> None:
        self._http = HttpClient(token or self._resolve_token())

        self.pages = PagesNamespace(self._http)
        self.databases = DatabasesNamespace(self._http)
        self.blocks = BlocksNamespace(self._http)
        self.workspace = WorkspaceNamespace(self._http)

    def _resolve_token() -> str:
        token = os.getenv("NOTION_API_KEY")
        if not token:
            raise ValueError(
                "Notion token must be provided via NOTION_API_KEY environment variable"
            )
        return token

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
