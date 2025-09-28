from notionary.page.properties.page_property_models import (
    PageCheckboxProperty,
    PageCreatedTimeProperty,
    PageDateProperty,
    PageEmailProperty,
    PageMultiSelectProperty,
    PageNumberProperty,
    PagePeopleProperty,
    PagePhoneNumberProperty,
    PageProperty,
    PageRelationProperty,
    PageRichTextProperty,
    PageSelectProperty,
    PageStatusProperty,
    PageTitleProperty,
    PageURLProperty,
)
from notionary.shared.properties.base_property_mixin import BasePropertyMixin
from notionary.shared.properties.property_type import PropertyType


class PagePropertiesMixin(BasePropertyMixin[PageProperty]):
    @classmethod
    def _get_property_classes(cls) -> dict[PropertyType, type[PageProperty]]:
        return {
            PropertyType.STATUS: PageStatusProperty,
            PropertyType.RELATION: PageRelationProperty,
            PropertyType.URL: PageURLProperty,
            PropertyType.RICH_TEXT: PageRichTextProperty,
            PropertyType.MULTI_SELECT: PageMultiSelectProperty,
            PropertyType.SELECT: PageSelectProperty,
            PropertyType.PEOPLE: PagePeopleProperty,
            PropertyType.DATE: PageDateProperty,
            PropertyType.TITLE: PageTitleProperty,
            PropertyType.NUMBER: PageNumberProperty,
            PropertyType.CHECKBOX: PageCheckboxProperty,
            PropertyType.EMAIL: PageEmailProperty,
            PropertyType.PHONE_NUMBER: PagePhoneNumberProperty,
            PropertyType.CREATED_TIME: PageCreatedTimeProperty,
        }
