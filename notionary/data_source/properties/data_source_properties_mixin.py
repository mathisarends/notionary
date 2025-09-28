from notionary.data_source.properties.models import (
    DataSourceCheckboxProperty,
    DataSourceCreatedTimeProperty,
    DataSourceDateProperty,
    DataSourceEmailProperty,
    DataSourceMultiSelectProperty,
    DataSourceNotionProperty,
    DataSourceNumberProperty,
    DataSourcePeopleProperty,
    DataSourcePhoneNumberProperty,
    DataSourceRelationProperty,
    DataSourceRichTextProperty,
    DataSourceSelectProperty,
    DataSourceStatusProperty,
    DataSourceTitleProperty,
    DataSourceURLProperty,
)
from notionary.shared.properties.base_property_mixin import BasePropertyMixin
from notionary.shared.properties.property_type import PropertyType


class DataSourcePropertiesMixin(BasePropertyMixin[DataSourceNotionProperty]):
    @classmethod
    def _get_property_classes(cls) -> dict[PropertyType, type[DataSourceNotionProperty]]:
        return {
            PropertyType.STATUS: DataSourceStatusProperty,
            PropertyType.MULTI_SELECT: DataSourceMultiSelectProperty,
            PropertyType.SELECT: DataSourceSelectProperty,
            PropertyType.RELATION: DataSourceRelationProperty,
            PropertyType.DATE: DataSourceDateProperty,
            PropertyType.TITLE: DataSourceTitleProperty,
            PropertyType.RICH_TEXT: DataSourceRichTextProperty,
            PropertyType.URL: DataSourceURLProperty,
            PropertyType.PEOPLE: DataSourcePeopleProperty,
            PropertyType.NUMBER: DataSourceNumberProperty,
            PropertyType.CHECKBOX: DataSourceCheckboxProperty,
            PropertyType.EMAIL: DataSourceEmailProperty,
            PropertyType.PHONE_NUMBER: DataSourcePhoneNumberProperty,
            PropertyType.CREATED_TIME: DataSourceCreatedTimeProperty,
        }
