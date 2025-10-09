from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ValidationInfo, field_validator, model_validator


class FieldType(StrEnum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"


class StringOperator(StrEnum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
    IN = "in"
    NOT_IN = "not_in"


class NumberOperator(StrEnum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    BETWEEN = "between"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class BooleanOperator(StrEnum):
    IS_TRUE = "is_true"
    IS_FALSE = "is_false"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class DateOperator(StrEnum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    BEFORE = "before"
    AFTER = "after"
    BETWEEN = "between"
    IN_LAST = "in_last"  # z.B. "in last 7 days"
    IN_NEXT = "in_next"  # z.B. "in next 30 days"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class ArrayOperator(StrEnum):
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    CONTAINS_ALL = "contains_all"
    CONTAINS_ANY = "contains_any"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


class LogicalOperator(StrEnum):
    AND = "and"
    OR = "or"


class TimeUnit(StrEnum):
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"


class FilterCondition(BaseModel):
    field: str
    field_type: FieldType
    operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator
    value: Any | None = None
    time_value: int | None = None
    time_unit: TimeUnit | None = None

    @model_validator(mode="after")
    def validate_operator_and_value(self) -> Self:
        """Validiert die Konsistenz von Operator und Wert"""
        self._validate_no_value_operators()
        self._validate_relative_date_operators()
        self._validate_between_operator()
        self._validate_list_operators()
        self._validate_value_required_operators()
        return self

    def _validate_no_value_operators(self) -> None:
        no_value_ops = {
            StringOperator.IS_EMPTY,
            StringOperator.IS_NOT_EMPTY,
            NumberOperator.IS_NULL,
            NumberOperator.IS_NOT_NULL,
            BooleanOperator.IS_TRUE,
            BooleanOperator.IS_FALSE,
            BooleanOperator.IS_NULL,
            BooleanOperator.IS_NOT_NULL,
            DateOperator.IS_NULL,
            DateOperator.IS_NOT_NULL,
            ArrayOperator.IS_EMPTY,
            ArrayOperator.IS_NOT_EMPTY,
        }
        if self.operator in no_value_ops and self.value is not None:
            raise ValueError(f"Operator '{self.operator}' does not expect a value")

    def _validate_relative_date_operators(self) -> None:
        if self.operator not in {DateOperator.IN_LAST, DateOperator.IN_NEXT}:
            return

        if self.time_value is None or self.time_unit is None:
            raise ValueError(f"Operator '{self.operator}' requires time_value and time_unit")

    def _validate_between_operator(self) -> None:
        if self.operator not in {NumberOperator.BETWEEN, DateOperator.BETWEEN}:
            return

        if not isinstance(self.value, list) or len(self.value) != 2:
            raise ValueError("Operator 'between' requires a list with two values")

    def _validate_list_operators(self) -> None:
        list_ops = {
            StringOperator.IN,
            StringOperator.NOT_IN,
            NumberOperator.IN,
            NumberOperator.NOT_IN,
            ArrayOperator.CONTAINS_ALL,
            ArrayOperator.CONTAINS_ANY,
        }
        if self.operator not in list_ops:
            return

        if not isinstance(self.value, list):
            raise ValueError(f"Operator '{self.operator}' requires a list of values")

    def _validate_value_required_operators(self) -> None:
        skip_ops = {
            # No value operators
            StringOperator.IS_EMPTY,
            StringOperator.IS_NOT_EMPTY,
            NumberOperator.IS_NULL,
            NumberOperator.IS_NOT_NULL,
            BooleanOperator.IS_TRUE,
            BooleanOperator.IS_FALSE,
            BooleanOperator.IS_NULL,
            BooleanOperator.IS_NOT_NULL,
            DateOperator.IS_NULL,
            DateOperator.IS_NOT_NULL,
            ArrayOperator.IS_EMPTY,
            ArrayOperator.IS_NOT_EMPTY,
            # Relative date operators
            DateOperator.IN_LAST,
            DateOperator.IN_NEXT,
            # Between operators
            NumberOperator.BETWEEN,
            DateOperator.BETWEEN,
            # List operators
            StringOperator.IN,
            StringOperator.NOT_IN,
            NumberOperator.IN,
            NumberOperator.NOT_IN,
            ArrayOperator.CONTAINS_ALL,
            ArrayOperator.CONTAINS_ANY,
        }

        if self.operator not in skip_ops and self.value is None:
            raise ValueError(f"Operator '{self.operator}' requires a value")

    @field_validator("operator")
    @classmethod
    def validate_operator_for_field_type(
        cls, v: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator, info: ValidationInfo
    ) -> StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator:
        if "field_type" not in info.data:
            return v

        field_type: FieldType = info.data["field_type"]
        operator_value = v if isinstance(v, str) else v.value

        if not cls._is_operator_valid_for_field_type(operator_value, field_type):
            raise ValueError(f"Operator '{operator_value}' is not valid for field type '{field_type}'")

        return v

    @staticmethod
    def _is_operator_valid_for_field_type(operator: str, field_type: FieldType) -> bool:
        valid_operators: dict[FieldType, list[str]] = {
            FieldType.STRING: [op.value for op in StringOperator],
            FieldType.NUMBER: [op.value for op in NumberOperator],
            FieldType.BOOLEAN: [op.value for op in BooleanOperator],
            FieldType.DATE: [op.value for op in DateOperator],
            FieldType.DATETIME: [op.value for op in DateOperator],
            FieldType.ARRAY: [op.value for op in ArrayOperator],
        }

        return operator in valid_operators.get(field_type, [])
