from __future__ import annotations

from notionary.data_source.http.data_source_instance_client import DataSourceInstanceClient
from notionary.data_source.properties.data_source_property_models import (
    DataSourceMultiSelectProperty,
    DataSourceNotionProperty,
    DataSourcePropertyOption,
    DataSourcePropertyT,
    DataSourceRelationProperty,
    DataSourceSelectProperty,
    DataSourceStatusProperty,
    EnrichedDataSourceStatusOption,
)
from notionary.page.page_models import NotionPageDto
from notionary.page.properties.page_property_models import PageTitleProperty
from notionary.shared.models.shared_property_models import PropertyType


class DataSourcePropertyReader:
    def __init__(self, properties: dict[str, DataSourceNotionProperty]) -> None:
        self._properties = properties

    def get_property_type_by_name(self, property_name: str) -> str | None:
        prop = self._properties.get(property_name)
        if not prop:
            return None

        if isinstance(prop, dict):
            return prop.get("type")

        return prop.type

    async def get_options_for_property_by_name(self, property_name: str) -> list[str]:
        prop = self._properties.get(property_name)

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
        select_prop = self._get_typed_database_property(property_name, DataSourceSelectProperty)
        if select_prop:
            return select_prop.option_names

    def get_multi_select_options_by_property_name(self, property_name: str) -> list[DataSourcePropertyOption]:
        multi_select_prop = self._get_typed_database_property(property_name, DataSourceMultiSelectProperty)
        if multi_select_prop:
            return multi_select_prop.option_names
        return []

    def get_detailed_multi_select_options_by_property_name(self, property_name: str) -> list[DataSourceSelectProperty]:
        multi_select_prop = self._get_typed_database_property(property_name, DataSourceMultiSelectProperty)
        if multi_select_prop:
            return multi_select_prop.multi_select.options
        return []

    def get_status_options_by_property_name(self, property_name: str) -> list[str]:
        status_prop = self._get_typed_database_property(property_name, DataSourceStatusProperty)
        if status_prop:
            return status_prop.option_names
        return []

    def get_detailed_status_options_by_property_name(self, property_name: str) -> list[EnrichedDataSourceStatusOption]:
        status_prop = self._get_typed_database_property(property_name, DataSourceStatusProperty)
        if status_prop:
            return status_prop.status.detailed_options
        return []

    async def get_relation_options_by_property_name(self, property_name: str) -> list[str]:
        relation_prop = self._get_typed_database_property(property_name, DataSourceRelationProperty)
        if relation_prop:
            return await self._get_relation_options(relation_prop)
        return []

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

    def _get_typed_database_property(
        self, name: str, property_type: type[DataSourcePropertyT]
    ) -> DataSourcePropertyT | None:
        prop = self._properties.get(name)
        if isinstance(prop, property_type):
            return prop
        return None
