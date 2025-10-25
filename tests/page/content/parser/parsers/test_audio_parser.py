from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import BlockType, CreateAudioBlock
from notionary.file_upload.service import NotionFileUpload
from notionary.page.content.parser.context import BlockParsingContext
from notionary.page.content.parser.parsers.audio import AudioParser
from notionary.page.content.syntax import SyntaxRegistry
from notionary.shared.models.file import FileType


@pytest.fixture
def audio_parser(syntax_registry: SyntaxRegistry) -> AudioParser:
    mock_file_upload = Mock(spec=NotionFileUpload)
    return AudioParser(syntax_registry=syntax_registry, file_upload_service=mock_file_upload)


@pytest.fixture
def make_audio_syntax(syntax_registry: SyntaxRegistry):
    syntax = syntax_registry.get_audio_syntax()

    def _make(url: str) -> str:
        return f"{syntax.start_delimiter}{url}{syntax.end_delimiter}"

    return _make


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/audio.mp3",
        "http://example.com/sound.wav",
        "https://example.com/music.ogg",
        "https://example.com/audio.m4a",
        "https://cdn.example.com/path/to/audio.mp3",
        "https://example.com/audio.mp3?version=1",
        "https://example.com/audio.mp3#start",
    ],
)
@pytest.mark.asyncio
async def test_valid_audio_syntax_should_create_audio_block(
    audio_parser: AudioParser,
    context: BlockParsingContext,
    make_audio_syntax,
    url: str,
) -> None:
    context.line = make_audio_syntax(url)

    await audio_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateAudioBlock)
    assert context.result_blocks[0].type == BlockType.AUDIO
    assert context.result_blocks[0].audio.external.url == url


@pytest.mark.asyncio
async def test_audio_block_should_have_external_file_type(
    audio_parser: AudioParser,
    context: BlockParsingContext,
    make_audio_syntax,
) -> None:
    context.line = make_audio_syntax("https://example.com/audio.mp3")

    await audio_parser._process(context)

    block = context.result_blocks[0]
    assert block.audio.type == FileType.EXTERNAL


@pytest.mark.asyncio
async def test_audio_block_should_have_empty_caption(
    audio_parser: AudioParser,
    context: BlockParsingContext,
    make_audio_syntax,
) -> None:
    context.line = make_audio_syntax("https://example.com/audio.mp3")

    await audio_parser._process(context)

    block = context.result_blocks[0]
    assert block.audio.caption == []


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/audio.mp3",
        "http://music.org/sound.wav",
        "https://cdn.example.com/files/audio.ogg",
    ],
)
def test_valid_audio_should_be_handled(
    audio_parser: AudioParser,
    context: BlockParsingContext,
    make_audio_syntax,
    url: str,
) -> None:
    context.line = make_audio_syntax(url)

    can_handle = audio_parser._can_handle(context)

    assert can_handle is True


@pytest.mark.parametrize(
    "invalid_line",
    [
        "audio](https://example.com/audio.mp3)",
        "[audio(https://example.com/audio.mp3)",
        "[audio]()",
        "[audio]",
        "[audio] https://example.com/audio.mp3",
        "https://example.com/audio.mp3",
        "[link](https://example.com/audio.mp3)",
        "[video](https://example.com/audio.mp3)",
        "",
        "just text",
    ],
)
def test_invalid_audio_syntax_should_not_be_handled(
    audio_parser: AudioParser,
    context: BlockParsingContext,
    invalid_line: str,
) -> None:
    context.line = invalid_line

    can_handle = audio_parser._can_handle(context)

    assert can_handle is False


def test_audio_inside_parent_context_should_not_be_handled(
    audio_parser: AudioParser,
    context: BlockParsingContext,
    make_audio_syntax,
) -> None:
    context.line = make_audio_syntax("https://example.com/audio.mp3")
    context.is_inside_parent_context = Mock(return_value=True)

    can_handle = audio_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.asyncio
async def test_process_with_invalid_url_should_not_create_block(
    audio_parser: AudioParser,
    context: BlockParsingContext,
) -> None:
    context.line = "not a valid audio line"

    await audio_parser._process(context)

    assert len(context.result_blocks) == 0


@pytest.mark.asyncio
async def test_audio_with_url_only_whitespace_should_create_block_with_empty_string(
    audio_parser: AudioParser,
    context: BlockParsingContext,
    make_audio_syntax,
) -> None:
    context.line = make_audio_syntax("   ")

    await audio_parser._process(context)

    assert len(context.result_blocks) == 0


@pytest.mark.asyncio
async def test_audio_block_should_have_correct_structure(
    audio_parser: AudioParser,
    context: BlockParsingContext,
    make_audio_syntax,
) -> None:
    context.line = make_audio_syntax("https://example.com/audio.mp3")

    await audio_parser._process(context)

    block = context.result_blocks[0]
    assert hasattr(block, "audio")
    assert hasattr(block.audio, "type")
    assert hasattr(block.audio, "external")
    assert hasattr(block.audio, "caption")
    assert hasattr(block.audio.external, "url")


@pytest.mark.asyncio
async def test_multiple_audio_patterns_should_use_first_match(
    audio_parser: AudioParser,
    context: BlockParsingContext,
    make_audio_syntax,
) -> None:
    context.line = (
        f"{make_audio_syntax('https://first.com/audio.mp3')} {make_audio_syntax('https://second.com/audio.mp3')}"
    )

    await audio_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].audio.external.url == "https://first.com/audio.mp3"
