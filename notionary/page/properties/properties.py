from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from notionary.http import HttpClient
from notionary.page.properties.client import PagePropertyHttpClient
from notionary.page.properties.schemas import (
    AnyPageProperty,
    DateValue,
    PageCheckboxProperty,
    PageDateProperty,
    PageEmailProperty,
    PageMultiSelectProperty,
    PageNumberProperty,
    PagePhoneNumberProperty,
    PageProperty,
    PageRelationProperty,
    PageRichTextProperty,
    PageSelectProperty,
    PageStatusProperty,
    PageTitleProperty,
    PageURLProperty,
    RelationItem,
    SelectOption,
    StatusOption,
)
from notionary.rich_text import RichText, rich_text_to_markdown


class PageProperties:
    """Read/write access to a Notion page's properties."""

    _SETTABLE_TYPES = frozenset(
        {
            "checkbox",
            "date",
            "email",
            "multi_select",
            "number",
            "phone_number",
            "rich_text",
            "select",
            "status",
            "title",
            "url",
        }
    )

    def __init__(
        self,
        id: UUID,
        properties: dict[str, AnyPageProperty],
        http: HttpClient,
        data_source_id: UUID | None = None,
    ) -> None:
        self.properties = properties
        self._http = http
        self._data_source_id = data_source_id
        self._data_source_option_names: dict[str, list[str]] | None = None
        self._property_http_client = PagePropertyHttpClient(page_id=id, http=http)

    async def set(
        self,
        name: str,
        value: str | int | float | bool | list[str] | None,
    ) -> None:
        """Agent-friendly property setter — resolves type and validates automatically.

        Args:
            name: Property name as it appears in Notion.
            value: The plain value to set. Type is validated against the schema.

        Raises:
            ValueError: If *name* is unknown, the value is an invalid option,
                or the property type is not supported.
            TypeError: If *value* has the wrong Python type for the property.
        """
        await self.set_property(name, value)

    async def set_property(self, name: str, value: Any) -> None:
        """Set a single page property by name.

        Args:
            name: Property name as it appears in Notion.
            value: New value for the property.
        """
        prop = self._require_property(name)
        normalized = await self._normalize_value(name, prop, value)
        built = self._build_property(prop, normalized)
        dto = await self._property_http_client.set_property(name, built)
        self._sync_properties(dto.properties)

    async def set_properties(self, values: dict[str, Any]) -> None:
        """Set multiple page properties in a single API request.

        Args:
            values: Mapping of property names to values.
        """
        built_properties: dict[str, PageProperty] = {}
        for name, value in values.items():
            prop = self._require_property(name)
            normalized = await self._normalize_value(name, prop, value)
            built_properties[name] = self._build_property(prop, normalized)

        dto = await self._property_http_client.set_properties(built_properties)
        self._sync_properties(dto.properties)

    async def set_title(self, title: str) -> None:
        """Set the page title.

        Raises:
            KeyError: If the page has no title property.
        """
        name = next(
            (k for k, p in self.properties.items() if isinstance(p, PageTitleProperty)),
            None,
        )
        if name is None:
            raise KeyError("No title property found on this page.")
        await self.set_property(name, title)

    def describe(self) -> dict[str, dict[str, Any]]:
        """Return a structured schema description of all properties.

        Designed for LLM context injection — each entry contains the property
        type, its current value (when available), and valid options for
        constrained types like status/select.
        """
        result: dict[str, dict[str, Any]] = {}
        for name, prop in self.properties.items():
            entry: dict[str, Any] = {"type": prop.type}

            match prop:
                case PageTitleProperty():
                    entry["current"] = rich_text_to_markdown(prop.title) or None

                case PageRichTextProperty():
                    entry["current"] = rich_text_to_markdown(prop.rich_text) or None

                case PageNumberProperty():
                    entry["current"] = prop.number

                case PageCheckboxProperty():
                    entry["current"] = prop.checkbox

                case PageDateProperty():
                    entry["current"] = prop.date.start if prop.date else None

                case PageSelectProperty():
                    entry["current"] = prop.select.name if prop.select else None
                    entry["options"] = self._known_option_names(name)

                case PageMultiSelectProperty():
                    entry["current"] = [o.name for o in prop.multi_select]
                    entry["options"] = self._known_option_names(name)

                case PageStatusProperty():
                    entry["current"] = prop.status.name if prop.status else None
                    entry["options"] = self._known_option_names(name)

                case PageRelationProperty():
                    ids = self._relation_ids(prop)
                    entry["current"] = ids
                    entry["options"] = ids

            result[name] = entry
        return result

    async def _normalize_value(
        self, name: str, prop: AnyPageProperty, value: Any
    ) -> Any:
        match prop:
            case PageStatusProperty() | PageSelectProperty():
                return await self._normalize_single_option(name, value)
            case PageMultiSelectProperty():
                return await self._normalize_multi_option(name, value)
            case PageNumberProperty():
                return self._normalize_number(name, value)
            case PageCheckboxProperty():
                return self._normalize_checkbox(name, value)
            case PageDateProperty():
                return self._normalize_date(name, value)
            case PageTitleProperty() | PageRichTextProperty():
                return self._normalize_text(name, value)
            case PageRelationProperty():
                return self._normalize_relation(name, prop, value)
            case _:
                if prop.type in self._SETTABLE_TYPES:
                    return value
                raise ValueError(
                    f"Property {name!r} has type {prop.type!r} which is not supported by set(). "
                    "Use set_property() directly."
                )

    async def _normalize_single_option(self, name: str, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"Property {name!r} expects a string, got {type(value).__name__}"
            )
        valid = await self._option_names_for(name)
        self._validate_option(name, value, valid)
        return value

    async def _normalize_multi_option(self, name: str, value: Any) -> list[str]:
        items: list[Any] = value if isinstance(value, list) else [value]
        valid = await self._option_names_for(name)
        for item in items:
            if not isinstance(item, str):
                raise TypeError(
                    f"Property {name!r} expects strings, got {type(item).__name__}"
                )
            self._validate_option(name, item, valid)
        return items

    @staticmethod
    def _normalize_number(name: str, value: Any) -> int | float:
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"Property {name!r} expects a number, got {type(value).__name__}: {value!r}"
            )
        return value

    @staticmethod
    def _normalize_checkbox(name: str, value: Any) -> bool:
        if not isinstance(value, bool):
            raise TypeError(
                f"Property {name!r} expects a bool, got {type(value).__name__}: {value!r}"
            )
        return value

    @staticmethod
    def _normalize_date(name: str, value: Any) -> Any:
        if isinstance(value, Mapping):
            if not isinstance(value.get("start"), str):
                raise TypeError(
                    f"Property {name!r} expects a date mapping with a string 'start' field."
                )
            return value
        if not isinstance(value, str):
            raise TypeError(
                f"Property {name!r} expects an ISO date string, got {type(value).__name__}"
            )
        return value

    @staticmethod
    def _normalize_text(name: str, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"Property {name!r} expects a string, got {type(value).__name__}"
            )
        return value

    def _normalize_relation(
        self, name: str, prop: PageRelationProperty, value: Any
    ) -> list[str]:
        available_ids = self._relation_ids(prop)

        if isinstance(value, str):
            relation_ids = [value]
        elif isinstance(value, list):
            relation_ids = value
        else:
            raise TypeError(
                f"Property {name!r} expects a relation page id string or list[str], "
                f"got {type(value).__name__}. Available ids: {available_ids}"
            )

        for rid in relation_ids:
            if not isinstance(rid, str):
                raise TypeError(
                    f"Property {name!r} expects relation ids as strings, "
                    f"got {type(rid).__name__}. Available ids: {available_ids}"
                )
            if not rid.strip():
                raise ValueError(
                    f"Property {name!r}: relation page id cannot be empty. "
                    f"Available ids: {available_ids}"
                )
            if not self._is_uuid_like(rid) and rid not in available_ids:
                raise ValueError(
                    f"Property {name!r}: {rid!r} is not a valid relation page id. "
                    f"Use a UUID-like id. Available ids: {available_ids}"
                )
        return relation_ids

    @staticmethod
    def _build_property(prop: AnyPageProperty, value: Any) -> PageProperty:
        match prop:
            case PageTitleProperty():
                return PageTitleProperty(
                    title=[RichText(type="text", text={"content": value})]
                )
            case PageRichTextProperty():
                return PageRichTextProperty(
                    rich_text=[RichText(type="text", text={"content": value})]
                )
            case PageNumberProperty():
                return PageNumberProperty(number=value)
            case PageCheckboxProperty():
                return PageCheckboxProperty(checkbox=value)
            case PageDateProperty():
                date = (
                    DateValue(**value)
                    if isinstance(value, dict)
                    else DateValue(start=value)
                )
                return PageDateProperty(date=date)
            case PageSelectProperty():
                return PageSelectProperty(select=SelectOption(name=value))
            case PageMultiSelectProperty():
                return PageMultiSelectProperty(
                    multi_select=[SelectOption(name=v) for v in value]
                )
            case PageStatusProperty():
                return PageStatusProperty(status=StatusOption(name=value))
            case PageURLProperty():
                return PageURLProperty(url=value)
            case PageEmailProperty():
                return PageEmailProperty(email=value)
            case PagePhoneNumberProperty():
                return PagePhoneNumberProperty(phone_number=value)
            case PageRelationProperty():
                ids = [value] if isinstance(value, str) else value
                return PageRelationProperty(relation=[RelationItem(id=i) for i in ids])
            case _:
                raise TypeError(f"Unsupported property type: {type(prop).__name__}")

    # ------------------------------------------------------------------ #
    # Option resolution                                                    #
    # ------------------------------------------------------------------ #

    async def _option_names_for(self, property_name: str) -> list[str]:
        await self._ensure_data_source_option_names()
        if not self._data_source_option_names:
            return []
        return self._data_source_option_names.get(property_name, [])

    def _known_option_names(self, property_name: str) -> list[str]:
        """Return cached option names without triggering a network fetch."""
        if not self._data_source_option_names:
            return []
        return self._data_source_option_names.get(property_name, [])

    async def _ensure_data_source_option_names(self) -> None:
        if self._data_source_option_names is not None:
            return

        self._data_source_option_names = {}

        if self._data_source_id is None:
            return

        from notionary.data_source.properties.properties import (
            DataSourceProperties,
        )
        from notionary.data_source.schemas import DataSourceDto

        try:
            response = await self._http.get(f"data_sources/{self._data_source_id}")
            dto = DataSourceDto.model_validate(response)
        except Exception:
            return

        descriptions = await DataSourceProperties(dto.properties).describe()
        for name, description in descriptions.items():
            if description.options:
                self._data_source_option_names[name] = description.options

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _require_property(self, name: str) -> AnyPageProperty:
        prop = self.properties.get(name)
        if prop is None:
            raise ValueError(
                f"Unknown property: {name!r}. Available: {list(self.properties)}"
            )
        return prop

    def _sync_properties(self, properties: dict[str, AnyPageProperty]) -> None:
        self.properties = properties

    @staticmethod
    def _relation_ids(prop: PageRelationProperty) -> list[str]:
        return [item.id for item in prop.relation]

    @staticmethod
    def _is_uuid_like(value: str) -> bool:
        try:
            UUID(value)
            return True
        except (ValueError, TypeError, AttributeError):
            return False

    @staticmethod
    def _validate_option(
        property_name: str, value: str, valid_names: list[str]
    ) -> None:
        if valid_names and value not in valid_names:
            raise ValueError(
                f"Property {property_name!r}: {value!r} is not a valid option. "
                f"Valid options: {valid_names}"
            )
