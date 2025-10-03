import uuid
from datetime import datetime

from pydantic import Field

from notionary.blocks.schemas import BaseBlock
from notionary.shared.models.parent_models import Parent
from notionary.user.schemas import PartialUserDto


def default_id() -> str:
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.now()


def default_user() -> PartialUserDto:
    return PartialUserDto()


def default_parent() -> Parent:
    return Parent()


class BlockTestFactory(BaseBlock):
    id: str = Field(default_factory=default_id)
    parent: Parent = Field(default_factory=default_parent)
    created_time: datetime = Field(default_factory=now)
    last_edited_time: datetime = Field(default_factory=now)
    created_by: PartialUserDto = Field(default_factory=default_user)
    last_edited_by: PartialUserDto = Field(default_factory=default_user)
    archived: bool = False
    in_trash: bool = False
    has_children: bool = False


def create_test_block[T: BaseBlock](model: type[T], **override_data) -> T:
    base_data = BlockTestFactory().model_dump()
    block_type = model.model_fields["type"].default
    final_data = {
        **base_data,
        "type": block_type,
        **override_data,
    }
    return model(**final_data)
