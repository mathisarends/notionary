from __future__ import annotations

from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ValidationInfo, field_validator, model_serializer, model_validator

from notionary.shared.properties.property_type import PropertyType


class FieldType(StrEnum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"
    RELATION = "relation"
    PEOPLE = "people"

class StringOperator(StrEnum):
    EQUALS = "equals"
    DOES_NOT_EQUAL = "does_not_equal"
    CONTAINS = "contains"
    DOES_NOT_CONTAIN = "does_not_contain"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


class NumberOperator(StrEnum):
    EQUALS = "equals"
    DOES_NOT_EQUAL = "does_not_equal"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL_TO = "greater_than_or_equal_to"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL_TO = "less_than_or_equal_to"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


class BooleanOperator(StrEnum):
    IS_TRUE = "is_true"
    IS_FALSE = "is_false"


class StatusOperator(StrEnum):
    EQUALS = "equals"
    DOES_NOT_EQUAL = "does_not_equal"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


class DateOperator(StrEnum):
    EQUALS = "equals"
    BEFORE = "before"
    AFTER = "after"
    ON_OR_BEFORE = "on_or_before"
    ON_OR_AFTER = "on_or_after"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


class ArrayOperator(StrEnum):
    CONTAINS = "contains"
    DOES_NOT_CONTAIN = "does_not_contain"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"

class RelationOperator(StrEnum):
    CONTAINS = "contains"
    DOES_NOT_CONTAIN = "does_not_contain"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"

class PeopleOperator(StrEnum):
    CONTAINS = "contains"
    DOES_NOT_CONTAIN = "does_not_contain"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"

class LogicalOperator(StrEnum):
    AND = "and"
    OR = "or"


class SortDirection(StrEnum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


class TimestampType(StrEnum):
    CREATED_TIME = "created_time"
    LAST_EDITED_TIME = "last_edited_time"


class TimeUnit(StrEnum):
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"


type Operator = StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator
type FilterValue = str | int | float | bool | list[str | int | float]


# Hier vllt. auch die übergebenen Werte direkt validieren dann muss man das nicht im resolver machen
class FilterCondition(BaseModel):
    field: str
    field_type: FieldType
    operator: Operator
    value: FilterValue | None = None
    time_value: int | None = None
    time_unit: TimeUnit | None = None

    @model_validator(mode="after")
    def validate_operator_and_value(self) -> Self:
        self._validate_no_value_operators()
        self._validate_value_required_operators()
        return self

    def _validate_no_value_operators(self) -> None:
        no_value_ops = {
            StringOperator.IS_EMPTY,
            StringOperator.IS_NOT_EMPTY,
            NumberOperator.IS_EMPTY,
            NumberOperator.IS_NOT_EMPTY,
            BooleanOperator.IS_TRUE,
            BooleanOperator.IS_FALSE,
            DateOperator.IS_EMPTY,
            DateOperator.IS_NOT_EMPTY,
            ArrayOperator.IS_EMPTY,
            ArrayOperator.IS_NOT_EMPTY,
        }
        if self.operator in no_value_ops and self.value is not None:
            raise ValueError(f"Operator '{self.operator}' does not expect a value")

    def _validate_value_required_operators(self) -> None:
        skip_ops = {
            StringOperator.IS_EMPTY,
            StringOperator.IS_NOT_EMPTY,
            NumberOperator.IS_EMPTY,
            NumberOperator.IS_NOT_EMPTY,
            BooleanOperator.IS_TRUE,
            BooleanOperator.IS_FALSE,
            DateOperator.IS_EMPTY,
            DateOperator.IS_NOT_EMPTY,
            ArrayOperator.IS_EMPTY,
            ArrayOperator.IS_NOT_EMPTY,
        }

        if self.operator not in skip_ops and self.value is None:
            raise ValueError(f"Operator '{self.operator}' requires a value")

    @field_validator("operator")
    @classmethod
    def validate_operator_for_field_type(
        cls,
        value: Operator,
        info: ValidationInfo,
    ) -> Operator:
        if "field_type" not in info.data:
            return value

        field_type: FieldType = info.data["field_type"]
        operator_value = value if isinstance(value, str) else value.value

        if not cls._is_operator_valid_for_field_type(operator_value, field_type):
            raise ValueError(f"Operator '{operator_value}' is not valid for field type '{field_type}'")

        return value

    @staticmethod
    def _is_operator_valid_for_field_type(operator: str, field_type: FieldType) -> bool:
        valid_operators: dict[FieldType, list[str]] = {
            FieldType.STRING: [op.value for op in StringOperator],
            FieldType.NUMBER: [op.value for op in NumberOperator],
            FieldType.BOOLEAN: [op.value for op in BooleanOperator],
            FieldType.DATE: [op.value for op in DateOperator],
            FieldType.DATETIME: [op.value for op in DateOperator],
            FieldType.ARRAY: [op.value for op in ArrayOperator],
            FieldType.RELATION: [op.value for op in RelationOperator],
            FieldType.PEOPLE: [op.value for op in PeopleOperator],
        }

        return operator in valid_operators.get(field_type, [])


class OrGroupMarker(BaseModel):
    conditions: list[FilterCondition]


type InternalFilterCondition = FilterCondition | OrGroupMarker


class PropertyFilter(BaseModel):
    property: str
    property_type: PropertyType
    operator: Operator
    value: FilterValue | None = None

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        property_type_str = self.property_type.value
        operator_str = self.operator.value
        filter_value = self.value

        if isinstance(self.operator, BooleanOperator):
            operator_str = "equals"
            filter_value = self.operator == BooleanOperator.IS_TRUE

        return {
            "property": self.property,
            property_type_str: {operator_str: filter_value if filter_value is not None else True},
        }


class CompoundFilter(BaseModel):
    operator: LogicalOperator
    filters: list[PropertyFilter | CompoundFilter]

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        operator_str = self.operator.value
        return {operator_str: [f.model_dump() for f in self.filters]}


type NotionFilter = PropertyFilter | CompoundFilter


class PropertySort(BaseModel):
    property: str
    direction: SortDirection


class TimestampSort(BaseModel):
    timestamp: TimestampType
    direction: SortDirection


type NotionSort = PropertySort | TimestampSort


class DataSourceQueryParams(BaseModel):
    filter: NotionFilter | None = None
    sorts: list[NotionSort] | None = None

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        result: dict[str, Any] = {}

        if self.filter is not None:
            result["filter"] = self.filter.model_dump()

        if self.sorts is not None and len(self.sorts) > 0:
            result["sorts"] = [sort.model_dump() for sort in self.sorts]

        return result
