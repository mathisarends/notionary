from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.data_source.properties.data_source_properties_mixin import DataSourcePropertiesMixin
from notionary.shared.entities.entity_models import NotionEntityResponseDto
from notionary.shared.models.parent_models import NotionParent


class DataSourceDto(NotionEntityResponseDto, DataSourcePropertiesMixin):
    database_parent: NotionParent
    title: list[RichTextObject]
    description: list[RichTextObject]
