from notionary.page.content.markdown.nodes import VideoMarkdownNode
from notionary.page.content.syntax.models import SyntaxDefinition
from notionary.page.content.syntax.service import SyntaxRegistry


def test_video_markdown_node(syntax_registry: SyntaxRegistry, caption_syntax: SyntaxDefinition) -> None:
    video_syntax = syntax_registry.get_video_syntax()

    video = VideoMarkdownNode(url="https://youtube.com/watch?v=123")
    expected = f"{video_syntax.start_delimiter}https://youtube.com/watch?v=123)"
    assert video.to_markdown() == expected

    video_with_caption = VideoMarkdownNode(url="https://youtube.com/watch?v=123", caption="Tutorial Video")
    expected = f"{video_syntax.start_delimiter}https://youtube.com/watch?v=123)\n{caption_syntax.start_delimiter} Tutorial Video"
    assert video_with_caption.to_markdown() == expected
