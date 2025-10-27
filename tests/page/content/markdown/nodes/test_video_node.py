import pytest

from notionary.page.content.markdown.nodes import VideoMarkdownNode
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


@pytest.fixture
def video_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_video_syntax().start_delimiter


def test_video_without_caption(video_delimiter: str) -> None:
    video = VideoMarkdownNode(url="https://youtube.com/watch?v=123")
    expected = f"{video_delimiter}https://youtube.com/watch?v=123)"

    assert video.to_markdown() == expected


def test_video_with_caption(video_delimiter: str, caption_delimiter: str) -> None:
    video = VideoMarkdownNode(
        url="https://youtube.com/watch?v=123", caption="Tutorial Video"
    )
    expected = f"{video_delimiter}https://youtube.com/watch?v=123)\n{caption_delimiter} Tutorial Video"

    assert video.to_markdown() == expected
