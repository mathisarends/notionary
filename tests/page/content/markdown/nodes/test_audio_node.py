import pytest

from notionary.page.content.markdown.nodes import AudioMarkdownNode
from notionary.page.content.syntax import SyntaxDefinitionRegistry


@pytest.fixture
def audio_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_audio_syntax().start_delimiter


def test_audio_without_caption(audio_delimiter: str) -> None:
    audio = AudioMarkdownNode(url="https://example.com/audio.mp3")
    expected = f"{audio_delimiter}https://example.com/audio.mp3)"

    assert audio.to_markdown() == expected


def test_audio_with_caption(audio_delimiter: str, caption_delimiter: str) -> None:
    audio = AudioMarkdownNode(url="https://example.com/audio.mp3", caption="My Audio File")
    expected = f"{audio_delimiter}https://example.com/audio.mp3)\n{caption_delimiter} My Audio File"

    assert audio.to_markdown() == expected
