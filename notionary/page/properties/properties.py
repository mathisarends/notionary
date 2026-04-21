from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any
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
from notionary.page.properties.views import PagePropertyDescription
from notionary.rich_text import RichText, rich_text_to_markdown

if TYPE_CHECKING:
    from notionary.data_source.client import DataSourceClient


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
        self._relation_data_source_ids: dict[str, str] | None = None
        self._relation_data_source_clients: dict[str, DataSourceClient] = {}
        self._relation_title_options: dict[str, list[tuple[str, str]]] = {}
        self._property_http_client = PagePropertyHttpClient(page_id=id, http=http)

    async def set(
        self,
        name: str,
        value: str | int | float | bool | list[str] | None,
    ) -> None:
        """Set a single page property by name.

        Args:
            name: Property name as it appears in Notion.
            value: New value for the property. Type is validated against the schema.

        Raises:
            ValueError: If *name* is unknown, the value is an invalid option,
                or the property type is not supported.
            TypeError: If *value* has the wrong Python type for the property.
        """
        prop = self._require_property(name)
        normalized = await self._normalize_value(name, prop, value)
        built = self._build_property(prop, normalized)
        dto = await self._property_http_client.set_property(name, built)
        self._sync_properties(dto.properties)

    async def set_many(self, values: dict[str, Any]) -> None:
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
        await self.set(name, title)

    async def describe(self) -> dict[str, PagePropertyDescription]:
        """Return normalized property descriptions with resolved relation names."""
        await self._ensure_data_source_option_names()

        descriptions: dict[str, PagePropertyDescription] = {}
        relation_current_ids_by_name: dict[str, list[str]] = {}
        for name, prop in self.properties.items():
            descriptions[name] = self._describe_property(name, prop)
            if isinstance(prop, PageRelationProperty):
                relation_current_ids_by_name[name] = self._relation_ids(prop)

        for name, description in descriptions.items():
            if str(description.type) != "relation":
                continue

            relation_options = await self._relation_options_for(name)

            relation_current_ids = relation_current_ids_by_name.get(name, [])
            if not relation_options:
                description.current = relation_current_ids
                description.options = relation_current_ids
                continue

            id_to_title = {
                relation_id: title for title, relation_id in relation_options if title
            }

            description.relation_options = [
                title if title else relation_id
                for title, relation_id in relation_options
            ]
            description.current = [
                id_to_title.get(relation_id, relation_id)
                for relation_id in relation_current_ids
            ]
            description.options = description.relation_options

        return descriptions

    def _describe_property(
        self,
        name: str,
        prop: AnyPageProperty,
    ) -> PagePropertyDescription:
        match prop:
            case PageTitleProperty():
                return PagePropertyDescription(
                    type=prop.type,
                    current=rich_text_to_markdown(prop.title) or None,
                )

            case PageRichTextProperty():
                return PagePropertyDescription(
                    type=prop.type,
                    current=rich_text_to_markdown(prop.rich_text) or None,
                )

            case PageNumberProperty():
                return PagePropertyDescription(type=prop.type, current=prop.number)

            case PageCheckboxProperty():
                return PagePropertyDescription(type=prop.type, current=prop.checkbox)

            case PageDateProperty():
                return PagePropertyDescription(
                    type=prop.type,
                    current=prop.date.start if prop.date else None,
                )

            case PageSelectProperty():
                return PagePropertyDescription(
                    type=prop.type,
                    current=prop.select.name if prop.select else None,
                    options=self._known_option_names(name),
                )

            case PageMultiSelectProperty():
                return PagePropertyDescription(
                    type=prop.type,
                    current=[option.name for option in prop.multi_select],
                    options=self._known_option_names(name),
                )

            case PageStatusProperty():
                return PagePropertyDescription(
                    type=prop.type,
                    current=prop.status.name if prop.status else None,
                    options=self._known_option_names(name),
                )

            case PageRelationProperty():
                relation_ids = self._relation_ids(prop)
                return PagePropertyDescription(
                    type=prop.type,
                    current=relation_ids,
                    options=relation_ids,
                )

            case _:
                return PagePropertyDescription(type=prop.type)

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
                return await self._normalize_relation(name, prop, value)
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

    async def _normalize_relation(
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
        resolved_ids: list[str] = []
        for rid in relation_ids:
            if self._is_uuid_like(rid):
                resolved_ids.append(rid)
                continue

            if rid in available_ids:
                resolved_ids.append(rid)
                continue

            resolved_ids.append(await self._resolve_relation_title(name, rid))

        return resolved_ids

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
        self._relation_data_source_ids = {}

        if self._data_source_id is None:
            return

        from notionary.data_source.properties.properties import (
            DataSourceProperties,
        )
        from notionary.data_source.schemas import DataSourceDto

        try:
            response = await self._http.get(f"data_sources/{self._data_source_id}")
        except Exception:
            return

        try:
            dto = DataSourceDto.model_validate(response)
            properties = dto.properties
        except Exception:
            properties = (
                response.get("properties", {}) if isinstance(response, dict) else {}
            )
        if not isinstance(properties, dict):
            return

        descriptions = await DataSourceProperties(properties).describe()
        for name, description in descriptions.items():
            if description.options:
                self._data_source_option_names[name] = description.options
            if description.relation_options:
                relation_data_source_id = next(
                    (
                        option.id
                        for option in description.relation_options
                        if option.id and option.id.strip()
                    ),
                    None,
                )
                if relation_data_source_id is not None:
                    self._relation_data_source_ids[name] = relation_data_source_id

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

    async def _resolve_relation_title(self, property_name: str, title: str) -> str:
        options = await self._relation_options_for(property_name)
        if not options:
            raise ValueError(
                f"Property {property_name!r}: cannot resolve title {title!r} to a page id "
                "- no related data source found for this relation."
            )

        normalized = title.lower()
        matching = [
            page_id
            for option_title, page_id in options
            if option_title.lower() == normalized
        ]

        if len(matching) == 1:
            return matching[0]

        valid_titles = [option_title for option_title, _ in options]
        if len(matching) > 1:
            raise ValueError(
                f"Property {property_name!r}: relation title {title!r} is ambiguous. "
                f"Valid options: {valid_titles}"
            )

        raise ValueError(
            f"Property {property_name!r}: cannot resolve relation title {title!r}. "
            f"Valid options: {valid_titles}"
        )

    async def _relation_options_for(self, property_name: str) -> list[tuple[str, str]]:
        cached = self._relation_title_options.get(property_name)
        if cached is not None:
            return cached

        await self._ensure_data_source_option_names()

        relation_data_source_id = None
        if self._relation_data_source_ids is not None:
            relation_data_source_id = self._relation_data_source_ids.get(property_name)

        if relation_data_source_id is None:
            self._relation_title_options[property_name] = []
            return []

        try:
            client = self._relation_client_for(relation_data_source_id)
            pages = await client.query()
        except Exception:
            self._relation_title_options[property_name] = []
            return []

        options = [(page.title, str(page.id)) for page in pages if page.title]

        self._relation_title_options[property_name] = options
        return options

    def _relation_client_for(self, data_source_id: str) -> DataSourceClient:
        client = self._relation_data_source_clients.get(data_source_id)
        if client is not None:
            return client

        from notionary.data_source.client import DataSourceClient

        try:
            parsed_data_source_id = UUID(data_source_id)
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValueError(
                f"Invalid related data source id: {data_source_id!r}"
            ) from exc

        client = DataSourceClient(http=self._http, data_source_id=parsed_data_source_id)
        self._relation_data_source_clients[data_source_id] = client
        return client

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
