from uuid import UUID

from notionary.user.mapper import to_bot, to_person
from notionary.user.schemas import (
    BotDto,
    BotResponseDto,
    PersonResponseDto,
    WorkspaceLimits,
)

PERSON_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
BOT_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _person_dto(
    name: str = "Alice",
    email: str = "alice@example.com",
    avatar_url: str | None = "https://example.com/avatar.png",
) -> PersonResponseDto:
    return PersonResponseDto(
        id=PERSON_ID, name=name, email=email, avatar_url=avatar_url
    )


def _bot_dto(
    name: str = "My Bot",
    workspace_name: str | None = "Acme Corp",
    max_upload_bytes: int = 5_000_000,
    avatar_url: str | None = None,
) -> BotResponseDto:
    limits = WorkspaceLimits(max_file_upload_size_in_bytes=max_upload_bytes)
    bot = BotDto(workspace_name=workspace_name, workspace_limits=limits)
    return BotResponseDto(id=BOT_ID, name=name, avatar_url=avatar_url, bot=bot)


class TestToPerson:
    def test_maps_all_fields(self) -> None:
        dto = _person_dto()
        person = to_person(dto)

        assert person.id == PERSON_ID
        assert person.name == "Alice"
        assert person.email == "alice@example.com"
        assert person.avatar_url == "https://example.com/avatar.png"

    def test_none_name_becomes_empty_string(self) -> None:
        dto = _person_dto(name=None)
        person = to_person(dto)

        assert person.name == ""

    def test_none_email_becomes_empty_string(self) -> None:
        dto = _person_dto(email=None)
        person = to_person(dto)

        assert person.email == ""

    def test_none_avatar_url_preserved(self) -> None:
        dto = _person_dto(avatar_url=None)
        person = to_person(dto)

        assert person.avatar_url is None


class TestToBot:
    def test_maps_all_fields(self) -> None:
        dto = _bot_dto()
        bot = to_bot(dto)

        assert bot.id == BOT_ID
        assert bot.name == "My Bot"
        assert bot.workspace_name == "Acme Corp"
        assert bot.workspace_file_upload_limit_in_bytes == 5_000_000

    def test_no_workspace_limits_yields_zero_upload_limit(self) -> None:
        bot_data = BotDto(workspace_name="Acme", workspace_limits=None)
        dto = BotResponseDto(id=BOT_ID, name="Bot", bot=bot_data)
        bot = to_bot(dto)

        assert bot.workspace_file_upload_limit_in_bytes == 0

    def test_avatar_url_forwarded(self) -> None:
        dto = _bot_dto(avatar_url="https://example.com/bot.png")
        bot = to_bot(dto)

        assert bot.avatar_url == "https://example.com/bot.png"
