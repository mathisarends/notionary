from notionary.blocks.markdown.nodes import AudioMarkdownNode


def test_audio_markdown_node() -> None:
    audio = AudioMarkdownNode(url="https://example.com/audio.mp3")
    expected = "[audio](https://example.com/audio.mp3)"
    assert audio.to_markdown() == expected

    audio_with_caption = AudioMarkdownNode(url="https://example.com/audio.mp3", caption="My Audio File")
    expected = "[audio](https://example.com/audio.mp3)(caption:My Audio File)"
    assert audio_with_caption.to_markdown() == expected
