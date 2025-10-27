import re
from uuid import UUID

from notionary.blocks.rich_text.name_id_resolver.page import PageNameIdResolver
from notionary.blocks.rich_text.name_id_resolver.person import PersonNameIdResolver
from notionary.data_source.query.schema import (
    CompoundFilter,
    DataSourceQueryParams,
    NotionFilter,
    PropertyFilter,
)
from notionary.shared.properties.type import PropertyType
from notionary.utils.mixins.logging import LoggingMixin


class QueryResolver(LoggingMixin):
    UUID_PATTERN = re.compile(
        r"^[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}$",
        re.IGNORECASE,
    )

    def __init__(
        self,
        user_resolver: PersonNameIdResolver | None = None,
        page_resolver: PageNameIdResolver | None = None,
    ):
        self._user_resolver = user_resolver or PersonNameIdResolver()
        self._page_resolver = page_resolver or PageNameIdResolver()

    async def resolve_params(
        self, params: DataSourceQueryParams
    ) -> DataSourceQueryParams:
        if not params.filter:
            return params

        resolved_filter = await self._resolve_filter(params.filter)
        return DataSourceQueryParams(filter=resolved_filter, sorts=params.sorts)

    async def _resolve_filter(self, filter: NotionFilter) -> NotionFilter:
        if isinstance(filter, PropertyFilter):
            return await self._resolve_property_filter(filter)
        elif isinstance(filter, CompoundFilter):
            return await self._resolve_compound_filter(filter)
        return filter

    async def _resolve_compound_filter(
        self, compound: CompoundFilter
    ) -> CompoundFilter:
        resolved_filters = []
        for filter in compound.filters:
            resolved = await self._resolve_filter(filter)
            resolved_filters.append(resolved)

        return CompoundFilter(operator=compound.operator, filters=resolved_filters)

    async def _resolve_property_filter(
        self, prop_filter: PropertyFilter
    ) -> PropertyFilter:
        if not self._is_resolvable_property_type(prop_filter.property_type):
            return prop_filter

        if prop_filter.value is None:
            return prop_filter

        if self._is_uuid(prop_filter.value):
            return prop_filter

        resolved_value = await self._resolve_value(
            prop_filter.value, prop_filter.property_type
        )

        return PropertyFilter(
            property=prop_filter.property,
            property_type=prop_filter.property_type,
            operator=prop_filter.operator,
            value=resolved_value,
        )

    def _is_resolvable_property_type(self, property_type: PropertyType) -> bool:
        return property_type in (PropertyType.PEOPLE, PropertyType.RELATION)

    def _is_uuid(self, value: str | int | float | bool | list) -> bool:
        if not isinstance(value, str):
            return False

        return self._is_standard_uuid(value) or self._is_notion_style_uuid(value)

    def _is_standard_uuid(self, value: str) -> bool:
        try:
            UUID(value)
            return True
        except (ValueError, AttributeError):
            return False

    def _is_notion_style_uuid(self, value: str) -> bool:
        return bool(self.UUID_PATTERN.match(value))

    async def _resolve_value(self, value: str, property_type: PropertyType) -> str:
        if property_type == PropertyType.PEOPLE:
            return await self._resolve_user_name_to_id(value)

        if property_type == PropertyType.RELATION:
            return await self._resolve_page_name_to_id(value)

        return value

    def _ensure_value_is_string(self, value: str | int | float | bool | list) -> None:
        if not isinstance(value, str):
            raise ValueError(f"Cannot resolve non-string value: {value}")

    async def _resolve_user_name_to_id(self, name: str) -> str:
        resolved = await self._user_resolver.resolve_name_to_id(name)

        if not resolved:
            raise ValueError(f"Could not resolve user name '{name}' to ID")

        return resolved

    async def _resolve_page_name_to_id(self, name: str) -> str:
        resolved = await self._page_resolver.resolve_name_to_id(name)

        if not resolved:
            raise ValueError(f"Could not resolve page name '{name}' to ID")

        return resolved
