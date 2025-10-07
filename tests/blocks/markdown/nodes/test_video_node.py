from notionary.blocks.markdown.nodes import VideoMarkdownNode


def test_video_markdown_node() -> None:
    """Test VideoMarkdownNode"""
    video = VideoMarkdownNode(url="https://youtube.com/watch?v=123")
    expected = "[video](https://youtube.com/watch?v=123)"
    assert video.to_markdown() == expected

    video_with_caption = VideoMarkdownNode(url="https://youtube.com/watch?v=123", caption="Tutorial Video")
    expected = "[video](https://youtube.com/watch?v=123)(caption:Tutorial Video)"
    assert video_with_caption.to_markdown() == expected
