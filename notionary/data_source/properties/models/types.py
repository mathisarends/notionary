from typing import Any, TypeVar

from notionary.data_source.properties.models.basic_properties import DataSourceCheckboxProperty
from notionary.data_source.properties.models.contact_properties import (
    DataSourceEmailProperty,
    DataSourcePeopleProperty,
    DataSourcePhoneNumberProperty,
)
from notionary.data_source.properties.models.datetime_properties import (
    DataSourceCreatedTimeProperty,
    DataSourceDateProperty,
)
from notionary.data_source.properties.models.number_properties import DataSourceNumberProperty
from notionary.data_source.properties.models.relation_properties import DataSourceRelationProperty
from notionary.data_source.properties.models.select_properties import (
    DataSourceMultiSelectProperty,
    DataSourceSelectProperty,
)
from notionary.data_source.properties.models.status_properties import DataSourceStatusProperty
from notionary.data_source.properties.models.text_properties import (
    DataSourceRichTextProperty,
    DataSourceTitleProperty,
    DataSourceURLProperty,
)

DataSourceNotionProperty = (
    DataSourceStatusProperty
    | DataSourceMultiSelectProperty
    | DataSourceSelectProperty
    | DataSourceRelationProperty
    | DataSourceDateProperty
    | DataSourceTitleProperty
    | DataSourceRichTextProperty
    | DataSourceURLProperty
    | DataSourcePeopleProperty
    | DataSourceNumberProperty
    | DataSourceCheckboxProperty
    | DataSourceEmailProperty
    | DataSourcePhoneNumberProperty
    | DataSourceCreatedTimeProperty
    | dict[str, Any]  # Fallback
)

DataSourcePropertyT = TypeVar("DataSourcePropertyT", bound=DataSourceNotionProperty)
