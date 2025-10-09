from notionary.page.content.markdown.nodes import AudioMarkdownNode
from notionary.page.content.syntax.models import SyntaxDefinition
from notionary.page.content.syntax.service import SyntaxRegistry


def test_audio_markdown_node(syntax_registry: SyntaxRegistry, caption_syntax: SyntaxDefinition) -> None:
    audio_syntax = syntax_registry.get_audio_syntax()

    audio = AudioMarkdownNode(url="https://example.com/audio.mp3")
    expected = f"{audio_syntax.start_delimiter}https://example.com/audio.mp3)"
    assert audio.to_markdown() == expected

    audio_with_caption = AudioMarkdownNode(url="https://example.com/audio.mp3", caption="My Audio File")
    expected = (
        f"{audio_syntax.start_delimiter}https://example.com/audio.mp3)\n{caption_syntax.start_delimiter} My Audio File"
    )
    assert audio_with_caption.to_markdown() == expected
