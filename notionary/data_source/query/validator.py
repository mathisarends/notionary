from typing import ClassVar

from notionary.data_source.properties.schemas import DataSourceProperty
from notionary.data_source.query.schema import (
    ArrayOperator,
    BooleanOperator,
    DateOperator,
    NumberOperator,
    Operator,
    SelectOperator,
    StringOperator,
)
from notionary.exceptions.data_source.builder import InvalidOperatorForPropertyType
from notionary.shared.properties.type import PropertyType


class QueryValidator:
    _PROPERTY_TYPE_OPERATORS: ClassVar[dict[PropertyType, list[type[Operator]]]] = {
        PropertyType.TITLE: [StringOperator],
        PropertyType.RICH_TEXT: [StringOperator],
        PropertyType.URL: [StringOperator],
        PropertyType.EMAIL: [StringOperator],
        PropertyType.PHONE_NUMBER: [StringOperator],
        PropertyType.SELECT: [SelectOperator],
        PropertyType.STATUS: [SelectOperator],
        PropertyType.MULTI_SELECT: [ArrayOperator],
        PropertyType.NUMBER: [NumberOperator],
        PropertyType.DATE: [DateOperator],
        PropertyType.CREATED_TIME: [DateOperator],
        PropertyType.LAST_EDITED_TIME: [DateOperator],
        PropertyType.PEOPLE: [ArrayOperator],
        PropertyType.CREATED_BY: [ArrayOperator],
        PropertyType.LAST_EDITED_BY: [ArrayOperator],
        PropertyType.RELATION: [ArrayOperator],
        PropertyType.CHECKBOX: [BooleanOperator],
    }

    def validate_operator_for_property(
        self, property_name: str, property_obj: DataSourceProperty, operator: Operator
    ) -> None:
        if not self._is_operator_valid_for_property_type(property_obj.type, operator):
            valid_operators = self._get_valid_operators_for_property_type(
                property_obj.type
            )
            raise InvalidOperatorForPropertyType(
                property_name=property_name,
                property_type=property_obj.type,
                operator=operator,
                valid_operators=valid_operators,
            )

    def _is_operator_valid_for_property_type(
        self, property_type: PropertyType, operator: Operator
    ) -> bool:
        allowed_operator_types = self._PROPERTY_TYPE_OPERATORS.get(property_type, [])
        valid_operator_values = self._get_operator_values_from_types(
            allowed_operator_types
        )
        return operator.value in valid_operator_values

    def _get_operator_values_from_types(
        self, operator_types: list[type[Operator]]
    ) -> set[str]:
        values: set[str] = set()
        for operator_type in operator_types:
            for operator in operator_type:
                values.add(operator.value)
        return values

    def _get_valid_operators_for_property_type(
        self, property_type: PropertyType
    ) -> list[Operator]:
        allowed_operator_types = self._PROPERTY_TYPE_OPERATORS.get(property_type, [])
        return self._collect_all_operators_from_types(allowed_operator_types)

    def _collect_all_operators_from_types(
        self, operator_types: list[type[Operator]]
    ) -> list[Operator]:
        operators: list[Operator] = []
        for operator_type in operator_types:
            operators.extend(self._get_all_enum_values(operator_type))
        return operators

    def _get_all_enum_values(self, operator_type: type[Operator]) -> list[Operator]:
        return list(operator_type)
