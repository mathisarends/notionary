from typing import Any
from uuid import UUID

from notionary.http import HttpClient
from notionary.page.properties.client import PagePropertyHttpClient
from notionary.page.properties.schemas import (
    AnyPageProperty,
    PageCheckboxProperty,
    PageDateProperty,
    PageMultiSelectProperty,
    PageNumberProperty,
    PageRelationProperty,
    PageRichTextProperty,
    PageSelectProperty,
    PageStatusProperty,
    PageTitleProperty,
)
from notionary.rich_text import rich_text_to_markdown


class PageProperties:
    """Scoped access to the properties of a single Notion page."""

    # Property types that an agent can write via set()
    _SETTABLE_TYPES = frozenset(
        {
            "status",
            "select",
            "multi_select",
            "number",
            "checkbox",
            "date",
            "title",
            "rich_text",
            "url",
            "email",
            "phone_number",
        }
    )

    @staticmethod
    def _validate_option(
        property_name: str, value: str, valid_names: list[str]
    ) -> None:
        if value not in valid_names:
            raise ValueError(
                f"Property {property_name!r}: {value!r} is not a valid option. "
                f"Valid options: {valid_names}"
            )

    @staticmethod
    def _relation_ids(prop: PageRelationProperty) -> list[str]:
        return [item.id for item in prop.relation]

    @staticmethod
    def _is_uuid_like(value: str) -> bool:
        try:
            UUID(value)
        except (ValueError, TypeError, AttributeError):
            return False
        return True

    def __init__(
        self,
        id: UUID,
        properties: dict[str, AnyPageProperty],
        http: HttpClient,
    ) -> None:
        self.properties = properties
        self._property_http_client = PagePropertyHttpClient(
            page_id=id, http=http, properties=properties
        )

    async def set_property(self, name: str, value: Any) -> None:
        """Set a page property by name.

        Args:
            name: Property name as it appears in Notion.
            value: New value for the property.
        """
        dto = await self._property_http_client.set_property(name, value)
        self.properties = dto.properties

    async def set_properties(self, values: dict[str, Any]) -> None:
        """Set multiple page properties in a single API request.

        Args:
            values: Mapping of property names to values.
        """
        dto = await self._property_http_client.set_properties(values)
        self.properties = dto.properties

    async def set_title(self, title: str) -> None:
        """Set the page title.

        Args:
            title: New title text.

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

    async def set(
        self,
        name: str,
        value: str | int | float | bool | list[str] | None,
    ) -> None:
        """Agent-friendly property setter. Resolves type and validates automatically.

        Args:
            name: Property name as it appears in Notion.
            value: The plain value to set. Type is validated against the property schema.

        Raises:
            ValueError: If *name* is unknown, the value is an invalid option,
                or the property type is not supported by ``set()``.
            TypeError: If *value* has the wrong Python type for the property.
        """
        prop = self.properties.get(name)
        if prop is None:
            raise ValueError(
                f"Unknown property: {name!r}. Available: {list(self.properties)}"
            )

        match prop:
            case PageStatusProperty():
                if not isinstance(value, str):
                    raise TypeError(
                        f"Property {name!r} expects a string, got {type(value).__name__}"
                    )
                self._validate_option(name, value, prop.option_names)
                await self.set_property(name, value)

            case PageSelectProperty():
                if not isinstance(value, str):
                    raise TypeError(
                        f"Property {name!r} expects a string, got {type(value).__name__}"
                    )
                self._validate_option(name, value, prop.option_names)
                await self.set_property(name, value)

            case PageMultiSelectProperty():
                names = value if isinstance(value, list) else [value]
                for v in names:
                    if not isinstance(v, str):
                        raise TypeError(
                            f"Property {name!r} expects strings, got {type(v).__name__}"
                        )
                    self._validate_option(name, v, prop.option_names)
                await self.set_property(name, names)

            case PageNumberProperty():
                if not isinstance(value, (int, float)):
                    raise TypeError(
                        f"Property {name!r} expects a number, "
                        f"got {type(value).__name__}: {value!r}"
                    )
                await self.set_property(name, value)

            case PageCheckboxProperty():
                if not isinstance(value, bool):
                    raise TypeError(
                        f"Property {name!r} expects a bool, "
                        f"got {type(value).__name__}: {value!r}"
                    )
                await self.set_property(name, value)

            case PageDateProperty():
                if not isinstance(value, str):
                    raise TypeError(
                        f"Property {name!r} expects an ISO date string, "
                        f"got {type(value).__name__}"
                    )
                await self.set_property(name, value)

            case PageTitleProperty() | PageRichTextProperty():
                if not isinstance(value, str):
                    raise TypeError(
                        f"Property {name!r} expects a string, "
                        f"got {type(value).__name__}"
                    )
                await self.set_property(name, value)

            case PageRelationProperty():
                available_ids = self._relation_ids(prop)
                if isinstance(value, str):
                    relation_ids = [value]
                elif isinstance(value, list):
                    relation_ids = value
                else:
                    raise TypeError(
                        f"Property {name!r} expects a relation page id string "
                        f"or list[str], got {type(value).__name__}. "
                        f"Available relation ids: {available_ids}"
                    )

                for relation_id in relation_ids:
                    if not isinstance(relation_id, str):
                        raise TypeError(
                            f"Property {name!r} expects relation page ids as strings, "
                            f"got {type(relation_id).__name__}. "
                            f"Available relation ids: {available_ids}"
                        )

                    if not relation_id.strip():
                        raise ValueError(
                            f"Property {name!r}: relation page id cannot be empty. "
                            f"Available relation ids: {available_ids}"
                        )

                    if (
                        not self._is_uuid_like(relation_id)
                        and relation_id not in available_ids
                    ):
                        raise ValueError(
                            f"Property {name!r}: {relation_id!r} is not a valid "
                            f"relation page id. Use a UUID-like id. "
                            f"Available relation ids: {available_ids}"
                        )

                await self.set_property(name, relation_ids)

            case _:
                if prop.type in self._SETTABLE_TYPES:
                    await self.set_property(name, value)
                else:
                    raise ValueError(
                        f"Property {name!r} has type {prop.type!r} which "
                        f"is not supported by set(). Use set_property() directly."
                    )

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
                case PageStatusProperty():
                    entry["current"] = prop.status.name if prop.status else None
                    entry["options"] = prop.option_names

                case PageSelectProperty():
                    entry["current"] = prop.select.name if prop.select else None
                    entry["options"] = prop.option_names

                case PageMultiSelectProperty():
                    entry["current"] = [o.name for o in prop.multi_select]
                    entry["options"] = prop.option_names

                case PageNumberProperty():
                    entry["current"] = prop.number

                case PageCheckboxProperty():
                    entry["current"] = prop.checkbox

                case PageDateProperty():
                    entry["current"] = prop.date.start if prop.date else None

                case PageTitleProperty():
                    entry["current"] = rich_text_to_markdown(prop.title) or None

                case PageRichTextProperty():
                    entry["current"] = rich_text_to_markdown(prop.rich_text) or None

                case PageRelationProperty():
                    relation_ids = self._relation_ids(prop)
                    entry["current"] = relation_ids
                    entry["options"] = relation_ids

                case _:
                    pass

            result[name] = entry
        return result
