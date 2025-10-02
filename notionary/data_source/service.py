from __future__ import annotations

import difflib
from typing import TYPE_CHECKING, Self

from notionary.data_source.factory import load_data_source_from_id, load_data_source_from_title
from notionary.data_source.http.data_source_instance_client import DataSourceInstanceClient
from notionary.data_source.properties.exceptions import DataSourcePropertyNotFound, DataSourcePropertyTypeError
from notionary.data_source.properties.models import (
    DataSourceMultiSelectProperty,
    DataSourceProperty,
    DataSourcePropertyOption,
    DataSourcePropertyT,
    DataSourceRelationProperty,
    DataSourceSelectProperty,
    DataSourceStatusProperty,
)
from notionary.page.page_models import NotionPageDto
from notionary.page.properties.page_property_models import PageTitleProperty
from notionary.shared.entity.entity import Entity
from notionary.shared.entity.entity_metadata_update_client import EntityMetadataUpdateClient

if TYPE_CHECKING:
    from notionary.database.service import NotionDatabase


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
        properties: dict[str, DataSourceProperty] | None = None,
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

        self._data_source_client = DataSourceInstanceClient(data_source_id=id)

    @classmethod
    async def from_id(cls, id: str) -> Self:
        return await load_data_source_from_id(id)

    @classmethod
    async def from_title(cls, title: str) -> Self:
        return await load_data_source_from_title(title)

    @property
    def _entity_metadata_update_client(self) -> EntityMetadataUpdateClient:
        return self._data_source_client

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

    async def create_blank_page(self, title: str | None = None) -> None:
        await self._data_source_client.create_blank_page(title=title)

    async def set_title(self, title: str) -> None:
        data_source_dto = await self._data_source_client.update_title(title)
        self._title = data_source_dto.title

    async def archive(self) -> None:
        if self._archived:
            self.logger.info("Data source is already archived.")
            return
        await self._data_source_client.archive()
        self._archived = True

    async def unarchive(self) -> None:
        if not self._archived:
            self.logger.info("Data source is not archived.")
            return
        await self._data_source_client.unarchive()
        self._archived = False

    async def update_description(self, description: str) -> None:
        self._description = await self._data_source_client.update_description(description)

    def get_property_type_by_name(self, property_name: str) -> str | None:
        prop = self._properties.get(property_name)
        if not prop:
            return None

        if isinstance(prop, dict):
            return prop.get("type")

        return prop.type

    async def get_options_for_property_by_name(self, property_name: str) -> list[str]:
        prop = self._properties.get(property_name)

        if prop is None:
            return []

        if isinstance(prop, DataSourceSelectProperty):
            return prop.option_names

        if isinstance(prop, DataSourceMultiSelectProperty):
            return prop.option_names

        if isinstance(prop, DataSourceStatusProperty):
            return prop.option_names

        if isinstance(prop, DataSourceRelationProperty):
            return await self._get_relation_options(prop)

        return []

    def get_select_options_by_property_name(self, property_name: str) -> list[str]:
        select_prop = self._get_typed_property(property_name, DataSourceSelectProperty)
        return select_prop.option_names

    def get_multi_select_options_by_property_name(self, property_name: str) -> list[DataSourcePropertyOption]:
        multi_select_prop = self._get_typed_property(property_name, DataSourceMultiSelectProperty)
        return multi_select_prop.option_names

    def get_status_options_by_property_name(self, property_name: str) -> list[str]:
        status_prop = self._get_typed_property(property_name, DataSourceStatusProperty)
        return status_prop.option_names

    async def get_relation_options_by_property_name(self, property_name: str) -> list[str]:
        relation_prop = self._get_typed_property(property_name, DataSourceRelationProperty)
        return await self._get_relation_options(relation_prop)

    async def _get_relation_options(self, relation_prop: DataSourceRelationProperty) -> list[str]:
        related_data_source_id = relation_prop.related_data_source_id
        if not related_data_source_id:
            return []

        async with DataSourceInstanceClient(related_data_source_id) as related_client:
            search_results = await related_client.query()

        page_titles = []
        for page_response in search_results.results:
            title = self._extract_title_from_notion_page_dto(page_response)
            if title:
                page_titles.append(title)

        return page_titles

    def _extract_title_from_notion_page_dto(self, page: NotionPageDto) -> str | None:
        if not page.properties:
            return None

        title_property = next(
            (prop for prop in page.properties.values() if isinstance(prop, PageTitleProperty)),
            None,
        )

        if not title_property:
            return None

        return "".join(item.plain_text for item in title_property.title)

    def _get_typed_property(self, name: str, property_type: type[DataSourcePropertyT]) -> DataSourcePropertyT:
        prop = self._properties.get(name)

        if prop is None:
            suggestions = self._find_closest_property_names(name)
            raise DataSourcePropertyNotFound(property_name=name, suggestions=suggestions)

        if not isinstance(prop, property_type):
            raise DataSourcePropertyTypeError(
                property_name=name, expected_type=property_type.__name__, actual_type=type(prop).__name__
            )

        return prop

    def _find_closest_property_names(self, property_name: str, max_matches: int = 5) -> list[str]:
        if not self._properties:
            return []

        keys = list(self._properties.keys())
        matches = difflib.get_close_matches(property_name, keys, n=max_matches, cutoff=0.6)
        return matches
