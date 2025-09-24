from notionary.page.properties.page_properties_mixin import PagePropertiesMixin
from notionary.shared.entities.entity_models import NotionEntityResponseDto


class NotionPageDto(NotionEntityResponseDto, PagePropertiesMixin): ...


class NotionPageUpdateDto(NotionEntityResponseDto, PagePropertiesMixin): ...
