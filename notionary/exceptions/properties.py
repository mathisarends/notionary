from typing import ClassVar

from notionary.exceptions.base import NotionaryError
from notionary.shared.models.parent import ParentType


class PagePropertyNotFoundError(NotionaryError):
    def __init__(self, page_url: str, property_name: str, suggestions: list[str] | None = None) -> None:
        message = f"Property '{property_name}' not found."
        if suggestions:
            suggestions_str = "', '".join(suggestions)
            message += f" Did you mean '{suggestions_str}'?"
        message += f" Please check the page at {page_url} to verify if the property exists and is correctly named."
        super().__init__(message)


class PagePropertyTypeError(NotionaryError):
    def __init__(
        self,
        property_name: str,
        actual_type: str,
    ) -> None:
        message = f"Property '{property_name}' is of type '{actual_type}'. Use the appropriate getter method for this property type."
        super().__init__(message)


class AccessPagePropertyWithoutDataSourceError(NotionaryError):
    _PARENT_DESCRIPTIONS: ClassVar[dict[ParentType, str]] = {
        ParentType.WORKSPACE: "the workspace itself",
        ParentType.PAGE_ID: "another page",
        ParentType.BLOCK_ID: "a block",
        ParentType.DATABASE_ID: "a database",
    }

    def __init__(self, parent_type: ParentType) -> None:
        parent_desc = self._PARENT_DESCRIPTIONS.get(parent_type, f"its parent type is '{parent_type}'")
        message = (
            f"Cannot access properties other than title because this page's parent is {parent_desc}. "
            "To use operations like property reading/writing, you need to use a page whose parent is a data source."
        )
        super().__init__(message)
