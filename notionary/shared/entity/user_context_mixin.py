from pydantic import BaseModel

from notionary.user.schemas import NotionUserReferenceDto


class UserContextMixin(BaseModel):
    created_by: NotionUserReferenceDto
    last_edited_by: NotionUserReferenceDto
