from notionary.page.properties.page_properties_mixin import PagePropertiesMixin
from notionary.shared.page_or_data_source.page_or_data_source_models import NotionPageOrDataSourceDto


class NotionPageDto(NotionPageOrDataSourceDto, PagePropertiesMixin): ...


class NotionPageUpdateDto(NotionPageOrDataSourceDto, PagePropertiesMixin): ...
