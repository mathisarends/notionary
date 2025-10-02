from typing import ClassVar

from notionary.infrastructure.exceptions.base import NotionaryError
from notionary.shared.models.parent_models import ParentType


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
        used_method: str | None = None,
        correct_method: str | None = None,
    ) -> None:
        incorrect_method_used = used_method != correct_method
        if used_method and correct_method and incorrect_method_used:
            message = (
                f"Property '{property_name}' cannot be accessed with the method '{used_method}'. "
                f"Because the property is of type '{actual_type}', you should use the method "
                f"'{correct_method}' instead."
            )
        else:
            message = f"Property '{property_name}' has the wrong type: '{actual_type}'."
            if correct_method:
                message += f" Try using the method '{correct_method}' to access it."

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
