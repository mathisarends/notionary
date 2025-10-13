from collections.abc import Awaitable, Callable

from notionary.blocks.rich_text.name_id_resolver import DataSourceNameIdResolver
from notionary.data_source.properties.models import (
    DataSourceMultiSelectProperty,
    DataSourceProperty,
    DataSourceRelationProperty,
    DataSourceSelectProperty,
    DataSourceStatusProperty,
)
from notionary.data_source.schema.registry import DatabasePropertyTypeDescriptorRegistry, PropertyTypeDescriptor
from notionary.shared.properties.type import PropertyType


class PropertyFormatter:
    INDENTATION = "   - "

    def __init__(
        self,
        relation_options_fetcher: Callable[[DataSourceRelationProperty], Awaitable[list[str]]],
        type_descriptor_registry: DatabasePropertyTypeDescriptorRegistry | None = None,
        data_source_resolver: DataSourceNameIdResolver | None = None,
    ) -> None:
        self._relation_options_fetcher = relation_options_fetcher
        self._type_descriptor_registry = type_descriptor_registry or DatabasePropertyTypeDescriptorRegistry()
        self._data_source_resolver = data_source_resolver or DataSourceNameIdResolver()

    async def format_property(self, prop: DataSourceProperty) -> list[str]:
        specific_details = await self._format_property_specific_details(prop)

        if specific_details:
            return [*specific_details, *self._format_custom_description(prop)]

        descriptor = self._type_descriptor_registry.get_descriptor(prop.type)
        return [*self._format_property_description(descriptor), *self._format_custom_description(prop)]

    def _format_property_description(self, descriptor: PropertyTypeDescriptor) -> list[str]:
        if not descriptor.description:
            return []
        return [f"{self.INDENTATION}{descriptor.description}"]

    async def _format_property_specific_details(self, prop: DataSourceProperty) -> list[str]:
        if isinstance(prop, DataSourceSelectProperty):
            return self._format_available_options("Choose one option from", prop.option_names)

        if isinstance(prop, DataSourceMultiSelectProperty):
            return self._format_available_options("Choose multiple options from", prop.option_names)

        if isinstance(prop, DataSourceStatusProperty):
            return self._format_available_options("Available statuses", prop.option_names)

        if isinstance(prop, DataSourceRelationProperty):
            return await self._format_relation_details(prop)

        return []

    def _format_custom_description(self, prop: DataSourceProperty) -> list[str]:
        if not prop.description:
            return []
        return [f"{self.INDENTATION}Description: {prop.description}"]

    def _format_available_options(self, label: str, options: list[str]) -> list[str]:
        options_text = ", ".join(options)
        return [f"{self.INDENTATION}{label}: {options_text}"]

    async def _format_relation_details(self, prop: DataSourceRelationProperty) -> list[str]:
        if not prop.related_data_source_id:
            return []

        data_source_name = await self._data_source_resolver.resolve_id_to_name(prop.related_data_source_id)
        data_source_display = data_source_name or prop.related_data_source_id
        lines = [f"{self.INDENTATION}Links to datasource: {data_source_display}"]

        available_entries = await self._fetch_relation_entries(prop)
        if available_entries:
            entries_text = ", ".join(available_entries)
            lines.append(f"{self.INDENTATION}Available entries: {entries_text}")

        return lines

    async def _fetch_relation_entries(self, prop: DataSourceRelationProperty) -> list[str] | None:
        try:
            return await self._relation_options_fetcher(prop)
        except Exception:
            return None


class NaturalLanguageSchemaFormatter:
    def __init__(
        self,
        relation_options_fetcher: Callable[[DataSourceRelationProperty], Awaitable[list[str]]] | None = None,
        data_source_resolver: DataSourceNameIdResolver | None = None,
    ) -> None:
        self._property_formatter = PropertyFormatter(
            relation_options_fetcher, data_source_resolver=data_source_resolver
        )

    async def format(self, title: str, description: str | None, properties: dict[str, DataSourceProperty]) -> str:
        lines = self._format_header(title, description)
        lines.append("Properties:")
        lines.append("")
        lines.extend(await self._format_properties(properties))

        return "\n".join(lines)

    def _format_header(self, title: str, description: str | None) -> list[str]:
        lines = [f"Data Source: {title}", ""]

        if description:
            lines.append(f"Description: {description}")
            lines.append("")

        return lines

    async def _format_properties(self, properties: dict[str, DataSourceProperty]) -> list[str]:
        lines = []
        sorted_properties = self._sort_with_title_first(properties)

        for index, (name, prop) in enumerate(sorted_properties, start=1):
            lines.extend(await self._format_single_property(index, name, prop))

        return lines

    def _sort_with_title_first(self, properties: dict[str, DataSourceProperty]) -> list[tuple[str, DataSourceProperty]]:
        return sorted(properties.items(), key=lambda item: (self._is_not_title_property(item[1]), item[0]))

    def _is_not_title_property(self, prop: DataSourceProperty) -> bool:
        return prop.type != PropertyType.TITLE

    async def _format_single_property(self, index: int, name: str, prop: DataSourceProperty) -> list[str]:
        lines = [f"{index}. - Property Name: '{name}'", f"   - Property Type: '{prop.type.value}'"]

        lines.extend(await self._property_formatter.format_property(prop))
        lines.append("")

        return lines
