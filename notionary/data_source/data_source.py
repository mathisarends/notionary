from __future__ import annotations

from typing import TYPE_CHECKING, Self

from notionary.data_source.data_source_factory import load_data_source_from_id, load_data_source_from_title
from notionary.shared.entity.entity import Entity
from notionary.shared.entity.entity_metadata_update_client import EntityMetadataUpdateClient

if TYPE_CHECKING:
    from notionary.database.database import NotionDatabase


class NotionDataSource(Entity):
    def __init__(
        self,
        id: str,
        title: str,
        created_time: str,
        last_edited_time: str,
        archived: bool,
        in_trash: bool,
        parent_database: NotionDatabase,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        description: str | None = None,
        properties: dict | None = None,
    ) -> None:
        super().__init__(
            id=id,
            created_time=created_time,
            last_edited_time=last_edited_time,
            in_trash=in_trash,
            emoji_icon=emoji_icon,
            external_icon_url=external_icon_url,
            cover_image_url=cover_image_url,
        )
        self._parent_database = parent_database
        self._title = title
        self._archived = archived
        self._description = description
        self._properties = properties or {}

    @classmethod
    async def from_id(cls, id: str) -> Self:
        return await load_data_source_from_id(id)

    @classmethod
    async def from_title(cls, title: str) -> Self:
        return await load_data_source_from_title(title)

    @property
    def _entity_metadata_update_client(self) -> EntityMetadataUpdateClient:
        raise NotImplementedError("Data source metadata update client not yet implemented")

    @property
    def title(self) -> str:
        return self._title

    @property
    def archived(self) -> bool:
        return self._archived

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def properties(self) -> dict:
        return self._properties

    @property
    def parent_database(self) -> NotionDatabase:
        return self._parent_database

    async def set_title(self, title: str) -> None:
        # TODO: Implement title update via metadata client
        self._title = title

    async def archive(self) -> None:
        if self._archived:
            self.logger.info("Data source is already archived.")
            return
        # TODO: Implement archive via metadata client
        self._archived = True

    async def unarchive(self) -> None:
        if not self._archived:
            self.logger.info("Data source is not archived.")
            return
        # TODO: Implement unarchive via metadata client
        self._archived = False
