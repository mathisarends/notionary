from typing import Any

from notionary.data_source.query.schema import (
    ArrayOperator,
    BooleanOperator,
    DateOperator,
    NumberOperator,
    StringOperator,
)
from notionary.exceptions.base import NotionaryError


class QueryBuilderError(NotionaryError):
    def __init__(self, message: str, property_name: str | None = None) -> None:
        self.property_name = property_name
        super().__init__(message)


class InvalidOperatorForPropertyType(QueryBuilderError):
    """Raised when an operator is used on a property type that doesn't support it."""

    def __init__(
        self,
        property_name: str,
        property_type: str,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
        valid_operators: list[StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator],
    ) -> None:
        self.property_type = property_type
        self.operator = operator
        self.valid_operators = valid_operators

        valid_operators_str = ", ".join([f"'{op.value}'" for op in valid_operators])
        message = (
            f"Cannot use operator '{operator.value}' on property '{property_name}' of type '{property_type}'. "
            f"Valid operators for this property type are: {valid_operators_str}"
        )
        super().__init__(message, property_name)


class InvalidValueForOperator(QueryBuilderError):
    """Raised when a value is incompatible with the operator being used."""

    def __init__(
        self,
        property_name: str,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
        provided_value: Any,
        expected_value_type: str,
        example_value: Any | None = None,
    ) -> None:
        self.operator = operator
        self.provided_value = provided_value
        self.expected_value_type = expected_value_type
        self.example_value = example_value

        message = (
            f"Invalid value for operator '{operator.value}' on property '{property_name}'. "
            f"Expected {expected_value_type}, but got {type(provided_value).__name__}"
        )

        if example_value is not None:
            message += f". Example: {example_value}"

        super().__init__(message, property_name)


class MissingRequiredValue(QueryBuilderError):
    """Raised when an operator requires a value but none was provided."""

    def __init__(
        self,
        property_name: str,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
    ) -> None:
        self.operator = operator

        message = f"Operator '{operator.value}' on property '{property_name}' requires a value, but none was provided"
        super().__init__(message, property_name)


class ValueNotAllowedForOperator(QueryBuilderError):
    """Raised when a value is provided for an operator that doesn't accept values."""

    def __init__(
        self,
        property_name: str,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
    ) -> None:
        self.operator = operator

        message = (
            f"Operator '{operator.value}' on property '{property_name}' does not accept a value. "
            f"Operators like 'is_empty', 'is_not_empty', 'is_true', 'is_false' don't need values"
        )
        super().__init__(message, property_name)


class InvalidDateFormat(QueryBuilderError):
    """Raised when a date string is in an invalid format."""

    def __init__(
        self,
        property_name: str,
        provided_date: str,
        expected_format: str = "ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
    ) -> None:
        self.provided_date = provided_date
        self.expected_format = expected_format

        message = (
            f"Invalid date format for property '{property_name}'. "
            f"Provided: '{provided_date}', expected format: {expected_format}"
        )
        super().__init__(message, property_name)


class InvalidNumberValue(QueryBuilderError):
    """Raised when a numeric value is invalid for the operation."""

    def __init__(
        self,
        property_name: str,
        provided_value: Any,
        reason: str,
    ) -> None:
        self.provided_value = provided_value
        self.reason = reason

        message = f"Invalid number value for property '{property_name}': {reason}. Provided value: {provided_value}"
        super().__init__(message, property_name)


class PropertyNotConfigured(QueryBuilderError):
    """Raised when attempting to filter on a property that has no configuration."""

    def __init__(
        self,
        property_name: str,
    ) -> None:
        message = (
            f"Property '{property_name}' exists but has no type configuration. "
            f"Cannot determine valid operators for this property"
        )
        super().__init__(message, property_name)


class NoPropertySelected(QueryBuilderError):
    """Raised when an operator method is called without first selecting a property."""

    def __init__(self) -> None:
        message = (
            "No property selected. Use .where('property_name') or .where_not('property_name') "
            "before calling an operator method like .equals(), .contains(), etc."
        )
        super().__init__(message)


class EmptyOrGroupError(QueryBuilderError):
    """Raised when attempting to create an OR group with no conditions."""

    def __init__(self) -> None:
        message = (
            "Cannot create an OR group with no conditions. Add at least one filter condition before using .or_where()"
        )
        super().__init__(message)


class ConflictingFiltersError(QueryBuilderError):
    """Raised when filters are logically contradictory."""

    def __init__(
        self,
        property_name: str,
        description: str,
    ) -> None:
        message = (
            f"Conflicting filters detected on property '{property_name}': {description}. "
            f"This query will never return any results"
        )
        super().__init__(message, property_name)


class InvalidSortProperty(QueryBuilderError):
    """Raised when attempting to sort by a property that doesn't exist or can't be sorted."""

    def __init__(
        self,
        property_name: str,
        reason: str,
        available_properties: list[str] | None = None,
    ) -> None:
        self.available_properties = available_properties
        self.reason = reason

        message = f"Cannot sort by property '{property_name}': {reason}"

        if available_properties:
            props_str = ", ".join([f"'{p}'" for p in sorted(available_properties)])
            message += f". Available properties: {props_str}"

        super().__init__(message, property_name)
