from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.data_source.properties.data_source_properties_mixin import DataSourcePropertiesMixin
from notionary.shared.models.parent_models import NotionParent
from notionary.shared.page_or_data_source.page_or_data_source_models import NotionPageOrDataSourceDto


class DataSourceDto(NotionPageOrDataSourceDto, DataSourcePropertiesMixin):
    database_parent: NotionParent
    title: list[RichTextObject]
    description: list[RichTextObject]
