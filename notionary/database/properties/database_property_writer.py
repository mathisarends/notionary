from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from notionary import NotionDatabase


class NotionDatbasePropertyWriter:
    def __init__(self, database: NotionDatabase) -> None:
        self._database = database
