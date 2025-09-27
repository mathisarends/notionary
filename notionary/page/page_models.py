from notionary.page.properties.page_properties_mixin import PagePropertiesMixin
from notionary.shared.entity.entity_models import EntityDto
from notionary.shared.entity.user_context_mixin import UserContextMixin


class NotionPageDto(EntityDto, UserContextMixin, PagePropertiesMixin):
    archived: bool
