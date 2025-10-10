from typing import Self

from notionary.data_source.query.schema import (
    ArrayOperator,
    BooleanOperator,
    DateOperator,
    FieldType,
    FilterCondition,
    NumberOperator,
    StringOperator,
)


class DataSourceFilterBuilder:
    """
    Fluent API for building Notion filter queries.

    Examples:
        builder = DataSourceFilterBuilder()
        filters = (
            builder
            .where("Status").equals("Active")
            .and_where("Priority").greater_than(5)
            .build()
        )

        pages = await data_source.get_pages(filters=filters)
    """

    def __init__(self) -> None:
        self._filters: list[FilterCondition] = []
        self._current_property: str | None = None

    def where(self, property_name: str) -> Self:
        self._current_property = property_name
        return self

    def and_where(self, property_name: str) -> Self:
        return self.where(property_name)

    def equals(self, value: str | int | float) -> Self:
        return self._add_filter(StringOperator.EQUALS, value)

    def does_not_equal(self, value: str | int | float) -> Self:
        return self._add_filter(StringOperator.DOES_NOT_EQUAL, value)

    def contains(self, value: str) -> Self:
        return self._add_filter(StringOperator.CONTAINS, value)

    def does_not_contain(self, value: str) -> Self:
        return self._add_filter(StringOperator.DOES_NOT_CONTAIN, value)

    def starts_with(self, value: str) -> Self:
        return self._add_filter(StringOperator.STARTS_WITH, value)

    def ends_with(self, value: str) -> Self:
        return self._add_filter(StringOperator.ENDS_WITH, value)

    def is_empty(self) -> Self:
        return self._add_filter(StringOperator.IS_EMPTY, None)

    def is_not_empty(self) -> Self:
        return self._add_filter(StringOperator.IS_NOT_EMPTY, None)

    def greater_than(self, value: float | int) -> Self:
        return self._add_filter(NumberOperator.GREATER_THAN, value)

    def greater_than_or_equal_to(self, value: float | int) -> Self:
        return self._add_filter(NumberOperator.GREATER_THAN_OR_EQUAL_TO, value)

    def less_than(self, value: float | int) -> Self:
        return self._add_filter(NumberOperator.LESS_THAN, value)

    def less_than_or_equal_to(self, value: float | int) -> Self:
        return self._add_filter(NumberOperator.LESS_THAN_OR_EQUAL_TO, value)

    def is_true(self) -> Self:
        return self._add_filter(BooleanOperator.IS_TRUE, None)

    def is_false(self) -> Self:
        return self._add_filter(BooleanOperator.IS_FALSE, None)

    def before(self, date: str) -> Self:
        return self._add_filter(DateOperator.BEFORE, date)

    def after(self, date: str) -> Self:
        return self._add_filter(DateOperator.AFTER, date)

    def on_or_before(self, date: str) -> Self:
        return self._add_filter(DateOperator.ON_OR_BEFORE, date)

    def on_or_after(self, date: str) -> Self:
        return self._add_filter(DateOperator.ON_OR_AFTER, date)

    def array_contains(self, value: str) -> Self:
        return self._add_filter(ArrayOperator.CONTAINS, value)

    def array_does_not_contain(self, value: str) -> Self:
        return self._add_filter(ArrayOperator.DOES_NOT_CONTAIN, value)

    def array_is_empty(self) -> Self:
        return self._add_filter(ArrayOperator.IS_EMPTY, None)

    def array_is_not_empty(self) -> Self:
        return self._add_filter(ArrayOperator.IS_NOT_EMPTY, None)

    def build(self) -> list[FilterCondition]:
        return self._filters

    def _add_filter(
        self,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
        value: str | int | float | list[str | int | float] | None,
    ) -> Self:
        if self._current_property is None:
            raise ValueError("No property selected. Use .where(property_name) first.")

        field_type = self._infer_field_type_from_operator(operator)

        filter_condition = FilterCondition(
            field=self._current_property,
            field_type=field_type,
            operator=operator,
            value=value,
        )

        self._filters.append(filter_condition)
        self._current_property = None
        return self

    def _infer_field_type_from_operator(
        self,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
    ) -> FieldType:
        if isinstance(operator, StringOperator):
            return FieldType.STRING
        elif isinstance(operator, NumberOperator):
            return FieldType.NUMBER
        elif isinstance(operator, BooleanOperator):
            return FieldType.BOOLEAN
        elif isinstance(operator, DateOperator):
            return FieldType.DATE
        elif isinstance(operator, ArrayOperator):
            return FieldType.ARRAY

        return FieldType.STRING
