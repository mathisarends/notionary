from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.workspace import NotionWorkspace


class BaseNameIdResolver:
    def __init__(
        self,
        *,
        workspace: NotionWorkspace | None = None,
        search_limit: int = 10,
    ):
        if workspace is None:
            from notionary import NotionWorkspace

            workspace = NotionWorkspace()

        self.workspace = workspace
        self.search_limit = search_limit
