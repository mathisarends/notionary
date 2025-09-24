from __future__ import annotations

from typing import TYPE_CHECKING

from notionary.database.database_http_client import NotionDatabseHttpClient
from notionary.page.page_models import NotionPageDto
from notionary.page.properties.page_property_models import PageTitleProperty
from notionary.shared.models.database_property_models import (
    DatabaseMultiSelectProperty,
    DatabasePropertyT,
    DatabaseRelationProperty,
    DatabaseSelectProperty,
    DatabaseStatusProperty,
)
from notionary.shared.models.shared_property_models import PropertyType

if TYPE_CHECKING:
    from notionary.database.database import NotionDatabase

# TODO: Wenn man sich hier die DatabaseProperties angucket könnte man sich überlegen ob man hier nicht auch sogar die detailed views hier abfragen wollte?
# Also mit Farbe und gruppen etc.


class DatabasePropertyReader:
    def __init__(self, database: NotionDatabase) -> None:
        self._database = database

    def get_property_type_by_name(self, property_name: str) -> str | None:
        prop = self._database.properties.get(property_name)
        if not prop:
            return None

        # This is for safety, should not be the case though
        if isinstance(prop, dict):
            return prop.get("type")

        return prop.type

    async def get_options_for_property_by_name(self, property_name: str) -> list[str]:
        prop = self._database.properties.get(property_name)

        if not prop:
            return []

        if prop.type in (
            PropertyType.SELECT,
            PropertyType.MULTI_SELECT,
            PropertyType.STATUS,
        ):
            return prop.option_names
        elif prop.type == PropertyType.RELATION:
            return await self._get_relation_options(prop)

        return []

    def get_select_options_by_property_name(self, property_name: str) -> list[str]:
        select_prop = self._get_select_property(property_name)
        if select_prop:
            return select_prop.option_names
        return []

    def _get_select_property(self, property_name: str) -> DatabaseSelectProperty | None:
        return self._get_database_property(property_name, DatabaseSelectProperty)

    def get_multi_select_options_by_property_name(self, property_name: str) -> list[str]:
        multi_select_prop = self._get_multi_select_property(property_name)
        if multi_select_prop:
            return multi_select_prop.option_names
        return []

    def _get_multi_select_property(self, property_name: str) -> DatabaseMultiSelectProperty | None:
        return self._get_database_property(property_name, DatabaseMultiSelectProperty)

    def get_status_options_by_property_name(self, property_name: str) -> list[str]:
        status_prop = self._get_status_property(property_name)
        if status_prop:
            return status_prop.option_names
        return []

    def _get_status_property(self, property_name: str) -> DatabaseStatusProperty | None:
        return self._get_database_property(property_name, DatabaseStatusProperty)

    async def get_relation_options_by_property_name(self, property_name: str) -> list[str]:
        relation_prop = self._get_relation_property(property_name)
        if relation_prop:
            return await self._get_relation_options(relation_prop)
        return []

    def _get_relation_property(self, property_name: str) -> DatabaseRelationProperty | None:
        return self._get_database_property(property_name, DatabaseRelationProperty)

    async def _get_relation_options(self, relation_prop: DatabaseRelationProperty) -> list[str]:
        related_db_id = relation_prop.related_database_id
        if not related_db_id:
            return []

        async with NotionDatabseHttpClient(database_id=related_db_id) as related_client:
            search_results = await related_client.query_database()

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

    def _get_database_property(self, name: str, property_type: type[DatabasePropertyT]) -> DatabasePropertyT | None:
        prop = self._database.properties.get(name)
        if isinstance(prop, property_type):
            return prop
        return None
