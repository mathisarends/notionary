from notionary.user.models import Bot, Person
from notionary.user.schemas import BotResponseDto, PersonResponseDto


def to_person(dto: PersonResponseDto) -> Person:
    return Person(
        id=dto.id,
        name=dto.name or "",
        email=dto.email or "",
        avatar_url=dto.avatar_url,
    )


def to_bot(dto: BotResponseDto) -> Bot:
    limit = (
        dto.bot.workspace_limits.max_file_upload_size_in_bytes
        if dto.bot.workspace_limits
        else 0
    )
    return Bot(
        id=dto.id,
        name=dto.name,
        workspace_name=dto.bot.workspace_name if dto.bot else None,
        workspace_file_upload_limit_in_bytes=limit,
        avatar_url=dto.avatar_url,
    )
