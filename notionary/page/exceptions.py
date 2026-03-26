import difflib
from typing import ClassVar

from notionary.exceptions.base import NotionaryException
from notionary.shared.exceptions import EntityNotFound
from notionary.shared.models.parent import ParentType


class PageNotFound(EntityNotFound):
    def __init__(self, query: str, available_titles: list[str] | None = None) -> None:
        super().__init__("page", query, available_titles)


class PagePropertyNotFoundError(NotionaryException):
    def __init__(
        self,
        property_name: str,
        available_properties: list[str] | None = None,
        max_suggestions: int = 3,
        cutoff: float = 0.6,
    ) -> None:
        self.property_name = property_name

        if available_properties:
            self.suggestions = difflib.get_close_matches(
                property_name, available_properties, n=max_suggestions, cutoff=cutoff
            )
        else:
            self.suggestions = []

        message = f"Property '{property_name}' not found."
        if self.suggestions:
            suggestions_str = "', '".join(self.suggestions)
            message += f" Did you mean '{suggestions_str}'?"
        message += " Please check the page to verify if the property exists and is correctly named."
        super().__init__(message)


class PagePropertyTypeError(NotionaryException):
    def __init__(
        self,
        property_name: str,
        actual_type: str,
    ) -> None:
        message = f"Property '{property_name}' is of type '{actual_type}'. Use the appropriate getter method for this property type."
        super().__init__(message)


class AccessPagePropertyWithoutDataSourceError(NotionaryException):
    _PARENT_DESCRIPTIONS: ClassVar[dict[ParentType, str]] = {
        ParentType.WORKSPACE: "the workspace itself",
        ParentType.PAGE_ID: "another page",
        ParentType.BLOCK_ID: "a block",
        ParentType.DATABASE_ID: "a database",
    }

    def __init__(self, parent_type: ParentType) -> None:
        parent_desc = self._PARENT_DESCRIPTIONS.get(
            parent_type, f"its parent type is '{parent_type}'"
        )
        message = (
            f"Cannot access properties other than title because this page's parent is {parent_desc}. "
            "To use operations like property reading/writing, you need to use a page whose parent is a data source."
        )
        super().__init__(message)


class InsufficientColumnsError(NotionaryException):
    def __init__(self, column_count: int) -> None:
        self.column_count = column_count
        super().__init__(
            f"Columns container must contain at least 2 column blocks, but only {column_count} found"
        )


class InvalidColumnRatioSumError(NotionaryException):
    _RATIO_TOLERANCE = 0.0001

    def __init__(self, total: float, tolerance: float = _RATIO_TOLERANCE) -> None:
        self.total = total
        self.tolerance = tolerance
        super().__init__(
            f"Width ratios must sum to 1.0 (±{tolerance}), but sum is {total}"
        )


class UnsupportedVideoFormatError(ValueError):
    def __init__(self, url: str, supported_formats: list[str]) -> None:
        self.url = url
        self.supported_formats = supported_formats
        super().__init__(self._create_user_friendly_message())

    def _create_user_friendly_message(self) -> str:
        formats = ", ".join(self.supported_formats[:5])
        remaining = len(self.supported_formats) - 5

        if remaining > 0:
            formats += f" and {remaining} more"

        return (
            f"The video URL '{self.url}' uses an unsupported format.\n"
            f"Supported formats include: {formats}.\n"
            f"YouTube embed and watch URLs are also supported."
            f"Also see https://developers.notion.com/reference/block#video for more information."
        )
