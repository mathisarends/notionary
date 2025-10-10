from notionary.exceptions.base import NotionaryError


class DataSourcePropertyNotFound(NotionaryError):
    def __init__(self, property_name: str, suggestions: list[str] | None = None) -> None:
        self.property_name = property_name
        self.suggestions = suggestions or []

        message = f"Property '{self.property_name}' not found."
        if self.suggestions:
            suggestions_str = "', '".join(self.suggestions)
            message += f" Did you mean '{suggestions_str}'?"
        super().__init__(message)


class DataSourcePropertyTypeError(NotionaryError):
    def __init__(self, property_name: str, expected_type: str, actual_type: str) -> None:
        message = f"Property '{property_name}' has the wrong type. Expected: '{expected_type}', found: '{actual_type}'."
        super().__init__(message)
