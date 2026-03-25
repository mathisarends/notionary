import re
from dataclasses import dataclass
from typing import Self

from notionary.shared.entity.schemas import EntityResponseDto
from notionary.shared.models.parent import Parent, ParentType
from notionary.user.schemas import PartialUserDto

_UUID_RAW_PATTERN = re.compile(r"([a-f0-9]{32})")
_UUID_PATTERN = re.compile(
    r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
)


def is_valid_uuid(uuid: str) -> bool:
    return bool(_UUID_PATTERN.match(uuid.lower()))


def extract_uuid(source: str) -> str | None:
    if is_valid_uuid(source):
        return source
    match = _UUID_RAW_PATTERN.search(source.lower())
    if not match:
        return None
    raw = match.group(1)
    return f"{raw[0:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:32]}"


@dataclass
class EntityMetadata:
    id: str
    created_time: str
    created_by: PartialUserDto
    last_edited_time: str
    last_edited_by: PartialUserDto
    parent: Parent
    url: str
    public_url: str | None
    in_trash: bool

    @classmethod
    def from_dto(cls, dto: EntityResponseDto) -> Self:
        return cls(
            id=dto.id,
            created_time=dto.created_time,
            created_by=dto.created_by,
            last_edited_time=dto.last_edited_time,
            last_edited_by=dto.last_edited_by,
            parent=dto.parent,
            url=dto.url,
            public_url=dto.public_url,
            in_trash=dto.in_trash,
        )

    def get_parent_database_id_if_present(self) -> str | None:
        if self.parent.type == ParentType.DATABASE_ID:
            return self.parent.database_id
        return None

    def get_parent_data_source_id_if_present(self) -> str | None:
        if self.parent.type == ParentType.DATA_SOURCE_ID:
            return self.parent.data_source_id
        return None

    def get_parent_page_id_if_present(self) -> str | None:
        if self.parent.type == ParentType.PAGE_ID:
            return self.parent.page_id
        return None

    def get_parent_block_id_if_present(self) -> str | None:
        if self.parent.type == ParentType.BLOCK_ID:
            return self.parent.block_id
        return None

    def is_workspace_parent(self) -> bool:
        return self.parent.type == ParentType.WORKSPACE
