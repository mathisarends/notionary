from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import ValidationError

from notionary.data_source.properties.schemas import (
    AnyDataSourceProperty,
    DataSourceMultiSelectProperty,
    DataSourceNumberProperty,
    DataSourceRelationProperty,
    DataSourceSelectProperty,
    DataSourceStatusProperty,
)
from notionary.data_source.properties.views import (
    DataSourcePropertyDescription,
    DataSourceRelationOption,
    RawDataSourceProperty,
)
from notionary.shared.properties.type import PropertyType


class DataSourceProperties:
    """Provides schema-aware operations for data source properties."""

    def __init__(self, properties: dict[str, AnyDataSourceProperty]) -> None:
        self._properties = properties

    def describe(self) -> dict[str, DataSourcePropertyDescription]:
        """Return normalized descriptions for all data source properties."""
        return {
            name: self._describe_property(name, prop)
            for name, prop in self._properties.items()
        }

    async def describe_with_relation_options(
        self,
        relation_options_resolver: Callable[
            [str],
            Awaitable[list[DataSourceRelationOption]],
        ],
    ) -> dict[str, DataSourcePropertyDescription]:
        """Describe properties and resolve relation options via a callback.

        The resolver receives a relation data source id and should return the
        natural-language options (e.g. page titles + ids) for that relation.
        """
        descriptions = self.describe()
        for description in descriptions.values():
            if str(description.type) != PropertyType.RELATION:
                continue

            if not description.relation_options:
                continue

            resolved_options: list[DataSourceRelationOption] = []
            for relation_option in description.relation_options:
                resolved_options.extend(
                    await relation_options_resolver(relation_option.id)
                )

            if resolved_options:
                description.relation_options = resolved_options

        return descriptions

    def _describe_property(
        self,
        name: str,
        prop: AnyDataSourceProperty,
    ) -> DataSourcePropertyDescription:
        match prop:
            case DataSourceStatusProperty():
                return DataSourcePropertyDescription(
                    type=prop.type,
                    options=prop.option_names,
                    groups=prop.group_names,
                )

            case DataSourceSelectProperty():
                return DataSourcePropertyDescription(
                    type=prop.type,
                    options=prop.option_names,
                )

            case DataSourceMultiSelectProperty():
                return DataSourcePropertyDescription(
                    type=prop.type,
                    options=prop.option_names,
                )

            case DataSourceNumberProperty():
                return DataSourcePropertyDescription(
                    type=prop.type,
                    format=prop.number_format,
                )

            case DataSourceRelationProperty():
                relation_options: list[DataSourceRelationOption] = []
                if prop.related_data_source_id is not None:
                    relation_options.append(
                        DataSourceRelationOption(
                            id=str(prop.related_data_source_id),
                            title=name,
                        )
                    )
                return DataSourcePropertyDescription(
                    type=prop.type,
                    relation_options=relation_options,
                )

            case _:
                return self._describe_from_raw(name, prop)

    def _describe_from_raw(
        self,
        name: str,
        prop: AnyDataSourceProperty,
    ) -> DataSourcePropertyDescription:
        raw = self._to_property_dict(prop)
        raw_type = raw.get("type", "unknown")

        try:
            parsed = RawDataSourceProperty.model_validate(raw)
        except ValidationError:
            return DataSourcePropertyDescription(type=raw_type)

        description = DataSourcePropertyDescription(type=parsed.type)
        parsed_type = str(parsed.type)

        if parsed_type == PropertyType.STATUS:
            if parsed.status is not None:
                description.options = [option.name for option in parsed.status.options]
                description.groups = [group.name for group in parsed.status.groups]
            return description

        if parsed_type == PropertyType.SELECT:
            if parsed.select is not None:
                description.options = [option.name for option in parsed.select.options]
            return description

        if parsed_type == PropertyType.MULTI_SELECT:
            if parsed.multi_select is not None:
                description.options = [
                    option.name for option in parsed.multi_select.options
                ]
            return description

        if parsed_type == PropertyType.NUMBER:
            if parsed.number is not None:
                description.format = parsed.number.format
            return description

        if parsed_type == PropertyType.RELATION:
            if parsed.relation is not None:
                relation_id = (
                    parsed.relation.data_source_id or parsed.relation.database_id
                )
                relation_title = (
                    parsed.relation.data_source_name
                    or parsed.relation.database_name
                    or name
                )
                if relation_id:
                    description.relation_options = [
                        DataSourceRelationOption(
                            id=relation_id,
                            title=relation_title,
                        )
                    ]
            return description

        return description

    @staticmethod
    def _to_property_dict(prop: AnyDataSourceProperty) -> dict[str, Any]:
        if hasattr(prop, "model_dump"):
            return prop.model_dump(mode="python")
        if isinstance(prop, dict):
            return prop
        return {}
